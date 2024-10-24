from django.test import TestCase

from ..models import Stock, StockHolding, Team, Transaction
from ..transactions import execute_transaction


class ExecuteTransactionTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team", balance=1000)
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TS", current_price=10
        )

    def test_buy_transaction_success(self):
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=10,
            price=10,
            fee=5,
        )
        execute_transaction(ta)

        self.assertEqual(ta.status, "closed")
        self.assertEqual(self.team.balance, 900 - 5)  # Überprüfe auch die Gebühr
        self.assertTrue(
            StockHolding.objects.filter(
                team=self.team, stock=self.stock, amount=10
            ).exists()
        )

    def test_buy_transaction_insufficient_funds(self):
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=10000,  # Kaufe zu viel
            price=10,
            fee=5,
        )
        execute_transaction(ta)

        self.assertEqual(ta.status, "error")
        self.assertIn("Nicht genügend Guthaben", ta.description)
        self.assertEqual(self.team.balance, 1000)  # Balance sollte unverändert sein
        self.assertFalse(
            StockHolding.objects.filter(team=self.team, stock=self.stock).exists()
        )

    def test_sell_transaction_success(self):
        StockHolding.objects.create(team=self.team, stock=self.stock, amount=20)
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=10,
            price=12,  # Verkaufe zu höherem Preis
            fee=2,
        )
        execute_transaction(ta)

        self.assertEqual(ta.status, "closed")
        self.assertEqual(
            self.team.balance, 1000 + 120 - 2
        )  # Überprüfe Verkaufspreis und Gebühr
        self.assertTrue(
            StockHolding.objects.filter(
                team=self.team, stock=self.stock, amount=10
            ).exists()
        )

    def test_sell_transaction_insufficient_shares(self):
        StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=5
        )  # Weniger Aktien
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=10,
            price=10,
            fee=2,
        )
        execute_transaction(ta)

        self.assertEqual(ta.status, "error")
        self.assertIn(
            f"Sie besitzen nur 5 Aktien von {self.stock.name}.", ta.description
        )
        self.assertEqual(self.team.balance, 1000)  # Balance sollte unverändert sein
        self.assertEqual(
            StockHolding.objects.get(team=self.team, stock=self.stock).amount, 5
        )

    def test_sell_transaction_no_holding(self):
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=10,
            price=10,
            fee=2,
        )
        execute_transaction(ta)

        self.assertEqual(ta.status, "error")
        self.assertIn("Sie haben keine Aktien von diesem Unternehmen.", ta.description)
        self.assertEqual(self.team.balance, 1000)

    def test_invalid_transaction_type(self):
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="invalid",  # Ungültiger Typ
            amount=10,
            price=10,
            fee=5,
        )
        execute_transaction(ta)

        self.assertEqual(ta.status, "error")
        self.assertIn("Ungültiger Transaktionstyp.", ta.description)
        self.assertEqual(self.team.balance, 1000)

    def test_transaction_already_closed(self):
        ta = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=10,
            price=10,
            fee=5,
            status="closed",  # Bereits geschlossen
        )

        execute_transaction(ta)

        # Sollte keine Änderungen vornehmen, da bereits geschlossen
        self.assertEqual(ta.status, "closed")
        self.assertEqual(self.team.balance, 1000)
