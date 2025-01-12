from decimal import Decimal


def calculate_stock_profit(transactions, current_price):
    """
    Calculates the total profit/loss for a stock based on a list of transactions and the current stock price.

    Args:
        transactions (list): A list of Transaction model instances related to a single stock.
        current_price (Decimal): The current market price of the stock.

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
