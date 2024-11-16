from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from ..models import RegistrationRequest, Stock


class SearchStocksViewTests(TestCase):
    def setUp(self):
        self.stock1 = Stock.objects.create(
            name="Apple Inc.", ticker="AAPL", current_price=Decimal("150.00")
        )
        self.stock2 = Stock.objects.create(
            name="Microsoft Corporation", ticker="MSFT", current_price=Decimal("300.00")
        )
        self.stock3 = Stock.objects.create(
            name="Alphabet Inc.", ticker="GOOG", current_price=Decimal("2500.00")
        )
        self.url = reverse("stock-search")

    def test_search_with_query(self):
        response = self.client.get(self.url, {"q": "Apple"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"id": self.stock1.id, "name": "Apple Inc.", "current_price": "150.00"}],
        )

    def test_search_with_partial_query(self):
        response = self.client.get(self.url, {"q": "corp"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": self.stock2.id,
                    "name": "Microsoft Corporation",
                    "current_price": "300.00",
                }
            ],
        )

    def test_search_with_no_results(self):
        response = self.client.get(self.url, {"q": "Nonexistent"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_search_with_empty_query(self):
        response = self.client.get(self.url)  # Keine 'q' Parameter
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_search_with_multiple_results(self):
        response = self.client.get(self.url, {"q": "Inc"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)  # 2 Ergebnisse erwartet

        #  Sortieren, um die Reihenfolge der Ergebnisse nicht zu beachten
        expected_results = sorted(
            [
                {"id": self.stock1.id, "name": "Apple Inc.", "current_price": "150.00"},
                {
                    "id": self.stock3.id,
                    "name": "Alphabet Inc.",
                    "current_price": "2500.00",
                },
            ],
            key=lambda x: x["id"],
        )
        received_results = sorted(response.json(), key=lambda x: x["id"])
        self.assertEqual(received_results, expected_results)


class RegisterPlayerViewTests(TestCase):
    def setUp(self):
        self.url = reverse("register_player")
        self.valid_email = "test01@example.com"
        self.invalid_email = "invalid_email"

        self.user = User.objects.create_superuser(
            "testuser", "test@example.com", "password"
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_register_player_valid_email(self):
        response = self.client.post(self.url, {"email": self.valid_email})
        # Überprüfen, ob ein Registrierungsanfrage-Objekt erstellt wurde
        self.assertRedirects(response, reverse("admin:index"))
        self.assertEqual(RegistrationRequest.objects.count(), 1)
        registration_request = RegistrationRequest.objects.get(email=self.valid_email)
        self.assertIsNotNone(registration_request)

    def test_register_player_existing_email(self):
        RegistrationRequest.objects.create(email=self.valid_email)
        self.client.post(self.url, {"email": self.valid_email})
        self.assertEqual(RegistrationRequest.objects.count(), 1)
        self.assertEqual(
            RegistrationRequest.objects.filter(email=self.valid_email).count(), 1
        )


class ValidateActivationTokenViewTests(TestCase):
    def setUp(self):
        self.registration_request = RegistrationRequest.objects.create(
            email="test@example.com"
        )
        self.token = self.registration_request.activation_token

        self.registration_request1 = RegistrationRequest.objects.create(
            email="test1@example.com"
        )
        self.wrong_token = self.registration_request1.activation_token
        self.registration_request1.delete()

        self.invalid_token = "invalid_token"
        self.valid_url = reverse("validate_activation_token", args=[self.token])
        self.invalid_url = reverse(
            "validate_activation_token", args=[self.invalid_token]
        )
        self.wrong_url = reverse("validate_activation_token", args=[self.wrong_token])

    def test_validate_activation_token_valid(self):
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"valid": True, "email": "test@example.com"})

    def test_validate_activation_token_active(self):
        self.registration_request.activated = True
        self.registration_request.save()

        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"valid": False, "message": "Bereits aktiviert"}
        )

    def test_validate_activation_token_invalid_token(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"valid": False, "message": "Ungültiges Token"}
        )

    def test_validate_activation_token_wrong_token(self):
        response = self.client.get(self.wrong_url)
        self.assertEqual(response.status_code, 404)
