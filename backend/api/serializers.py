from django.contrib.auth.models import User
from rest_framework import serializers

from stocks.models import History, Stock, StockHolding, Team, Transaction, Watchlist
from stocks.transactions import execute_transaction


def calculate_fee(current_price, amount):
    return max(15, int(float(current_price * amount) * 0.001))


class UserSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Erstellt einen neuen Benutzer."""
        user = User.objects.create_user(**validated_data)
        return user


class TeamSerializer(serializers.ModelSerializer):
    """Serializer für Teams."""

    portfolio_value = serializers.SerializerMethodField()
    trades = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "balance", "portfolio_value", "trades"]
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
            return watchlist_entry.id
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
