# Generated by Django 5.1.1 on 2024-10-06 13:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0003_alter_stock_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StockHolding",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.IntegerField(default=0)),
                (
                    "stock",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stocks.stock"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("balance", models.FloatField(default=100000)),
                (
                    "members",
                    models.ManyToManyField(
                        related_name="teams", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "stocks",
                    models.ManyToManyField(
                        through="stocks.StockHolding", to="stocks.stock"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="stockholding",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.team"
            ),
        ),
    ]
