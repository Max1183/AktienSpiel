from django.contrib.auth.models import User
from rest_framework import serializers
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
from stocks.transactions import execute_transaction


def calculate_fee(current_price, amount):
    return max(15, int(float(current_price * amount) * 0.001))


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        return token


class TeamRankingSerializer(serializers.ModelSerializer):
    total_balance = serializers.FloatField()
    rank = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "total_balance", "rank")


class RegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationRequest
        fields = ["email"]

    def create(self, validated_data):
        email = validated_data["email"]

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {
                    "detail": [
                        f"Ein Benutzer mit dieser E-Mail-Adresse {email} existiert bereits."
                    ]
                }
            )
        else:
            if not RegistrationRequest.objects.filter(email=email).exists():
                return super().create(validated_data)
            else:
                raise serializers.ValidationError(
                    {
                        "detail": [
                            f"Eine Registrierungsanfrage für {email} existiert bereits."
                        ]
                    }
                )


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer."""

    token = serializers.UUIDField(write_only=True)
    first_name = serializers.CharField(max_length=20, write_only=True)
    last_name = serializers.CharField(max_length=20, write_only=True)
    team_code = serializers.CharField(max_length=8, required=False, allow_blank=True)
    team_name = serializers.CharField(required=False, allow_blank=True)
    join_team = serializers.BooleanField(write_only=True)

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

    def validate(self, data):  # noqa: C901
        """Validiert die Eingaben."""
        try:
            registration_request = RegistrationRequest.objects.get(
                activation_token=data["token"]
            )
        except RegistrationRequest.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": ["Dieses Token ist ungültig."]}
            )

        if registration_request.email != data["email"]:
            raise serializers.ValidationError(
                {
                    "detail": [
                        "Diese E-Mail-Adresse wurde nicht mit diesem Token registriert."
                    ]
                }
            )

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"detail": ["Diese E-Mail-Adresse ist bereits registriert."]}
            )

        if len(data["first_name"]) < 3 or len(data["first_name"]) > 20:
            raise serializers.ValidationError(
                {"detail": ["Der Vorname muss zwischen 3 und 20 Zeichen lang sein."]}
            )

        if len(data["last_name"]) < 3 or len(data["last_name"]) > 20:
            raise serializers.ValidationError(
                {"detail": ["Der Nachname muss zwischen 3 und 20 Zeichen lang sein."]}
            )

        if len(data["username"]) < 3 or len(data["username"]) > 20:
            raise serializers.ValidationError(
                {"detail": ["Der Nutzername muss zwischen 3 und 20 Zeichen lang sein."]}
            )

        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                {"detail": ["Dieser Nutzername ist bereits vergeben."]}
            )

        if len(data["password"]) < 8 or len(data["password"]) > 20:
            raise serializers.ValidationError(
                {"detail": ["Das Passwort muss zwischen 8 und 20 Zeichen lang sein."]}
            )

        if not any(char.isdigit() for char in data["password"]):
            raise serializers.ValidationError(
                {"detail": ["Das Passwort muss mindestens eine Zahl enthalten."]}
            )

        if not any(char.isalpha() for char in data["password"]):
            raise serializers.ValidationError(
                {
                    "detail": [
                        "Das Passwort muss mindestens einen Großbuchstaben enthalten."
                    ]
                }
            )

        if data["join_team"]:
            if data["team_code"] == "":
                raise serializers.ValidationError(
                    {"detail": ["Bitte geben Sie einen Teamcode ein."]}
                )
            try:
                team = Team.objects.get(code=data["team_code"])
            except Team.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": ["Dieser Teamcode ist ungültig."]}
                )
            if team.members.count() >= 4:
                raise serializers.ValidationError(
                    {"detail": ["Dieses Team ist bereits voll."]}
                )

        else:
            if data["team_name"] == "":
                raise serializers.ValidationError(
                    {"detail": ["Bitte geben Sie einen Teamnamen ein."]}
                )
            if Team.objects.filter(name=data["team_name"]).exists():
                raise serializers.ValidationError(
                    {"detail": ["Dieser Teamname ist bereits vergeben."]}
                )

        return data

    def create(self, validated_data):
        """Erstellt einen neuen Benutzer."""
        token = validated_data.pop("token")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        team_code = validated_data.pop("team_code", None)
        team_name = validated_data.pop("team_name", None)
        join_team = validated_data.pop("join_team")

        user = User.objects.create_user(**validated_data)

        if join_team:
            team = Team.objects.get(code=team_code)
        else:
            team = Team.objects.create(
                name=team_name,
            )

        user_profile = user.profile
        user_profile.team = team
        user_profile.first_name = first_name
        user_profile.last_name = last_name
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
        fields = ["id", "username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer für Benutzerprofile."""

    user = UserSerializer()
    team_name = serializers.CharField(source="team.name")

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "user", "team_name"]


class MemberSerializer(serializers.ModelSerializer):
    """Serializer für Team Members"""

    name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "name"]

    def get_name(self, obj):
        return obj.user.username


class TeamSerializer(serializers.ModelSerializer):
    """Serializer für Teams."""

    members = MemberSerializer(many=True, read_only=True)
    portfolio_value = serializers.SerializerMethodField()
    trades = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "balance",
            "portfolio_value",
            "trades",
            "code",
            "members",
        ]
        read_only_fields = fields

    def get_portfolio_value(self, obj):
        return float(obj.portfolio_value().replace("€", ""))

    def get_trades(self, obj):
        return Transaction.objects.filter(team=obj).count()


class HistorySerializer(serializers.ModelSerializer):
    """Serializer für Aktienhistorie."""

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
        read_only_fields = fields

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


class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer für die Watchlist."""

    stock = StockSerializer(read_only=True)

    class Meta:
        model = Watchlist
        fields = ["id", "team", "stock", "note", "date"]
        read_only_fields = ["team"]


class WatchlistCreateSerializer(serializers.ModelSerializer):
    """Serializer für die Erstellung von Watchlist-Einträgen."""

    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())

    class Meta:
        model = Watchlist
        fields = ["stock", "note"]


class WatchlistUpdateSerializer(serializers.ModelSerializer):
    """Serializer zum Aktualisieren der Beschreibung eines Watchlist-Eintrags."""

    class Meta:
        model = Watchlist
        fields = ["note"]


class StockHoldingSerializer(serializers.ModelSerializer):
    """Serializer für Aktienbestände."""

    stock = StockSerializer(read_only=True)

    class Meta:
        model = StockHolding
        fields = ["id", "stock", "amount"]
        read_only_fields = fields


class TransactionListSerializer(serializers.ModelSerializer):
    """Serializer für die Liste der Transaktionen."""

    stock = StockSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

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
        read_only_fields = [
            "id",
            "stock",
            "status",
            "transaction_type",
            "amount",
            "price",
            "fee",
            "total_price",
            "date",
        ]

    def get_total_price(self, obj):
        return float(obj.total_price().replace("€", ""))


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer zum Aktualisieren der Beschreibung."""

    class Meta:
        model = Transaction
        fields = ["description"]


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer für das Erstellen von Transaktionen."""

    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Transaction
        fields = ["stock", "transaction_type", "amount", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context["request"].method == "GET":
            self.fields["stock"].read_only = True

    def validate(self, data):
        """Validiert die Transaktionsdaten."""
        team = self.context["request"].user.profile.team
        stock = data["stock"]
        amount = data["amount"]
        transaction_type = data["transaction_type"]

        if amount <= 0:
            raise serializers.ValidationError({"detail": ["Ungültige Anzahl."]})

        if transaction_type == "buy":
            price = amount * stock.current_price + calculate_fee(
                stock.current_price, amount
            )
            if team.balance < price:
                raise serializers.ValidationError(
                    {"detail": ["Nicht genügend Guthaben."]}
                )

        elif transaction_type == "sell":
            try:
                stock_holding = StockHolding.objects.get(team=team, stock=stock)
                if stock_holding.amount < amount:
                    raise serializers.ValidationError(
                        {"detail": ["Nicht genügend Aktien im Depot."]}
                    )

            except StockHolding.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": ["Sie besitzen keine Aktien dieses Typs."]}
                )

        else:
            raise serializers.ValidationError(
                {"detail": ["Ungültiger Transaktionstyp."]}
            )

        return data

    def create(self, validated_data):
        """Erstellt eine neue Transaktion."""
        team = self.context["request"].user.profile.team
        validated_data["team"] = team
        validated_data["price"] = validated_data["stock"].current_price
        fee = calculate_fee(validated_data["price"], validated_data["amount"])
        validated_data["fee"] = fee

        transaction = Transaction.objects.create(**validated_data)
        execute_transaction(transaction)
        return transaction


class AnalysisSerializer(serializers.Serializer):
    """Serializer für die Analyse der Aktien."""

    stock_name = serializers.CharField(source="stock.name")
    stock_ticker = serializers.CharField(source="stock.ticker")
    total_profit = serializers.DecimalField(max_digits=20, decimal_places=2)

    def calculate_profit(self, transactions, current_price):
        """Berechnet den Gesamtgewinn oder -verlust für eine Aktie basierend auf den Transaktionen."""
        total_profit = 0
        for transaction in transactions:
            if transaction.transaction_type == "buy":
                total_profit -= transaction.amount * transaction.price + transaction.fee
            elif transaction.transaction_type == "sell":
                total_profit += transaction.amount * transaction.price - transaction.fee

        return total_profit

    def to_representation(self, team):
        """Erstellt die serialisierte Darstellung für ein Team."""
        stock_profits = []
        unique_stocks = set(
            Transaction.objects.filter(team=team).values_list("stock", flat=True)
        )

        for stock_id in unique_stocks:
            stock = Stock.objects.get(id=stock_id)
            transactions = Transaction.objects.filter(team=team, stock=stock)
            total_profit = self.calculate_profit(transactions, stock.current_price)

            try:
                stock_holding = StockHolding.objects.get(team=team, stock=stock)
                total_profit += stock_holding.amount * stock.current_price
            except StockHolding.DoesNotExist:
                pass

            stock_profits.append(
                {
                    "id": stock.pk,
                    "name": stock.name,
                    "ticker": stock.ticker,
                    "total_profit": total_profit,
                }
            )

        return stock_profits
