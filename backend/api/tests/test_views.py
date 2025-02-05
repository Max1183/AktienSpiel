import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

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
        self.url = reverse("get-token")

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


class TeamUpdateViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )
        self.team = Team.objects.create(name="Test Team")
        self.profile = self.user.profile
        self.team.team_admin = self.profile
        self.team.save()
        self.profile.team = self.team
        self.profile.save()

        self.url = reverse("team-update")
        self.client.force_authenticate(user=self.user)

        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.other_profile = self.other_user.profile
        self.other_profile.team = self.team
        self.other_profile.save()

    def test_update_team_success(self):
        self.team.last_edited = timezone.now() - timedelta(days=1)
        data = {"name": "Updated Team Name"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Team Name")
        self.team.refresh_from_db()
        self.assertEqual(self.team.name, "Updated Team Name")

    def test_update_team_admin_success(self):
        self.team.last_edited = timezone.now() - timedelta(days=1)
        data = {"admin": self.other_profile.pk}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.team_admin, self.other_profile)

    def test_update_team_name_exists(self):
        self.team.last_edited = timezone.now() - timedelta(days=1)
        Team.objects.create(name="Existing Team")
        data = {"name": "Existing Team"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("Teamname ist bereits vergeben.", response.data["name"])

    def test_update_team_name_invalid_length(self):
        data = {"name": "te"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["name"]
        )

        data = {"name": "test" * 10}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.", response.data["name"]
        )

    def test_update_team_admin_not_member(self):
        non_member_user = User.objects.create_user(
            username="nonmember", password="password", email="nonmember@example.com"
        )
        non_member_profile = non_member_user.profile

        data = {"admin": non_member_profile.pk}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("admin", response.data)
        self.assertIn("Der Admin muss Mitglied des Teams sein.", response.data["admin"])

    def test_update_team_admin_invalid_user_profile(self):
        data = {"admin": 999}  # Non-existent UserProfile pk
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("admin", response.data)
        self.assertIn(
            'Invalid pk "999" - object does not exist.', response.data["admin"]
        )

    def test_update_team_not_admin(self):
        self.client.force_authenticate(
            user=self.other_user
        )  # Authenticate with a non-admin user
        data = {"name": "Attempted Update"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn(
            "Nur der Team Admin kann Änderungen vornehmen.",
            response.data["non_field_errors"],
        )

    def test_update_team_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"name": "Attempted Update"}
        response = self.client.patch(self.url, data, format="json")
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
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["count"], 2)
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
        self.assertEqual(len(response.data["results"]), 4)
        self.assertEqual(response.data["count"], 14)
        self.assertEqual(response.data["num_pages"], 2)
        self.assertEqual(response.data["current_page"], 2)
        self.assertEqual(response.data["page_size"], 10)
        self.assertEqual(response.data["results"][0]["name"], "Team 5")
        self.assertEqual(response.data["results"][0]["rank"], 11)
        self.assertEqual(response.data["results"][3]["name"], "Team 3")
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


class CreateUserViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("create-user")
        self.registration_request = RegistrationRequest.objects.create(
            email="test@example.com"
        )
        self.valid_data = {
            "token": str(self.registration_request.activation_token),
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "password": "Testpassword123",
            "join_team": False,
            "team_name": "Test Team",
        }

    def test_create_user_success_new_team(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertTrue(Team.objects.filter(name="Test Team").exists())
        self.assertEqual(response.data["email"], "test@example.com")

    def test_create_user_success_join_team(self):
        Team.objects.create(name="Existing Team", code="testcode")
        data = self.valid_data.copy()
        data["join_team"] = True
        data["team_code"] = "testcode"
        del data["team_name"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertTrue(Team.objects.filter(code="testcode").exists())
        self.assertEqual(response.data["email"], "test@example.com")

    def test_create_user_invalid_token(self):
        data = self.valid_data.copy()
        data["token"] = str(uuid.uuid4())
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token", response.data)
        self.assertIn("Dieses Token ist ungültig.", response.data["token"])

    def test_create_user_mismatched_email_token(self):
        data = self.valid_data.copy()
        data["email"] = "wrong@test.com"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn(
            "Diese E-Mail-Adresse wurde nicht mit diesem Token registriert.",
            response.data["non_field_errors"],
        )

    def test_create_user_email_exists(self):
        User.objects.create_user(
            username="test1", password="password", email="test@example.com"
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("This field must be unique.", response.data["email"])

    def test_create_user_username_exists(self):
        User.objects.create_user(
            username="testuser", password="password", email="test2@example.com"
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("This field must be unique.", response.data["username"])

    def test_create_user_invalid_first_name_length(self):
        data = self.valid_data.copy()
        data["first_name"] = "te"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["first_name"]
        )

        data = self.valid_data.copy()
        data["first_name"] = "test" * 10
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.",
            response.data["first_name"],
        )

    def test_create_user_invalid_last_name_length(self):
        data = self.valid_data.copy()
        data["last_name"] = "te"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["last_name"]
        )

        data = self.valid_data.copy()
        data["last_name"] = "test" * 10
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.",
            response.data["last_name"],
        )

    def test_create_user_invalid_username_length(self):
        data = self.valid_data.copy()
        data["username"] = "te"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["username"]
        )
        data = self.valid_data.copy()
        data["username"] = "test" * 10
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.",
            response.data["username"],
        )

    def test_create_user_invalid_password_length(self):
        data = self.valid_data.copy()
        data["password"] = "test1"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertIn(
            "Ensure this field has at least 8 characters.", response.data["password"]
        )
        data = self.valid_data.copy()
        data["password"] = "test1" * 10
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertIn(
            "Ensure this field has no more than 30 characters.",
            response.data["password"],
        )

    def test_create_user_invalid_password_complexity(self):
        data = self.valid_data.copy()
        data["password"] = "testtest"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertIn(
            "Das Passwort muss mindestens eine Zahl enthalten.",
            response.data["password"],
        )
        data = self.valid_data.copy()
        data["password"] = "12345678"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertIn(
            "Das Passwort muss mindestens einen Buchstaben enthalten.",
            response.data["password"],
        )

    def test_create_user_missing_team_code_join_team(self):
        data = self.valid_data.copy()
        data["join_team"] = True
        data["team_code"] = ""
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_code", response.data)
        self.assertIn("Bitte geben Sie einen Teamcode ein.", response.data["team_code"])

    def test_create_user_invalid_team_code(self):
        data = self.valid_data.copy()
        data["join_team"] = True
        data["team_code"] = "invalid"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_code", response.data)
        self.assertIn("Dieser Teamcode ist ungültig.", response.data["team_code"])

    def test_create_user_full_team(self):
        team = Team.objects.create(name="test", code="testcode")
        for i in range(4):
            user = User.objects.create_user(username=f"test{i}", password="password")
            user.profile.team = team
            user.profile.save()
        data = self.valid_data.copy()
        data["join_team"] = True
        data["team_code"] = "testcode"
        del data["team_name"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_code", response.data)
        self.assertIn("Dieses Team ist bereits voll.", response.data["team_code"])

    def test_create_user_missing_team_name_create_team(self):
        data = self.valid_data.copy()
        data["team_name"] = ""
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_name", response.data)
        self.assertIn(
            "Bitte geben Sie einen Teamnamen ein.", response.data["team_name"]
        )

    def test_create_user_invalid_team_name(self):
        Team.objects.create(name="Existing Team")
        data = self.valid_data.copy()
        data["team_name"] = "Existing Team"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_name", response.data)
        self.assertIn(
            "Dieser Teamname ist bereits vergeben.", response.data["team_name"]
        )


class UserProfileUpdateViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        self.team = Team.objects.create(name="Test Team")
        self.profile = self.user.profile
        self.url = reverse("user-profile-update")
        self.client.force_authenticate(user=self.user)

    def test_update_user_profile_success(self):
        data = {
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "username": "updateduser",
            "email": "updated@example.com",
        }
        self.profile.last_edited = timezone.now() - timedelta(days=1)
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedFirst")
        self.assertEqual(self.user.last_name, "UpdatedLast")
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")

    def test_update_user_profile_username_exists(self):
        User.objects.create_user(
            username="otheruser", password="testpassword", email="other@example.com"
        )
        data = {"username": "otheruser"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn(
            "Dieser Benutzername ist bereits vergeben.", response.data["username"]
        )

    def test_update_user_profile_email_exists(self):
        User.objects.create_user(
            username="otheruser", password="testpassword", email="other@example.com"
        )
        data = {"email": "other@example.com"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn(
            "Diese E-Mail-Adresse ist bereits registriert.", response.data["email"]
        )

    def test_update_user_profile_invalid_first_name_length(self):
        data = {"first_name": "te"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["first_name"]
        )
        data = {"first_name": "test" * 10}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.",
            response.data["first_name"],
        )

    def test_update_user_profile_invalid_last_name_length(self):
        data = {"last_name": "te"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["last_name"]
        )
        data = {"last_name": "test" * 10}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.",
            response.data["last_name"],
        )

    def test_update_user_profile_invalid_username_length(self):
        data = {"username": "te"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn(
            "Ensure this field has at least 3 characters.", response.data["username"]
        )
        data = {"username": "test" * 10}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn(
            "Ensure this field has no more than 20 characters.",
            response.data["username"],
        )

    def test_update_user_profile_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"first_name": "UpdatedFirst"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class StockHoldingListViewTests(APITestCase):
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
        self.stock_holding1 = StockHolding.objects.create(
            team=self.team, stock=self.stock1, amount=5
        )
        self.stock_holding2 = StockHolding.objects.create(
            team=self.team, stock=self.stock2, amount=0
        )  # Zero amount

    def test_stock_holding_list_success(self):
        url = reverse("stock-holdings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one holding with > 0
        self.assertEqual(response.data[0]["stock"]["name"], "Stock 1")
        self.assertEqual(response.data[0]["amount"], 5)

    def test_stock_holding_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("stock-holdings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TransactionViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.user.profile.team = self.team
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="STK1", current_price=100.00
        )
        self.stock2 = Stock.objects.create(
            name="Stock 2", ticker="STK2", current_price=50.00
        )
        self.stock_holding = StockHolding.objects.create(
            team=self.team, stock=self.stock1, amount=5
        )
        self.transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock1,
            transaction_type="buy",
            amount=2,
            price=100.00,
            fee=15.00,
        )

        self.other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.other_team = Team.objects.create(name="Other Team", balance=100000)
        self.other_user.profile.team = self.other_team
        self.other_user.profile.save()
        self.other_transaction = Transaction.objects.create(
            team=self.other_team,
            stock=self.stock1,
            transaction_type="buy",
            amount=2,
            price=100.00,
            fee=15.00,
        )

    def test_transaction_list_success(self):
        url = reverse("transaction-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["stock"]["name"], "Stock 1")
        self.assertEqual(response.data[0]["amount"], 2)
        self.assertEqual(float(response.data[0]["total_price"]), 215.00)

    def test_transaction_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("transaction-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_transaction_create_buy_success(self):
        url = reverse("transaction-create")
        data = {
            "stock": self.stock2.pk,
            "transaction_type": "buy",
            "amount": 2,
            "description": "Test description",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stock"], self.stock2.pk)
        self.assertEqual(response.data["transaction_type"], "buy")
        self.assertEqual(response.data["amount"], 2)
        self.assertIn("description", response.data)

    def test_transaction_create_sell_success(self):
        url = reverse("transaction-create")
        data = {
            "stock": self.stock1.pk,
            "transaction_type": "sell",
            "amount": 2,
            "description": "Test description",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stock"], self.stock1.pk)
        self.assertEqual(response.data["transaction_type"], "sell")
        self.assertEqual(response.data["amount"], 2)
        self.assertIn("description", response.data)

    def test_transaction_create_buy_insufficient_funds(self):
        url = reverse("transaction-create")
        data = {"stock": self.stock1.pk, "transaction_type": "buy", "amount": 1000}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Nicht genügend Guthaben.", response.data["non_field_errors"][0])

    def test_transaction_create_sell_insufficient_stock(self):
        url = reverse("transaction-create")
        data = {"stock": self.stock1.pk, "transaction_type": "sell", "amount": 100}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Nicht genügend Aktien im Depot.", response.data["non_field_errors"][0]
        )

    def test_transaction_create_sell_no_stock(self):
        url = reverse("transaction-create")
        data = {"stock": self.stock2.pk, "transaction_type": "sell", "amount": 10}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Sie besitzen keine Aktien dieses Typs.",
            response.data["non_field_errors"][0],
        )

    def test_transaction_create_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("transaction-create")
        data = {"stock": self.stock1.pk, "transaction_type": "buy", "amount": 2}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_transaction_update_success(self):
        url = reverse("transaction-update", kwargs={"pk": self.transaction1.pk})
        data = {"description": "Updated description"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Updated description")
        self.transaction1.refresh_from_db()
        self.assertEqual(self.transaction1.description, "Updated description")

    def test_transaction_update_other_user(self):
        url = reverse("transaction-update", kwargs={"pk": self.other_transaction.pk})
        data = {"description": "Updated description"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_transaction.refresh_from_db()
        self.assertEqual(self.other_transaction.description, "")

    def test_transaction_update_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("transaction-update", kwargs={"pk": self.transaction1.pk})
        data = {"description": "Updated description"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AnalysisViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.user.profile.team = self.team
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)
        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="STK1", current_price=100.00
        )
        self.stock2 = Stock.objects.create(
            name="Stock 2", ticker="STK2", current_price=50.00
        )
        self.stock3 = Stock.objects.create(
            name="Stock 3", ticker="STK3", current_price=200.00
        )

    def test_retrieve_analysis_success(self):
        # Create transactions and holdings to test data
        Transaction.objects.create(
            team=self.team,
            stock=self.stock1,
            transaction_type="buy",
            amount=2,
            price=100.00,
            fee=15.00,
        )
        Transaction.objects.create(
            team=self.team,
            stock=self.stock2,
            transaction_type="sell",
            amount=3,
            price=50.00,
            fee=10.00,
        )
        StockHolding.objects.create(team=self.team, stock=self.stock1, amount=3)

        url = reverse("analysis")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Asserts for the stock1
        self.assertEqual(response.data[1]["name"], "Stock 1")
        self.assertEqual(response.data[1]["ticker"], "STK1")
        self.assertEqual(response.data[1]["total_profit"], "85.00")
        self.assertEqual(response.data[1]["current_holding"], "300.00")

        # Asserts for the stock2
        self.assertEqual(response.data[0]["name"], "Stock 2")
        self.assertEqual(response.data[0]["ticker"], "STK2")
        self.assertEqual(response.data[0]["total_profit"], "140.00")
        self.assertEqual(response.data[0]["current_holding"], "0.00")

    def test_retrieve_analysis_no_transactions_or_holdings(self):
        url = reverse("analysis")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_analysis_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("analysis")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ValidateFormViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("validate-form")
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team", code="testcode")

    def test_validate_username_success(self):
        data = {"field": "username", "value": "newuser"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])

    def test_validate_password_success(self):
        data = {"field": "password", "value": "Test1234"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])

    def test_validate_team_code_success(self):
        data = {"field": "team_code", "value": "testcode"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])
        self.assertEqual(response.data["team_name"], "Test Team")

    def test_validate_team_name_success(self):
        data = {"field": "team_name", "value": "new team"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])

    def test_validate_username_exists(self):
        data = {"field": "username", "value": "testuser"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(
            response.data["message"], "Dieser Benutzername existiert bereits."
        )

    def test_validate_password_invalid_length(self):
        data = {"field": "password", "value": "test1"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(
            response.data["message"],
            "Das Passwort muss mindestens 8 Zeichen lang sein.",
        )
        data = {"field": "password", "value": "test1" * 10}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(
            response.data["message"], "Das Passwort kann maximal 30 Zeichen lang sein."
        )

    def test_validate_password_invalid_complexity(self):
        data = {"field": "password", "value": "testtest"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(
            response.data["message"],
            "Das Passwort muss mindestens eine Zahl enthalten.",
        )
        data = {"field": "password", "value": "12345678"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(
            response.data["message"],
            "Das Passwort muss mindestens einen Buchstaben enthalten.",
        )

    def test_validate_team_code_invalid(self):
        data = {"field": "team_code", "value": "invalid"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(response.data["message"], "Ungültiger Teamcode.")

    def test_validate_team_code_full(self):
        for i in range(4):
            user = User.objects.create_user(
                username=f"testuser{i}", password="password"
            )
            user.profile.team = self.team
            user.profile.save()

        data = {"field": "team_code", "value": "testcode"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(response.data["message"], "Das Team ist bereits voll.")

    def test_validate_team_name_exists(self):
        Team.objects.create(name="Existing Team")
        data = {"field": "team_name", "value": "Existing Team"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(
            response.data["message"], "Ein Team mit diesem Namen existiert bereits."
        )

    def test_validate_invalid_field(self):
        data = {"field": "invalid", "value": "test"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(response.data["message"], "Ungültige Anfrage!")


class SearchStocksViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("stock-search")
        self.stock1 = Stock.objects.create(
            name="Stock Test 1", ticker="STK1", current_price=100.00
        )
        self.stock2 = Stock.objects.create(
            name="Stock Test 2", ticker="STK2", current_price=50.00
        )
        self.stock3 = Stock.objects.create(
            name="Another Stock", ticker="STK3", current_price=100.00
        )

    def test_search_stocks_success(self):
        response = self.client.get(self.url, {"q": "Test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Stock Test 1")
        self.assertEqual(response.data[1]["name"], "Stock Test 2")

    def test_search_stocks_no_results(self):
        response = self.client.get(self.url, {"q": "nonexistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_stocks_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url, {"q": "Test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ValidateActivationTokenViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("validate-token", kwargs={"token": str(uuid.uuid4())})
        self.registration_request = RegistrationRequest.objects.create(
            email="test@example.com"
        )

    def test_validate_token_success(self):
        url = reverse(
            "validate-token",
            kwargs={"token": str(self.registration_request.activation_token)},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])
        self.assertEqual(response.data["email"], "test@example.com")

    def test_validate_token_invalid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(response.data["message"], "Ungültiges Token")

    def test_validate_token_already_activated(self):
        self.registration_request.activated = True
        self.registration_request.save()
        url = reverse(
            "validate-token",
            kwargs={"token": str(self.registration_request.activation_token)},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["valid"], False)
        self.assertEqual(response.data["message"], "Bereits aktiviert")

    def test_validate_token_unauthenticated(self):
        url = reverse(
            "validate-token",
            kwargs={"token": str(self.registration_request.activation_token)},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
