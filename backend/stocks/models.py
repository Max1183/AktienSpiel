from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models


class Stock(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    current_price = models.FloatField(default=0)

    def __str__(self):
        return self.name


class History(models.Model):
    stock = models.ForeignKey(Stock,
                              on_delete=models.CASCADE,
                              related_name='history_entries')
    name = models.CharField(max_length=10)
    period = models.CharField(max_length=10)
    interval = models.CharField(max_length=10)
    values = models.JSONField(default=list)

    def __str__(self):
        return f"{self.stock.name} - {self.name}"


class Team(models.Model):
    name = models.CharField(max_length=20)
    balance = models.FloatField(default=100000)
    stocks = models.ManyToManyField(Stock, through='StockHolding')

    def __str__(self):
        return self.name

    @admin.display(description='Members')
    def team_member_count(self):
        return self.members.count()

    @admin.display(description='Gesamtdepotwert')
    def team_balance(self):
        stock_balance = sum([
            holdings.stock.current_price * holdings.amount
            for holdings in self.holdings.all()
        ])
        return f"{self.balance + stock_balance:.2f}€"

    def update_balance(self, amount_change):
        self.balance += amount_change
        self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             related_name='members')

    def __str__(self):
        return f'Profile of {self.user.username}'


class StockHolding(models.Model):
    team = models.ForeignKey(Team,
                             on_delete=models.CASCADE,
                             related_name='holdings')
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


# status: open, closed, canceled, error
class Transaction(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default="open")
    amount = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    fee = models.FloatField(default=0)
    transaction_type = models.CharField(max_length=5)
    description = models.TextField(default="")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} - {self.stock.name} ({self.amount})"

    @admin.display(description='Total Price')
    def total_price(self):
        fee = (1 if self.transaction_type == 'buy' else -1) * self.fee
        total_price = self.amount * self.price + fee
        return str(round(total_price, 2)) + "€"
