from django.db import models


class Stock(models.Model):
    name = models.CharField(max_length=30)
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
        return f"{self.stock.name} - {self.period}"
