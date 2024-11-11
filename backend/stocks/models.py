from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum


class Stock(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class History(models.Model):
    HISTORY_NAME_CHOICES = (
        ("Day", "Tag"),
        ("5 Days", "5 Tage"),
        ("Month", "Monat"),
        ("3 Months", "3 Monate"),
        ("Year", "Jahr"),
        ("5 Years", "5 Jahre"),
    )

    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="history_entries"
    )

    name = models.CharField(max_length=10, choices=HISTORY_NAME_CHOICES)
    period = models.CharField(max_length=10)
    interval = models.CharField(max_length=10)

    values = models.JSONField(default=list)

    def __str__(self):
        return f"{self.stock.name} - {self.name}"


class Team(models.Model):
    name = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=100000)
    stocks = models.ManyToManyField(Stock, through="StockHolding")

    def __str__(self):
        return self.name

    @admin.display(description="Members")
    def team_member_count(self):
        return self.members.count()

    @admin.display(description="Gesamtdepotwert")
    def portfolio_value(self):
        total = Sum(F("stock__current_price") * F("amount"))
        stock_balance = self.holdings.aggregate(total_value=total)["total_value"] or 0

        total_value = self.balance + stock_balance
        return f"{total_value:.2f}€"

    def update_balance(self, amount_change):
        self.balance += amount_change
        self.save()


class Watchlist(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="watchlist")
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock.name} in Watchlist of {self.team.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")

    def __str__(self):
        return f"Profile of {self.user.username}"


class StockHolding(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="holdings")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team.name} - {self.stock.name} ({self.amount})"

    def adjust_amount(self, quantity):
        self.amount += quantity

        if self.amount == 0:
            self.delete()
        else:
            self.save()


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("canceled", "Canceled"),
        ("error", "Error"),
    ]

    TRANSACTION_TYPE_CHOICES = (
        ("buy", "Kaufen"),
        ("sell", "Verkaufen"),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)

    amount = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fee = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} - {self.stock.name} ({self.amount})"

    @admin.display(description="Total Price")
    def total_price(self):
        fee = (1 if self.transaction_type == "buy" else -1) * self.fee
        total_price = self.amount * self.price + fee
        return str(round(total_price, 2)) + "€"
