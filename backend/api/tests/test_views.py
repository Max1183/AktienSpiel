from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

# from api.serializers import calculate_fee
from stocks.models import Stock, StockHolding, Team, Transaction


class TestCreateUserView(TestCase):
    # Testen Sie die Erstellung eines neuen Benutzers.
    def test_create_user_success(self):
        url = reverse("create-user")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.count(), 1
        )  # Überprüfen Sie, ob ein Benutzer erstellt wurde


class TestStockViewSet(APITestCase):
    # Testen Sie den Zugriff auf die Aktien Details.
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=Decimal("100.00")
        )
        self.url = reverse("stock-detail", kwargs={"pk": self.stock.pk})

    def test_retrieve_stock_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Test Stock")


class TestStockHoldingViewSet(APITestCase):
    # Testen Sie den Zugriff auf die Stock Holdings eines Teams.
    def setUp(self):
        self.team = Team.objects.create(name="Test Team")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.user.profile.team = self.team
        self.user.profile.save()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=Decimal("100.00")
        )
        self.stock_holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=10
        )
        self.url = reverse("stockholding-detail", kwargs={"pk": self.stock_holding.pk})

    def test_retrieve_stock_holding_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["amount"], 10)


class TestTransactionViewSet(APITestCase):
    # Testen Sie das Erstellen neuer Transaktionen.
    def setUp(self):
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.user.profile.team = self.team
        self.user.profile.save()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=Decimal("100.00")
        )
        self.url = reverse("transaction-list")

    def test_create_transaction_buy_success(self):
        data = {"stock": self.stock.pk, "transaction_type": "buy", "amount": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        # fee = calculate_fee(self.stock.current_price, 5)
        # self.assertEqual(self.team.balance, int(100000 - (5 * self.stock.current_price + fee)))

    def test_create_transaction_sell_success(self):
        self.team.balance = 100000
        StockHolding.objects.create(team=self.team, stock=self.stock, amount=10)
        data = {"stock": self.stock.pk, "transaction_type": "sell", "amount": 3}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(
            StockHolding.objects.get(team=self.team, stock=self.stock).amount, 7
        )
        # fee = calculate_fee(self.stock.current_price, 3)
        # self.assertEqual(self.team.balance, int(100000 + (3 * self.stock.current_price - fee)))

    def test_create_transaction_invalid_amount(self):
        data = {"stock": self.stock.pk, "transaction_type": "buy", "amount": 0}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ungültige Anzahl.", response.json()["detail"][0])

    def test_create_transaction_invalid_type(self):
        data = {"stock": self.stock.pk, "transaction_type": "invalid", "amount": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if "detail" in response.json():
            self.assertIn("Ungültiger Transaktionstyp.", response.json()["detail"][0])

    def test_create_transaction_insufficient_funds(self):
        data = {
            "stock": self.stock.pk,
            "transaction_type": "buy",
            "amount": 10000,
        }  # Viel zu teuer
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Nicht genügend Guthaben.", response.json()["detail"][0])

    def test_create_transaction_insufficient_stocks(self):
        StockHolding.objects.create(team=self.team, stock=self.stock, amount=10)
        data = {
            "stock": self.stock.pk,
            "transaction_type": "sell",
            "amount": 10000,
        }  # Viel zu viel
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Nicht genügend Aktien im Depot.", response.json()["detail"][0])

    def test_create_transaction_invalid_stock(self):
        data = {"stock": 100000, "transaction_type": "buy", "amount": 5}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        if "detail" in response.json():
            self.assertIn(
                "Sie besitzen keine Aktien dieses Typs.", response.json()["detail"][0]
            )
