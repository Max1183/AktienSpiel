from django.contrib.auth.models import User

from rest_framework import serializers

from stocks.models import History, Stock, StockHolding, Transaction
from stocks.transactions import execute_transaction


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = History
        fields = ['id', 'name', 'values']
        read_only = True


class StockSerializer(serializers.ModelSerializer):
    history_entries = HistorySerializer(many=True, read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'name', 'ticker', 'current_price', 'history_entries']
        read_only = True


class StockHoldingSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockHolding
        fields = ['id', 'team', 'stock', 'amount']
        read_only = True


class TransactionSerializer(serializers.ModelSerializer):
    stock_id = serializers.IntegerField()

    class Meta:
        model = Transaction
        fields = ['stock_id', 'transaction_type', 'amount']

    def create(self, validated_data):
        team = self.context['request'].user.profile.team

        stock = Stock.objects.get(pk=validated_data.pop('stock_id'))
        amount = validated_data.pop('amount')
        price = stock.current_price
        fee = max(15, price * amount * 0.001)
        transaction_type = validated_data.pop('transaction_type')

        transaction = Transaction.objects.create(
            team=team,
            stock=stock,
            amount=amount,
            price=price,
            fee=fee,
            transaction_type=transaction_type)

        execute_transaction(transaction)

        return transaction
