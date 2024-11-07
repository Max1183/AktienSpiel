# Generated by Django 5.1.3 on 2024-11-06 17:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0018_watchlist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="watchlist",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="watchlist",
                to="stocks.team",
            ),
        ),
    ]