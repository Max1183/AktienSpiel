# Generated by Django 5.1.2 on 2024-10-17 17:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0011_transaction_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stockholding",
            name="stock",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stocks.stock"
            ),
        ),
        migrations.AlterField(
            model_name="stockholding",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="holdings",
                to="stocks.team",
            ),
        ),
    ]
