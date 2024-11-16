from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import TeamSerializer  # , calculate_fee
from stocks.models import Stock, StockHolding, Team, Transaction, Watchlist


class TestTeamViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team", balance=1000)
        self.user.profile.team = self.team
        self.user.profile.save()

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="S1", current_price=Decimal("50.00")
        )
        self.stock2 = Stock.objects.create(
            name="Stock 2", ticker="S2", current_price=Decimal("100.00")
        )
        StockHolding.objects.create(team=self.team, stock=self.stock1, amount=2)
        StockHolding.objects.create(team=self.team, stock=self.stock2, amount=5)

        self.url = reverse("team-detail")

    def test_retrieve_team_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = TeamSerializer(instance=self.team)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_team_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)  # Entferne die Autorisierung
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestWatchlistViewSet(APITestCase):
    # Testen Sie den Zugriff auf die Watchlist.
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="S1", current_price=Decimal("50.00")
        )
        self.stock2 = Stock.objects.create(
            name="Stock 1", ticker="S1", current_price=Decimal("50.00")
        )
        self.watchlist = Watchlist.objects.create(
            stock=self.stock2, team=self.user.profile.team
        )

        self.url = reverse("watchlist-list")
        self.create_url = reverse("watchlist-create")

    def test_retrieve_watchlist_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_watchlist_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)  # Entferne die Autorisierung
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_watchlist_item_success(self):
        data = {"stock": self.stock1.pk}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_watchlist_item_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)  # Entferne die Autorisierung
        data = {"stock": self.stock1.pk}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_watchlist_item_invalid_data(self):
        data = {"stock": "invalid_stock_id"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_watchlist_item_success(self):
        response = self.client.delete(
            reverse("watchlist-delete", args=[self.watchlist.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_watchlist_item_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION=None)  # Entferne die Autorisierung
        response = self.client.delete(
            reverse("watchlist-delete", args=[self.watchlist.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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
