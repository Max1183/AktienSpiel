from decimal import Decimal

from django.test import TestCase

from stocks.models import Stock, StockHolding, Team, Transaction
from stocks.services import (
    calculate_stock_profit,
    execute_transaction,
    transaction_error,
)


class ServiceFunctionTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team", balance=100000.00)
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )

    def test_calculate_stock_profit(self):
        # Test with a list of valid transactions
        transactions = [
            Transaction(
                team=self.team,
                stock=self.stock,
                transaction_type="buy",
                amount=2,
                price=Decimal("100.00"),
                fee=Decimal("15.00"),
            ),
            Transaction(
                team=self.team,
                stock=self.stock,
                transaction_type="sell",
                amount=1,
                price=Decimal("110.00"),
                fee=Decimal("10.00"),
            ),
        ]
        profit = calculate_stock_profit(transactions)
        self.assertEqual(profit, Decimal("-115.00"))

        # Test with no transactions
        profit = calculate_stock_profit([])
        self.assertEqual(profit, Decimal("0.00"))

        # Test with only sell transactions
        transactions = [
            Transaction(
                team=self.team,
                stock=self.stock,
                transaction_type="sell",
                amount=2,
                price=Decimal("100.00"),
                fee=Decimal("15.00"),
            ),
            Transaction(
                team=self.team,
                stock=self.stock,
                transaction_type="sell",
                amount=1,
                price=Decimal("110.00"),
                fee=Decimal("10.00"),
            ),
        ]
        profit = calculate_stock_profit(transactions)
        self.assertEqual(profit, Decimal("285.00"))

        # Test with only buy transactions
        transactions = [
            Transaction(
                team=self.team,
                stock=self.stock,
                transaction_type="buy",
                amount=2,
                price=Decimal("100.00"),
                fee=Decimal("15.00"),
            ),
            Transaction(
                team=self.team,
                stock=self.stock,
                transaction_type="buy",
                amount=1,
                price=Decimal("110.00"),
                fee=Decimal("10.00"),
            ),
        ]
        profit = calculate_stock_profit(transactions)
        self.assertEqual(profit, Decimal("-335.00"))

    def test_execute_transaction_buy_success(self):
        transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=2,
            price=100.00,
            fee=15.00,
        )
        execute_transaction(transaction1)
        transaction1.refresh_from_db()
        self.assertEqual(transaction1.status, "closed")
        self.assertEqual(self.team.balance, 100000 - 2 * 100 - 15)
        stock_holding = StockHolding.objects.get(team=self.team, stock=self.stock)
        self.assertEqual(stock_holding.amount, 2)
        self.assertEqual(transaction1.errors, "")

    def test_execute_transaction_sell_success(self):
        stock_holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=5
        )
        transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=2,
            price=100.00,
            fee=15.00,
        )
        execute_transaction(transaction1)
        transaction1.refresh_from_db()
        self.assertEqual(transaction1.status, "closed")
        self.assertEqual(self.team.balance, 100000 + 2 * 100 - 15)
        stock_holding = StockHolding.objects.get(team=self.team, stock=self.stock)
        self.assertEqual(stock_holding.amount, 3)
        self.assertEqual(transaction1.errors, "")

    def test_execute_transaction_buy_insufficient_funds(self):
        transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=1000,
            price=100.00,
            fee=15.00,
        )
        execute_transaction(transaction1)
        transaction1.refresh_from_db()
        self.assertEqual(transaction1.status, "error")
        self.assertIn("Nicht genügend Guthaben.", transaction1.errors)

    def test_execute_transaction_sell_insufficient_stock(self):
        StockHolding.objects.create(team=self.team, stock=self.stock, amount=5)
        transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=100,
            price=100.00,
            fee=15.00,
        )
        execute_transaction(transaction1)
        transaction1.refresh_from_db()
        self.assertEqual(transaction1.status, "error")
        self.assertIn("Sie besitzen nur 5 Aktien von Test Stock.", transaction1.errors)

    def test_execute_transaction_invalid_transaction_type(self):
        transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="invalid",
            amount=2,
            price=100.00,
            fee=15.00,
        )
        execute_transaction(transaction1)
        transaction1.refresh_from_db()
        self.assertEqual(transaction1.status, "error")
        self.assertIn("Ungültiger Transaktionstyp.", transaction1.errors)

    def test_transaction_error(self):
        transaction1 = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=2,
            price=100.00,
            fee=15.00,
            status="open",
        )
        error_message = "Test Error"
        transaction_error(transaction1, error_message)
        transaction1.refresh_from_db()
        self.assertEqual(transaction1.status, "error")
        self.assertEqual(transaction1.errors, error_message)
