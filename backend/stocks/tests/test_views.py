from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from ..models import Stock


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
