# Generated by Django 5.1.1 on 2024-10-04 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='history',
            old_name='time',
            new_name='name',
        ),
    ]
