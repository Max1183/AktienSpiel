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
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='teams')
    balance = models.FloatField(default=100000)
    stocks = models.ManyToManyField(Stock, through='StockHolding')

    def __str__(self):
        return self.name


class StockHolding(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team.name} - {self.stock.name} ({self.amount})"
