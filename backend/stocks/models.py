import binascii
import os
import uuid

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models import F, Sum
from django.db.models.aggregates import Count
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

USER = get_user_model()

DEFAULT_FRONTEND_URL = (
    "https://409f5ae8-31da-4c60-aff4-ab2291a4ae79.e1-eu-north-azure.choreoapps.dev"
)
FEE_PERCENTAGE = 0.001
MINIMUM_FEE = 15


class RegistrationRequest(models.Model):
    """
    Ein Request für die Registrierung eines neuen Benutzers.
    """

    user = models.OneToOneField(
        USER,
        on_delete=models.CASCADE,
        related_name="registration_request",
        null=True,
        blank=True,
    )
    email = models.EmailField()
    activation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)

    def send_activation_email(self):
        """
        Sendet eine Aktivierungs-E-Mail an die angegebene E-Mail-Adresse.
        """
        frontend_url = (
            settings.FRONTEND_URL if settings.FRONTEND_URL else DEFAULT_FRONTEND_URL
        )
        activation_link = f"{frontend_url}/activate/{self.activation_token}"

        subject = "Bestätigen Sie Ihr Konto beim Aktienspiel"
        html_message = render_to_string(
            "stocks/activation_email.html", {"activation_link": activation_link}
        )
        plain_message = strip_tags(html_message)
        to = [self.email]

        send_mail(
            subject,
            plain_message,
            None,
            to,
            html_message=html_message,
            fail_silently=False,
        )

    def __str__(self):
        return self.email


class Stock(models.Model):
    """
    Repräsentiert eine Aktie.
    """

    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    def calculate_fee(self, amount):
        """
        Berechnet die Transaktionsgebühr für den Kauf oder Verkauf einer Aktie.
        """
        fee = float(self.current_price) * amount * FEE_PERCENTAGE
        return max(MINIMUM_FEE, round(fee))


class History(models.Model):
    """
    Speichert historische Daten für eine Aktie.
    """

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
    """
    Repräsentiert ein Team von Spielern mit einem gemeinsamen Portfolio.
    """

    name = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=100000)
    stocks = models.ManyToManyField(Stock, through="StockHolding")
    code = models.CharField(max_length=8, unique=True, blank=True)
    portfolio_history = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    def get_portfolio_value(self):
        """Berechnet den Gesamtwert des Portfolios (Bargeld + Aktien)."""
        stock_value = (
            self.holdings.aggregate(
                total_value=Sum(F("stock__current_price") * F("amount"))
            )["total_value"]
            or 0
        )
        return self.balance + stock_value

    def calculate_rank(self):
        """Berechnet den Rang des Teams basierend auf dem Portfoliowert im Vergleich zu anderen Teams."""
        current_portfolio_value = self.get_portfolio_value()
        queryset = get_team_ranking_queryset()

        higher_ranked_teams = (
            queryset.annotate(
                portfolio_value=models.Case(
                    models.When(holdings__stock__isnull=True, then=F("balance")),
                    default=F("balance")
                    + Sum(F("holdings__stock__current_price") * F("holdings__amount")),
                    output_field=models.DecimalField(),
                )
            )
            .filter(portfolio_value__gt=current_portfolio_value)
            .count()
        )

        return higher_ranked_teams + 1

    @property
    def total_balance(self):
        """Gibt den Gesamtwert des Portfolios zurück (Property-Zugriff)."""
        return self.get_portfolio_value()

    @admin.display(description="Members")
    def team_member_count(self):
        """Gibt die Anzahl der Teammitglieder zurück."""
        return self.members.count()

    @admin.display(description="Gesamtdepotwert")
    def portfolio_value(self):
        """Gibt den formatierten Gesamtdepotwert für die Admin-Oberfläche zurück."""
        return f"{self.get_portfolio_value():.2f}€"

    @admin.display(description="Rang")
    def rank(self):
        """Gibt den Rang des Teams zurück."""
        return self.calculate_rank()

    def update_balance(self, amount_change):
        """Aktualisiert den Kontostand des Teams."""
        self.balance += amount_change
        self.save()


def get_team_ranking_queryset():
    """Gibt eine QuerySet zurück, die Teams enthält, die für das Ranking berücksichtigt werden."""
    queryset = (
        Team.objects.annotate(num_members=Count("members"))
        .filter(num_members__gt=0)
        .exclude(name="default")
        .exclude(name="Admin")
    )
    return queryset


@receiver(pre_save, sender=Team)
def generate_team_code(sender, instance, **kwargs):
    """
    Generiert einen eindeutigen Team-Code vor dem Speichern.
    """
    if not instance.code:
        while True:
            random_bytes = os.urandom(4)
            code = binascii.hexlify(random_bytes).decode("utf-8")[:8]
            if not Team.objects.filter(code=code).exists():
                instance.code = code
                break


class Watchlist(models.Model):
    """
    Enthält Aktien, die ein Team beobachtet.
    """

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="watchlist")
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock.name} in Watchlist of {self.team.name}"


class UserProfile(models.Model):
    """
    Erweiterung des Benutzer-Modells um zusätzliche Profilinformationen.
    """

    user = models.OneToOneField(USER, on_delete=models.CASCADE, related_name="profile")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    last_edited = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class StockHolding(models.Model):
    """
    Verknüpfungstabelle, die die Anzahl der Aktien darstellt, die ein Team besitzt.
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="holdings")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team.name} - {self.stock.name} ({self.amount})"

    def adjust_amount(self, quantity):
        """Passt die Anzahl der gehaltenen Aktien an."""
        self.amount += quantity
        self.save()


class Transaction(models.Model):
    """
    Repräsentiert eine einzelne Transaktion (Kauf oder Verkauf) von Aktien.
    """

    STATUS_CHOICES = [
        ("open", "Offen"),
        ("closed", "Abgeschlossen"),
        ("canceled", "Storniert"),
        ("error", "Fehler"),
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
    errors = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} - {self.stock.name} ({self.amount})"

    def get_total_price(self):
        """Berechnet den Gesamtpreis der Transaktion inklusive Gebühren."""
        return (self.amount * self.price) + (
            self.fee if self.transaction_type == "buy" else -self.fee
        )

    @admin.display(description="Gesamtpreis")
    def formatted_total_price(self):
        """Gibt den formatierten Gesamtpreis für die Admin-Oberfläche zurück."""
        return f"{self.get_total_price():.2f}€"
