from django.contrib.auth.models import User

from rest_framework import serializers

from stocks.models import History, Stock, StockHolding


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
