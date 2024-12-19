import decimal
from datetime import datetime, timedelta, timezone

import pytz  # type: ignore
from django.contrib.auth.models import User
from django.test import TestCase

from ..models import (
    History,
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
)


class RegistrationRequestModelTests(TestCase):
    def test_registration_request_creation(self):
        registration_request = RegistrationRequest.objects.create(
            email="test@example.com"
        )
        self.assertEqual(registration_request.email, "test@example.com")
        self.assertFalse(registration_request.activated)
        self.assertIsNotNone(registration_request.activation_token)
        self.assertIsNotNone(registration_request.created_at)

    def test_registration_request_str(self):
        registration_request = RegistrationRequest.objects.create(
            email="test@example.com"
        )
        self.assertEqual(str(registration_request), "test@example.com")


class StockModelTests(TestCase):
    def test_stock_creation(self):
        stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=decimal.Decimal("100.50")
        )
        self.assertEqual(stock.name, "Test Stock")
        self.assertEqual(stock.ticker, "TST")
        self.assertEqual(stock.current_price, decimal.Decimal("100.50"))

    def test_stock_str(self):
        stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=decimal.Decimal("100.50")
        )
        self.assertEqual(str(stock), "Test Stock")


class HistoryModelTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=decimal.Decimal("100.50")
        )

    def test_history_creation(self):
        history = History.objects.create(
            stock=self.stock,
            name="Day",
            period="1d",
            interval="5m",
            values=[100, 102, 101],
        )
        self.assertEqual(history.stock, self.stock)
        self.assertEqual(history.name, "Day")
        self.assertEqual(history.period, "1d")
        self.assertEqual(history.interval, "5m")
        self.assertEqual(history.values, [100, 102, 101])

    def test_history_str(self):
        history = History.objects.create(
            stock=self.stock,
            name="Day",
            period="2024-10-26",
            interval="1d",
            values=[100, 102, 101],
        )
        self.assertEqual(str(history), "Test Stock - Day")


class TeamModelTests(TestCase):
    def setUp(self):
        Team.objects.create(name="default")
        self.team = Team.objects.create(name="Test Team")
        self.stock1 = Stock.objects.create(
            name="Stock 1", ticker="STK1", current_price=decimal.Decimal("50.00")
        )
        self.stock2 = Stock.objects.create(
            name="Stock 2", ticker="STK2", current_price=decimal.Decimal("100.00")
        )

    def test_team_creation(self):
        self.assertEqual(self.team.name, "Test Team")
        self.assertEqual(self.team.balance, decimal.Decimal("100000.00"))

    def test_team_str(self):
        self.assertEqual(str(self.team), "Test Team")

    def test_team_member_count(self):
        user1 = User.objects.create_user(username="user1")
        user2 = User.objects.create_user(username="user2")

        user1.profile.team = self.team
        user1.profile.save()

        user2.profile.team = self.team
        user2.profile.save()

        self.assertEqual(self.team.team_member_count(), 2)

    def test_portfolio_value(self):
        StockHolding.objects.create(team=self.team, stock=self.stock1, amount=10)
        StockHolding.objects.create(team=self.team, stock=self.stock2, amount=5)

        balance = self.team.balance
        stock_balance = (self.stock1.current_price * 10) + (
            self.stock2.current_price * 5
        )
        total_value = balance + stock_balance
        self.assertEqual(self.team.portfolio_value(), f"{total_value:.2f}€")

    def test_update_balance(self):
        self.team.update_balance(decimal.Decimal("100.00"))
        self.assertEqual(self.team.balance, decimal.Decimal("100100.00"))
        self.team.update_balance(decimal.Decimal("-50.00"))
        self.assertEqual(self.team.balance, decimal.Decimal("100050.00"))


class WatchlistModelTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team")
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=decimal.Decimal("100.50")
        )

    def test_watchlist_creation(self):
        watchlist = self.team.watchlist.create(stock=self.stock)
        self.assertEqual(watchlist.team, self.team)
        self.assertEqual(watchlist.stock, self.stock)

    def test_watchlist_str(self):
        watchlist = self.team.watchlist.create(stock=self.stock)
        self.assertEqual(str(watchlist), "Test Stock in Watchlist of Test Team")


class UserProfileModelTests(TestCase):
    def setUp(self):
        Team.objects.create(name="default")
        self.user = User.objects.create_user(username="testuser")
        self.team = Team.objects.create(name="Test Team")

    def test_userprofile_auto_creation(self):
        profile = self.user.profile
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.team, Team.objects.get(name="default"))

    def test_userprofile_str(self):
        profile = self.user.profile
        self.assertEqual(str(profile), "Profile of testuser")


class StockHoldingModelTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Test Team")
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=decimal.Decimal("100.50")
        )

    def test_stockholding_creation(self):
        holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=10
        )
        self.assertEqual(holding.team, self.team)
        self.assertEqual(holding.stock, self.stock)
        self.assertEqual(holding.amount, 10)

    def test_stockholding_str(self):
        holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=10
        )
        self.assertEqual(str(holding), "Test Team - Test Stock (10)")

    def test_adjust_amount(self):
        holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=10
        )
        holding.adjust_amount(5)
        self.assertEqual(holding.amount, 15)
        holding.adjust_amount(-15)
        self.assertEqual(holding.amount, 0)


class TransactionModelTests(TestCase):

    def setUp(self):
        self.team = Team.objects.create(name="Test Team")
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=decimal.Decimal("100.50")
        )

    def test_transaction_creation(self):
        berlin_tz = pytz.timezone("Europe/Berlin")
        now = datetime.now(timezone.utc).astimezone(berlin_tz)

        transaction = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            status="open",
            transaction_type="buy",
            amount=10,
            price=decimal.Decimal("100.50"),
            fee=decimal.Decimal("15.00"),
            description="Test Transaction",
        )
        self.assertEqual(transaction.team, self.team)
        self.assertEqual(transaction.stock, self.stock)
        self.assertEqual(transaction.status, "open")
        self.assertEqual(transaction.transaction_type, "buy")
        self.assertEqual(transaction.amount, 10)
        self.assertEqual(transaction.price, decimal.Decimal("100.50"))
        self.assertEqual(transaction.fee, decimal.Decimal("15.00"))
        self.assertEqual(transaction.description, "Test Transaction")
        self.assertAlmostEqual(transaction.date, now, delta=timedelta(seconds=1))

    def test_transaction_str(self):
        transaction = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=10,
            price=decimal.Decimal("100.50"),
            fee=decimal.Decimal("15.00"),
        )
        self.assertEqual(str(transaction), "Test Team - Test Stock (10)")

    def test_total_price_buy(self):
        transaction = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=10,
            price=decimal.Decimal("100.50"),
            fee=decimal.Decimal("15.00"),
        )
        self.assertEqual(transaction.total_price(), "1020.00€")

    def test_total_price_sell(self):
        transaction = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=10,
            price=decimal.Decimal("100.50"),
            fee=decimal.Decimal("15.00"),
        )
        self.assertEqual(transaction.total_price(), "990.00€")
