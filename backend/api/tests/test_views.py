from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from stocks.models import (
    History,
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
    Watchlist,
)

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
            "Ein Benutzer mit der E-Mail-Adresse test@example.com existiert bereits.",
            response.data["non_field_errors"],
        )

    def test_create_registration_request_already_requested(self):
        RegistrationRequest.objects.create(email="test@example.com")
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Eine Registrierungsanfrage für test@example.com existiert bereits.",
            response.data["non_field_errors"],
        )

    def test_create_registration_request_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StockDetailViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team")
        self.user.profile.team = self.team
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="STK1", current_price=100.00
        )
        self.stock2 = Stock.objects.create(
            name="Stock 2", ticker="STK2", current_price=0
        )
        self.history1 = History.objects.create(
            stock=self.stock1, name="Day", period="1d", interval="5m", values=[1, 2, 3]
        )
        self.stock_holding = StockHolding.objects.create(
            team=self.team, stock=self.stock1, amount=5
        )

    def test_retrieve_stock_success(self):
        url = reverse("stock-detail", kwargs={"pk": self.stock1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Stock 1")
        self.assertEqual(response.data["ticker"], "STK1")
        self.assertEqual(response.data["current_price"], "100.00")
        self.assertEqual(response.data["history_entries"][0]["name"], "Tag")
        self.assertEqual(response.data["history_entries"][0]["values"], [1, 2, 3])
        self.assertEqual(response.data["amount"], 5)

    def test_retrieve_stock_with_no_holding(self):
        stock3 = Stock.objects.create(
            name="Stock 3", ticker="STK3", current_price=50.00
        )
        url = reverse("stock-detail", kwargs={"pk": stock3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["amount"], 0)

    def test_retrieve_stock_with_watchlist_entry(self):
        watchlist_entry = Watchlist.objects.create(team=self.team, stock=self.stock1)
        url = reverse("stock-detail", kwargs={"pk": self.stock1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["watchlist_id"], watchlist_entry.pk)

    def test_retrieve_stock_with_no_watchlist_entry(self):
        stock3 = Stock.objects.create(
            name="Stock 3", ticker="STK3", current_price=50.00
        )
        url = reverse("stock-detail", kwargs={"pk": stock3.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["watchlist_id"])

    def test_retrieve_stock_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("stock-detail", kwargs={"pk": self.stock1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stock_filtering(self):
        url = reverse("stock-detail", kwargs={"pk": self.stock2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TeamDetailViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.user.profile.team = self.team
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.stock_holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=10
        )
        Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=5,
            price=100,
        )

    def test_retrieve_team_detail_success(self):
        url = reverse("team-detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Team")
        self.assertEqual(response.data["balance"], "100000.00")
        self.assertEqual(response.data["trades"], 1)
        self.assertIsNotNone(response.data["code"])
        self.assertEqual(len(response.data["members"]), 1)
        self.assertIsNotNone(response.data["portfolio_value"])
        self.assertIsNotNone(response.data["rank"])

    def test_retrieve_team_detail_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("team-detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TeamRankingListViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )

        self.team1 = Team.objects.create(name="Team 1", balance=100000)
        self.team2 = Team.objects.create(name="Team 2", balance=150000)
        self.team3 = Team.objects.create(name="Team 3", balance=100000)
        self.team4 = Team.objects.create(name="Admin", balance=100000)

        self.user1.profile.team = self.team1
        self.user1.profile.save()

        self.user2.profile.team = self.team2
        self.user2.profile.save()

        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.stock_holding = StockHolding.objects.create(
            team=self.team1, stock=self.stock, amount=10
        )

    def test_retrieve_team_ranking_list_success(self):
        url = reverse("ranking")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(response.data["num_pages"], 1)
        self.assertEqual(response.data["current_page"], 1)
        self.assertEqual(response.data["page_size"], 10)
        self.assertEqual(response.data["results"][0]["name"], "Team 2")
        self.assertEqual(response.data["results"][0]["rank"], 1)
        self.assertEqual(response.data["results"][1]["name"], "Team 1")
        self.assertEqual(response.data["results"][1]["rank"], 2)

    def test_retrieve_team_ranking_list_pagination(self):
        for i in range(12):
            team = Team.objects.create(name=f"Team {i + 3}", balance=100000 + i * 1000)
            user = User.objects.create_user(
                username=f"testuser{i + 3}", password="testpassword"
            )
            user.profile.team = team
            user.profile.save()

        url = reverse("ranking")
        response = self.client.get(f"{url}?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 7)
        self.assertEqual(response.data["count"], 17)
        self.assertEqual(response.data["num_pages"], 2)
        self.assertEqual(response.data["current_page"], 2)
        self.assertEqual(response.data["page_size"], 10)
        self.assertEqual(response.data["results"][0]["name"], "Team 5")
        self.assertEqual(response.data["results"][0]["rank"], 11)
        self.assertEqual(response.data["results"][3]["name"], "default")
        self.assertEqual(response.data["results"][3]["rank"], 14)


class WatchlistViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team")
        self.user.profile.team = self.team
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="STK1", current_price=100.00
        )
        self.stock2 = Stock.objects.create(
            name="Stock 2", ticker="STK2", current_price=50.00
        )

        self.watchlist2 = Watchlist.objects.create(
            team=self.team, stock=self.stock2, note="Test Note 2"
        )

        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.other_team = Team.objects.create(name="Other Team")
        self.other_user.profile.team = self.other_team
        self.other_user.profile.save()
        self.other_watchlist = Watchlist.objects.create(
            team=self.other_team, stock=self.stock1, note="Other user note"
        )

    def test_watchlist_list_success(self):
        url = reverse("watchlist-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["stock"]["name"], "Stock 2")
        self.assertEqual(response.data[0]["note"], "Test Note 2")

    def test_watchlist_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("watchlist-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_create_success(self):
        url = reverse("watchlist-create")
        data = {"stock": self.stock1.pk, "note": "New Watchlist Item"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stock"], self.stock1.pk)
        self.assertEqual(response.data["note"], "New Watchlist Item")
        self.assertTrue(
            Watchlist.objects.filter(
                team=self.team, stock=self.stock1, note="New Watchlist Item"
            ).exists()
        )

    def test_watchlist_create_duplicate(self):
        url = reverse("watchlist-create")
        data = {"stock": self.stock1.pk, "note": "Duplicate Watchlist"}
        self.client.post(
            url, data, format="json"
        )  # Make sure that this entry already exists
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Stock is already in the watchlist.", response.data["non_field_errors"]
        )

    def test_watchlist_create_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("watchlist-create")
        data = {"stock": self.stock1.pk, "note": "New Watchlist Item"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_update_success(self):
        url = reverse("watchlist-update", kwargs={"pk": self.watchlist2.pk})
        data = {"note": "Updated Note"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["note"], "Updated Note")
        self.watchlist2.refresh_from_db()
        self.assertEqual(self.watchlist2.note, "Updated Note")

    def test_watchlist_update_other_user(self):
        url = reverse("watchlist-update", kwargs={"pk": self.other_watchlist.pk})
        data = {"note": "Updated Note"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_watchlist.refresh_from_db()
        self.assertEqual(self.other_watchlist.note, "Other user note")

    def test_watchlist_update_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("watchlist-update", kwargs={"pk": self.watchlist2.pk})
        data = {"note": "Updated Note"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_delete_other_user(self):
        url = reverse("watchlist-delete", kwargs={"pk": self.other_watchlist.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Watchlist.objects.filter(pk=self.other_watchlist.pk).exists())

    def test_watchlist_delete_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("watchlist-delete", kwargs={"pk": self.watchlist2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_delete_success(self):
        url = reverse("watchlist-delete", kwargs={"pk": self.watchlist2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Watchlist.objects.filter(pk=self.watchlist2.pk).exists())


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
