from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from stocks.models import StockHolding, Transaction


def calculate_stock_profit(transactions):
    """
    Calculates the total profit/loss for a stock based on a list of transactions and the current stock price.

    Args:
        transactions (list): A list of Transaction model instances related to a single stock.

    Returns:
        Decimal: The calculated total profit/loss.
    """
    total_profit = Decimal("0.00")
    for transaction1 in transactions:
        if transaction1.transaction_type == "buy":
            total_profit -= transaction1.amount * transaction1.price + transaction1.fee
        elif transaction1.transaction_type == "sell":
            total_profit += transaction1.amount * transaction1.price - transaction1.fee
    return total_profit


@transaction.atomic()
def execute_transaction(ta: Transaction):
    """Executes the transaction, and saves errors to the errors field."""
    if ta.status != "open":
        return

    team = ta.team
    amount = ta.amount
    stock = ta.stock
    try:
        if ta.transaction_type == "buy":
            total_price = amount * ta.price + ta.fee

            if total_price > team.balance:
                raise serializers.ValidationError("Nicht genügend Guthaben.")

            team.update_balance(-total_price)

            stock_holding, created = StockHolding.objects.update_or_create(
                team=team, stock=stock, defaults={"amount": 0}
            )
            stock_holding.adjust_amount(amount)

        elif ta.transaction_type == "sell":
            stock_holding = StockHolding.objects.get(team=team, stock=stock)
            if amount > stock_holding.amount:
                raise serializers.ValidationError(
                    f"Sie besitzen nur {stock_holding.amount} Aktien von {stock.name}."
                )
            team.update_balance(amount * ta.price - ta.fee)
            stock_holding.adjust_amount(-amount)
        else:
            raise serializers.ValidationError("Ungültiger Transaktionstyp.")
        ta.status = "closed"
        ta.save()
    except serializers.ValidationError as e:
        transaction_error(ta, str(e))


def transaction_error(ta: Transaction, error_message):
    """Saves an error to the error field of the transaction"""
    ta.status = "error"
    ta.errors = error_message
    ta.save()
