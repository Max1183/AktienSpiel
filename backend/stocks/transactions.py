from django.db import transaction

from .models import StockHolding, Transaction


@transaction.atomic()
def execute_transaction(ta: Transaction):
    if ta.status != "open":
        return

    team = ta.team
    amount = ta.amount
    stock = ta.stock

    if ta.transaction_type == "buy":
        total_price = amount * ta.price + ta.fee

        if total_price > team.balance:
            transaction_error(ta, "Nicht genügend Guthaben.")
            return

        team.update_balance(-total_price)

        stock_holding, created = StockHolding.objects.update_or_create(
            team=team,
            stock=stock,
        )

        stock_holding.adjust_amount(amount)

    elif ta.transaction_type == "sell":
        try:
            stock_holding = StockHolding.objects.get(team=team, stock=stock)

        except StockHolding.DoesNotExist:
            transaction_error(ta, "Sie haben keine Aktien von diesem Unternehmen.")
            return

        if amount > stock_holding.amount:
            message = (
                f"Sie besitzen nur {stock_holding.amount} Aktien von {stock.name}."
            )
            transaction_error(ta, message)
            return

        team.update_balance(amount * ta.price - ta.fee)
        stock_holding.adjust_amount(-amount)

    else:
        transaction_error(ta, "Ungültiger Transaktionstyp.")
        return

    ta.status = "closed"
    ta.save()


def transaction_error(ta: Transaction, error_message):
    ta.status = "error"
    ta.description = f"{ta.description}\nFehler: {error_message}"
    ta.save()
