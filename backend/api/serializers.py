from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from stocks.models import (
    History,
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
    UserProfile,
    Watchlist,
)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer für das Abrufen eines Tokens."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        return token


class RegistrationRequestSerializer(serializers.ModelSerializer):
    """Serializer für die Registrierungsanfrage."""

    class Meta:
        model = RegistrationRequest
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f"Ein Benutzer mit der E-Mail-Adresse {email} existiert bereits."
            )

        if RegistrationRequest.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f"Eine Registrierungsanfrage für {email} existiert bereits."
            )

        return attrs


class HistorySerializer(serializers.ModelSerializer):
    """Serializer für Aktienhistorie."""

    name = serializers.CharField(source="get_name_display")

    class Meta:
        model = History
        fields = ["id", "name", "values"]
        read_only_fields = fields


class StockSerializer(serializers.ModelSerializer):
    """Serializer für Aktien."""

    history_entries = HistorySerializer(many=True, read_only=True)
    amount = serializers.SerializerMethodField()
    watchlist_id = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            "id",
            "name",
            "ticker",
            "current_price",
            "history_entries",
            "amount",
            "watchlist_id",
        ]

    def get_amount(self, obj):
        team = self.context["request"].user.profile.team
        try:
            stock_holding = StockHolding.objects.get(team=team, stock=obj)
            return stock_holding.amount
        except StockHolding.DoesNotExist:
            return 0

    def get_watchlist_id(self, obj):
        team = self.context["request"].user.profile.team
        try:
            watchlist_entry = Watchlist.objects.get(team=team, stock=obj)
            return watchlist_entry.pk
        except Watchlist.DoesNotExist:
            return None


class MemberSerializer(serializers.ModelSerializer):
    """Serializer für Team Members"""

    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        fields = ["id", "username", "first_name", "last_name"]


class TeamSerializer(serializers.ModelSerializer):
    """Serializer für Teams."""

    members = MemberSerializer(many=True, read_only=True)
    portfolio_value = serializers.SerializerMethodField()
    trades = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    edit_timeout = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "balance",
            "portfolio_value",
            "trades",
            "rank",
            "code",
            "members",
            "portfolio_history",
            "admin",
            "is_admin",
            "edit_timeout",
        ]
        read_only_fields = fields

    def get_portfolio_value(self, obj):
        return obj.get_portfolio_value()

    def get_trades(self, obj):
        return Transaction.objects.filter(team=obj).count()

    def get_admin(self, obj):
        try:
            return obj.team_admin.user.username
        except AttributeError:
            return None

    def get_is_admin(self, obj):
        return self.context["request"].user.profile == obj.team_admin

    def get_edit_timeout(self, obj):
        return timedelta(minutes=30) - (timezone.now() - obj.last_edited)


class TeamUpdateSerializer(serializers.ModelSerializer):
    """Serializer für die Aktualisierung von Teams."""

    name = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Team.objects.all(), message="Teamname ist bereits vergeben."
            )
        ],
        min_length=3,
        max_length=20,
        required=False,
    )
    admin = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        required=False,
    )

    class Meta:
        model = Team
        fields = ["name", "admin"]

    def validate(self, attrs):
        if self.instance.team_admin != self.context["request"].user.profile:
            raise serializers.ValidationError(
                "Nur der Team Admin kann Änderungen vornehmen."
            )

        if self.instance.last_edited + timedelta(minutes=30) > timezone.now():
            raise serializers.ValidationError(
                "Du kannst nur alle 30 Minuten Änderungen vornehmen."
            )
        return attrs

    def validate_admin(self, value):
        if value not in self.instance.members.all():
            raise serializers.ValidationError("Der Admin muss Mitglied des Teams sein.")
        return value

    def update(self, instance, validated_data):
        new_admin = validated_data.get("admin")
        if new_admin:
            instance.team_admin = new_admin

        instance.last_edited = timezone.now()
        instance.save()
        return super().update(instance, validated_data)


class TeamRankingSerializer(serializers.ModelSerializer):
    """Serializer für die Rangliste der Teams."""

    total_balance = serializers.FloatField()
    rank = serializers.IntegerField(read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    stocks = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ("id", "name", "total_balance", "rank", "members", "stocks")

    def get_stocks(self, obj):
        stocks = obj.holdings.filter(amount__gt=0)
        return [{"id": stock.stock.id, "name": stock.stock.name} for stock in stocks]


class StockInfoSerializer(serializers.ModelSerializer):
    """Serializer für Aktieninformationen."""

    class Meta:
        model = Stock
        fields = ["id", "name", "ticker", "current_price"]


class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer für die Watchlist."""

    stock = StockInfoSerializer(read_only=True)

    class Meta:
        model = Watchlist
        fields = ["id", "stock", "note", "date"]
        read_only_fields = ["date"]


class WatchlistCreateSerializer(serializers.ModelSerializer):
    """Serializer für die Erstellung von Watchlist-Einträgen."""

    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())

    class Meta:
        model = Watchlist
        fields = ["id", "stock", "note"]

    def validate(self, data):
        team = self.context["request"].user.profile.team
        stock = data["stock"]
        if Watchlist.objects.filter(team=team, stock=stock).exists():
            raise serializers.ValidationError("Stock is already in the watchlist.")
        return data


class WatchlistUpdateSerializer(serializers.ModelSerializer):
    """Serializer zum Aktualisieren der Beschreibung eines Watchlist-Eintrags."""

    class Meta:
        model = Watchlist
        fields = ["note"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer."""

    token = serializers.UUIDField(write_only=True)
    team_code = serializers.CharField(
        max_length=8, required=False, allow_blank=True, write_only=True
    )
    team_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    join_team = serializers.BooleanField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        min_length=3,
        max_length=20,
    )
    first_name = serializers.CharField(min_length=3, max_length=20)
    last_name = serializers.CharField(min_length=3, max_length=20)
    password = serializers.CharField(min_length=8, max_length=30)

    class Meta:
        model = User
        fields = [
            "token",
            "email",
            "first_name",
            "last_name",
            "username",
            "password",
            "team_code",
            "team_name",
            "join_team",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, password):
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError(
                "Das Passwort muss mindestens eine Zahl enthalten."
            )
        if not any(char.isalpha() for char in password):
            raise serializers.ValidationError(
                "Das Passwort muss mindestens einen Buchstaben enthalten."
            )
        return password

    def validate_token(self, token):
        try:
            RegistrationRequest.objects.get(activation_token=token)
        except RegistrationRequest.DoesNotExist:
            raise serializers.ValidationError("Dieses Token ist ungültig.")
        return token

    def validate_team_code(self, team_code):
        join_team = self.initial_data.get("join_team")

        if not join_team:
            return team_code
        if not team_code:
            raise serializers.ValidationError("Bitte geben Sie einen Teamcode ein.")
        if join_team and not team_code:
            raise serializers.ValidationError("Bitte geben Sie einen Teamcode ein.")
        if not team_code:
            return team_code
        try:
            team = Team.objects.get(code=team_code)
        except Team.DoesNotExist:
            raise serializers.ValidationError("Dieser Teamcode ist ungültig.")
        if team.members.count() >= 4:
            raise serializers.ValidationError("Dieses Team ist bereits voll.")
        return team_code

    def validate_team_name(self, team_name):
        join_team = self.initial_data.get("join_team")

        if join_team:
            return team_name
        if not team_name:
            raise serializers.ValidationError("Bitte geben Sie einen Teamnamen ein.")
        if Team.objects.filter(name=team_name).exists():
            raise serializers.ValidationError("Dieser Teamname ist bereits vergeben.")
        return team_name

    def validate(self, data):
        token = data["token"]
        registration_request = RegistrationRequest.objects.get(activation_token=token)
        if registration_request.email != data["email"]:
            raise serializers.ValidationError(
                "Diese E-Mail-Adresse wurde nicht mit diesem Token registriert."
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Erstellt einen neuen Benutzer."""
        token = validated_data.pop("token")
        team_code = validated_data.pop("team_code", None)
        team_name = validated_data.pop("team_name", None)
        join_team = validated_data.pop("join_team")

        user = User.objects.create_user(**validated_data)

        if join_team:
            team = Team.objects.get(code=team_code)
        else:
            team = Team.objects.create(name=team_name)

        user_profile = user.profile
        user_profile.team = team
        user_profile.save()

        registration_request = RegistrationRequest.objects.get(activation_token=token)
        registration_request.activated = True
        registration_request.user = user
        registration_request.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer."""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer für Benutzerprofile."""

    user = UserSerializer()
    team = serializers.CharField(source="team.name")
    edit_timeout = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["user", "team", "edit_timeout"]

    def get_edit_timeout(self, obj):
        return timedelta(minutes=30) - (timezone.now() - obj.last_edited)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a UserProfile."""

    email = serializers.EmailField(
        required=False,
    )
    username = serializers.CharField(
        min_length=3,
        max_length=20,
        required=False,
    )
    first_name = serializers.CharField(min_length=3, max_length=20, required=False)
    last_name = serializers.CharField(min_length=3, max_length=20, required=False)

    class Meta:
        model = UserProfile
        fields = ["email", "username", "first_name", "last_name"]

    def validate_username(self, value):
        if (
            User.objects.filter(username=value)
            .exclude(pk=self.instance.user.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                "Dieser Benutzername ist bereits vergeben."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.user.pk).exists():
            raise serializers.ValidationError(
                "Diese E-Mail-Adresse ist bereits registriert."
            )
        return value

    def validate(self, data):
        last_edited = self.instance.last_edited
        if last_edited and timezone.now() - last_edited < timedelta(minutes=30):
            raise serializers.ValidationError(
                "Sie können Ihr Profil nur alle 30 Minuten bearbeiten."
            )

        return data

    def update(self, instance, validated_data):
        user = instance.user
        if "username" in validated_data:
            user.username = validated_data.pop("username")
        if "email" in validated_data:
            user.email = validated_data.pop("email")
        if "first_name" in validated_data:
            user.first_name = validated_data.pop("first_name")
        if "last_name" in validated_data:
            user.last_name = validated_data.pop("last_name")
        user.save()
        return super().update(instance, validated_data)


class StockHoldingSerializer(serializers.ModelSerializer):
    """Serializer für Aktienbestände."""

    stock = StockInfoSerializer(read_only=True)

    class Meta:
        model = StockHolding
        fields = ["id", "stock", "amount"]


class TransactionListSerializer(serializers.ModelSerializer):
    """Serializer für die Liste der Transaktionen."""

    stock = StockInfoSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = Transaction
        fields = [
            "id",
            "stock",
            "status",
            "transaction_type",
            "amount",
            "price",
            "fee",
            "total_price",
            "description",
            "date",
        ]

    def get_total_price(self, obj):
        """Calculates the total price of the transaction, by using the model method."""
        return obj.get_total_price()


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer zum Aktualisieren der Beschreibung."""

    class Meta:
        model = Transaction
        fields = ["description"]


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer für das Erstellen von Transaktionen."""

    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())
    description = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.IntegerField(min_value=1)
    transaction_type = serializers.ChoiceField(
        choices=Transaction.TRANSACTION_TYPE_CHOICES
    )

    class Meta:
        model = Transaction
        fields = ["stock", "transaction_type", "amount", "description"]

    def validate_amount(self, amount):
        """Validiert die Anzahl der Aktien."""
        if amount <= 0:
            raise serializers.ValidationError("Die Anzahl muss größer als 0 sein")
        return amount

    def validate(self, data):
        """Validiert die Transaktionsdaten."""
        team = self.context["request"].user.profile.team
        stock = data["stock"]
        amount = data["amount"]
        transaction_type = data["transaction_type"]

        if transaction_type == "buy":
            price = amount * stock.current_price + stock.calculate_fee(amount)
            if team.balance < price:
                raise serializers.ValidationError("Nicht genügend Guthaben.")

        else:
            try:
                stock_holding = StockHolding.objects.get(team=team, stock=stock)
                if stock_holding.amount < amount:
                    raise serializers.ValidationError("Nicht genügend Aktien im Depot.")

            except StockHolding.DoesNotExist:
                raise serializers.ValidationError(
                    "Sie besitzen keine Aktien dieses Typs."
                )

        return data


class StockAnalysisSerializer(serializers.Serializer):
    """Serializer for stock analysis data."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    ticker = serializers.CharField()
    total_profit = serializers.DecimalField(max_digits=20, decimal_places=2)
    current_holding = serializers.DecimalField(max_digits=20, decimal_places=2)


class ValidateFieldSerializer(serializers.Serializer):
    """Serializer for validating fields"""

    field = serializers.CharField(required=True)
    value = serializers.CharField(required=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Dieser Benutzername existiert bereits.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Das Passwort muss mindestens 8 Zeichen lang sein."
            )
        elif len(value) > 30:
            raise serializers.ValidationError(
                "Das Passwort kann maximal 30 Zeichen lang sein."
            )
        elif not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Das Passwort muss mindestens eine Zahl enthalten."
            )
        elif not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                "Das Passwort muss mindestens einen Buchstaben enthalten."
            )
        return value

    def validate_team_code(self, value):
        try:
            team = Team.objects.get(code=value)
            if team.members.count() >= 4:
                raise serializers.ValidationError("Das Team ist bereits voll.")
            return {"valid": True, "team_name": team.name}
        except Team.DoesNotExist:
            raise serializers.ValidationError("Ungültiger Teamcode.")

    def validate_team_name(self, value):
        if Team.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Ein Team mit diesem Namen existiert bereits."
            )
        return value
