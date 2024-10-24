from django.contrib.auth.models import User
from rest_framework import serializers

from stocks.models import History, Stock, StockHolding, Transaction
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


class HistorySerializer(serializers.ModelSerializer):
    """Serializer für Aktienhistorie."""

    class Meta:
        model = History
        fields = ["id", "name", "values"]
        read_only_fields = fields


class StockSerializer(serializers.ModelSerializer):
    """Serializer für Aktien."""

    history_entries = HistorySerializer(many=True, read_only=True)

    class Meta:
        model = Stock
        fields = ["id", "name", "ticker", "current_price", "history_entries"]
        read_only_fields = fields


class StockHoldingSerializer(serializers.ModelSerializer):
    """Serializer für Aktienbestände."""

    stock = StockSerializer(read_only=True)

    class Meta:
        model = StockHolding
        fields = ["id", "stock", "amount"]
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer für Transaktionen."""

    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())

    class Meta:
        model = Transaction
        fields = ["stock", "transaction_type", "amount"]

    def validate(self, data):
        """Validiert die Transaktionsdaten."""
        team = self.context["request"].user.profile.team
        stock = data["stock"]
        amount = data["amount"]
        transaction_type = data["transaction_type"]

        if amount <= 0:
            raise serializers.ValidationError(
                {"amount": "Die Menge muss positiv sein."}
            )

        if transaction_type == "buy":
            price = amount * stock.current_price + calculate_fee(
                stock.current_price, amount
            )
            if team.balance < price:
                raise serializers.ValidationError("Nicht genügend Guthaben.")

        elif transaction_type == "sell":
            try:
                stock_holding = StockHolding.objects.get(team=team, stock=stock)
                if stock_holding.amount < amount:
                    raise serializers.ValidationError("Nicht genügend Aktien im Depot.")

            except StockHolding.DoesNotExist:
                raise serializers.ValidationError(
                    "Sie besitzen keine Aktien dieses Typs."
                )

        else:
            raise serializers.ValidationError(
                {"transaction_type": "Ungültiger Transaktionstyp."}
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
