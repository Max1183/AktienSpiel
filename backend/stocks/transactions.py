from django.db import transaction

from .models import StockHolding, Transaction


@transaction.atomic()
def execute_transaction(ta: Transaction):
    team = ta.team
    amount = ta.amount

    if ta.transaction_type == "buy":
        total_price = amount * ta.price + ta.fee

        if total_price > team.balance:
            transaction_error(ta,
                              "Insufficient funds to complete the purchase.")

        else:
            team.update_balance(-total_price)

            stock_holding, created = StockHolding.objects.update_or_create(
                team=team,
                stock=ta.stock,
            )

            stock_holding.adjust_amount(amount)

    elif ta.transaction_type == "sell":
        try:
            stock_holding = StockHolding.objects.get(team=team, stock=ta.stock)

            if amount > stock_holding.amount:
                transaction_error(
                    ta,
                    f"You only have {stock_holding.amount} shares of {ta.stock.name} available to sell."
                )

            else:
                team.update_balance(amount * ta.price - ta.fee)
                stock_holding.adjust_amount(-amount)

        except StockHolding.DoesNotExist:
            transaction_error(ta, "You don't have stocks of this type!")

    else:
        transaction_error(ta, "Unsupported transaction type")

    if ta.status == "open":
        ta.status = "closed"
    ta.save()


def transaction_error(transaction: Transaction, error):
    transaction.status = "error"
    transaction.description += "\nTransaction couldn't be completed due to the following problem:\n" + error
