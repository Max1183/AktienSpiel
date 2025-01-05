from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import (
    History,
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
    UserProfile,
    Watchlist,
)

User = get_user_model()


class RegistrationRequestTests(TestCase):
    def test_registration_request_creation(self):
        user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )
        registration_request = RegistrationRequest.objects.create(
            email="test@example.com", user=user
        )
        self.assertTrue(RegistrationRequest.objects.exists())
        self.assertEqual(registration_request.email, "test@example.com")
        self.assertFalse(registration_request.activated)

    def test_registration_request_str_method(self):
        registration_request = RegistrationRequest.objects.create(
            email="test@example.com"
        )
        self.assertEqual(str(registration_request), "test@example.com")


class StockTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )

    def test_stock_creation(self):
        self.assertTrue(Stock.objects.exists())
        self.assertEqual(self.stock.name, "Test Stock")
        self.assertEqual(self.stock.ticker, "TST")
        self.assertEqual(self.stock.current_price, 100.00)

    def test_stock_str_method(self):
        self.assertEqual(str(self.stock), "Test Stock")

    def test_calculate_fee(self):
        fee = self.stock.calculate_fee(10)  # 10 Aktien
        self.assertGreaterEqual(fee, 15)  # Sollte mindestens die MINIMUM_FEE sein


class HistoryTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.history = History.objects.create(
            stock=self.stock, name="Day", period="1d", interval="5m", values=[]
        )

    def test_history_creation(self):
        self.assertTrue(History.objects.exists())
        self.assertEqual(self.history.stock, self.stock)
        self.assertEqual(self.history.name, "Day")

    def test_history_str_method(self):
        self.assertEqual(str(self.history), "Test Stock - Day")


class TeamTests(TestCase):
    def setUp(self):
        self.team1 = Team.objects.create(name="Team 1", balance=100000)
        self.team2 = Team.objects.create(name="Team 2", balance=50000)
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.holding = StockHolding.objects.create(
            team=self.team1, stock=self.stock, amount=10
        )

    def test_team_creation(self):
        self.assertTrue(Team.objects.exists())
        self.assertEqual(self.team1.name, "Team 1")
        self.assertEqual(self.team1.balance, 100000)

    def test_team_str_method(self):
        self.assertEqual(str(self.team1), "Team 1")

    def test_get_portfolio_value(self):
        # Team 1 hat 10 Aktien zum Preis von 100€ + 100000€ Guthaben
        self.assertEqual(self.team1.get_portfolio_value(), 100 * 10 + 100000)

    def test_calculate_rank(self):
        self.assertEqual(self.team1.calculate_rank(), 1)  # Team 1 hat höheren Wert
        self.assertEqual(self.team2.calculate_rank(), 2)  # Team 2 hat niedrigeren Wert

    def test_update_balance(self):
        self.team1.update_balance(5000)
        self.assertEqual(self.team1.balance, 105000)

    def test_generate_team_code(self):
        team = Team.objects.create(name="Team ohne Code")
        self.assertIsNotNone(team.code)
        self.assertEqual(len(team.code), 8)


class WatchlistTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.watchlist = Watchlist.objects.create(stock=self.stock, team=self.team)

    def test_watchlist_creation(self):
        self.assertTrue(Watchlist.objects.exists())
        self.assertEqual(self.watchlist.stock, self.stock)
        self.assertEqual(self.watchlist.team, self.team)

    def test_watchlist_str_method(self):
        self.assertEqual(str(self.watchlist), "Test Stock in Watchlist of Test Team")


class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)

        self.profile = self.user.profile
        self.profile.team = self.team
        self.profile.save()

    def test_user_profile_creation(self):
        self.assertTrue(UserProfile.objects.exists())
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.team, self.team)

    def test_user_profile_str_method(self):
        self.assertEqual(str(self.profile), "Profile of testuser")


class StockHoldingTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.stock_holding = StockHolding.objects.create(
            team=self.team, stock=self.stock, amount=5
        )

    def test_stock_holding_creation(self):
        self.assertTrue(StockHolding.objects.exists())
        self.assertEqual(self.stock_holding.team, self.team)
        self.assertEqual(self.stock_holding.stock, self.stock)
        self.assertEqual(self.stock_holding.amount, 5)

    def test_stock_holding_str_method(self):
        self.assertEqual(str(self.stock_holding), "Test Team - Test Stock (5)")

    def test_adjust_amount(self):
        self.stock_holding.adjust_amount(3)
        self.assertEqual(self.stock_holding.amount, 8)


class TransactionTests(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            name="Test Stock", ticker="TST", current_price=100.00
        )
        self.team = Team.objects.create(name="Test Team", balance=100000)
        self.transaction = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="buy",
            amount=2,
            price=100,
            fee=15,
        )

    def test_transaction_creation(self):
        self.assertTrue(Transaction.objects.exists())
        self.assertEqual(self.transaction.team, self.team)
        self.assertEqual(self.transaction.stock, self.stock)
        self.assertEqual(self.transaction.amount, 2)

    def test_transaction_str_method(self):
        self.assertEqual(str(self.transaction), "Test Team - Test Stock (2)")

    def test_get_total_price_buy(self):
        self.assertEqual(self.transaction.get_total_price(), 2 * 100 + 15)

    def test_get_total_price_sell(self):
        sell_transaction = Transaction.objects.create(
            team=self.team,
            stock=self.stock,
            transaction_type="sell",
            amount=2,
            price=100,
            fee=15,
        )
        self.assertEqual(sell_transaction.get_total_price(), 2 * 100 - 15)

    def test_formatted_total_price(self):
        self.assertEqual(self.transaction.formatted_total_price(), "215.00€")
