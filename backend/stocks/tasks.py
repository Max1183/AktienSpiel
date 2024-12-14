import json
import time

import numpy
import yfinance as yf
from django.db import transaction

from stocks.models import History, Stock

DATA_DIR = "Data/"
HISTORY_INTERVALS = {
    "Day": ["1d", "5m"],
    "5 Days": ["5d", "30m"],
    "Month": ["1mo", "90m"],
    "3 Months": ["3mo", "1d"],
    "Year": ["1y", "1wk"],
    "5 Years": ["5y", "1mo"],
}


def load_stocks():
    with open(f"{DATA_DIR}companies.json", "r") as file:
        companies = json.load(file)

    if len(companies) == len(Stock.objects.all()):
        print("All Stocks are already loaded.")
        return

    print("Loading Stocks...")

    try:
        for ticker, name in companies.items():
            with transaction.atomic():
                stock, created = Stock.objects.get_or_create(
                    name=name,
                    ticker=ticker,
                )

                if created:
                    stock.current_price = 0
                    stock.save()
                    print(f"Added {stock.name} ({stock.ticker})")

        print("Successfully loaded all stocks.")

    except Exception as e:
        print(f"Error loading stocks: {e}")


def stock_updater_loop():
    print("Starting stock updater loop...")
    time.sleep(5)
    load_stocks()

    while True:
        time_taken = stock_updater()
        time.sleep(3600 - time_taken)


def stock_updater():
    start_time = time.time()
    print("Starting stock updater...")
    stocks = Stock.objects.all()

    tickers = list(stock.ticker for stock in stocks)
    errors = []

    for name, (period, interval) in HISTORY_INTERVALS.items():
        data = yf.download(tickers, period=period, interval=interval)

        if not data.empty:
            for stock in stocks:
                try:
                    if stock.ticker in data["Close"].columns:
                        values = data["Close"][stock.ticker].values.tolist()
                        values = [value for value in values if not numpy.isnan(value)]

                        if period == "1d":
                            current_price = values[-1]
                            if not isinstance(current_price, float):
                                errors.append(stock.ticker)
                                continue

                            with transaction.atomic():
                                stock.current_price = current_price
                                stock.save()

                        with transaction.atomic():
                            history, created = History.objects.get_or_create(
                                stock=stock,
                                name=name,
                                period=period,
                                interval=interval,
                            )

                            if not isinstance(values, list) or len(values) == 0:
                                errors.append(stock.ticker)
                                continue

                            history.values = values
                            history.save()

                    else:
                        errors.append(stock.ticker)

                except Exception:
                    errors.append(stock.ticker)
        else:
            print(f"No data available for period `{period}`.")
            break

        print(
            f"Updated alls stocks for period `{period}`. {len(errors)} Errors: {errors}"
        )

        if len(errors) > 50:
            print("Too many errors. Stopping...")
            break
        errors = []

    time_taken = time.time() - start_time
    print(f"Updated all stocks in {time_taken} seconds.")
    return time_taken