# Generated by Django 5.1.3 on 2024-11-16 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0024_alter_team_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="nickname",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="nickname_cooldown",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="first_name",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="last_name",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]