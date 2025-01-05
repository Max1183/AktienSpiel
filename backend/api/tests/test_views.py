from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from stocks.models import (
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
    Watchlist,
)

from ..serializers import TeamSerializer

User = get_user_model()


class MyTokenObtainPairViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", is_staff=True
        )
        self.url = reverse("get_token")

    def test_token_obtain_with_valid_credentials(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        decoded_token = AccessToken(response.data["access"])
        self.assertTrue(decoded_token["is_staff"])

    def test_token_obtain_with_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)


class RegistrationRequestViewTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword", email="admin@test.com"
        )
        self.url = reverse("register")
        self.client.force_authenticate(
            user=self.admin_user
        )  # Authenticate the admin user

    def test_create_registration_request_success(self):
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RegistrationRequest.objects.filter(email="test@example.com").exists()
        )
        self.assertEqual(response.data["email"], "test@example.com")

    def test_create_registration_request_user_exists(self):
        # Create the user with the given email
        User.objects.create_user(
            username="existuser", password="password", email="test@example.com"
        )
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Ein Benutzer mit dieser E-Mail-Adresse test@example.com existiert bereits.",
            response.data[0],
        )

    def test_create_registration_request_already_requested(self):
        RegistrationRequest.objects.create(email="test@example.com")
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Eine Registrierungsanfrage für test@example.com existiert bereits.",
            response.data[0],
        )

    def test_create_registration_request_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCreateUserView(APITestCase):
    def setUp(self):
        self.url = reverse("create-user")
        self.team = Team.objects.create(name="Team 1")
        self.team_code = self.team.code
        self.email = "test@example.com"

        self.registration_request = RegistrationRequest.objects.create(email=self.email)
        self.token = self.registration_request.activation_token

        self.data = {
            "token": self.token,
            "email": self.email,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "password": "testpassword1",
            "team_code": self.team_code,
            "team_name": "Test Team",
            "join_team": True,
        }

    def test_create_user_invalid_token(self):
        data = self.data.copy()
        data["token"] = "invalid_token"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_email(self):
        data = self.data.copy()
        data["email"] = "invalid_email"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_password(self):
        data = self.data.copy()
        data["password"] = "short"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_team_code(self):
        data = self.data.copy()
        data["team_code"] = "invalid_code"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_team_name(self):
        data = self.data.copy()
        data["team_name"] = ""
        data["join_team"] = False
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_valid(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username="johndoe")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.profile.team.name, "Team 1")
        self.assertEqual(user.profile.team.code, self.team_code)
        self.assertTrue(user.profile.team.members.filter(user=user).exists())


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
