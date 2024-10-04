import json
import threading
import time

from django.core.signals import request_started
from django.dispatch import receiver

import yfinance as yf

from .models import History, Stock

DATA_DIR = "../Data/"


def get_current_price(info, name):
    current_price = info.get("currentPrice")
    if current_price is None:
        print(
            f"Konnte den aktuellen Preis für {name} nicht abrufen. Info: {info}"
        )
        return 0
    return current_price


def update_history(ticker_data, stock: Stock, name, times):
    period, interval = times

    stock.history_entries.filter(name=name).delete()

    hist = ticker_data.history(period=period, interval=interval)

    history = History.objects.create(
        stock=stock,
        name=name,
        period=period,
        interval=interval,
        values=list(float(value['Close']) for index, value in hist.iterrows()),
    )

    return history


def load_stock_data():
    with open(f"{DATA_DIR}companies.json", "r") as file:
        companies = json.load(file)

    if len(companies) == len(Stock.objects.all()):
        print("Daten wurden bereits geladen.")
        return
    print("Daten werden geladen...")

    with open(f"{DATA_DIR}histories.json", "r") as file:
        histories = json.load(file)

    Stock.objects.all().delete()
    History.objects.all().delete()

    for ticker, name in companies.items():
        stock = Stock.objects.create(name=name, ticker=ticker)

        ticker_data = yf.Ticker(stock.ticker)
        stock.current_price = get_current_price(ticker_data.info, stock.name)
        stock.save()

        for history_name, times in histories.items():
            update_history(ticker_data, stock, history_name, times)

        print(f"Daten für {stock.name} wurden erfolgreich geladen.")
    print("Daten wurden erfolgreich geladen.")


def update_stock_data(stock: Stock):
    try:
        ticker_data = yf.Ticker(stock.ticker)
        stock.current_price = get_current_price(ticker_data.info, stock.name)
        stock.save()

        for history in stock.history_entries.all():
            update_history(ticker_data, stock, history.name,
                           (history.period, history.interval))

    except Exception as e:
        print(f"Fehler beim Aktualisieren der Daten für {stock}: {e}")


def stock_updater():
    load_stock_data()
    while True:
        time.sleep(60)
        for stock in Stock.objects.all():
            update_stock_data(stock)

        print("Daten wurden erfolgreich aktualisiert.")


background_thread = threading.Thread(target=stock_updater, daemon=True)


@receiver(request_started)
def start_background_task(sender, **kwargs):
    if not background_thread.is_alive():
        background_thread.start()
