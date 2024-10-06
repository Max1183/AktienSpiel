import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from django.core.signals import request_started
from django.db import transaction
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
    hist = ticker_data.history(period=period, interval=interval)
    values = list(float(value['Close']) for index, value in hist.iterrows())

    with transaction.atomic():
        history, created = History.objects.select_for_update().get_or_create(
            stock=stock,
            name=name,
            period=period,
            interval=interval,
        )

        history.values = values
        history.save()

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


def update_stock_data(element, ticker, progress, total, lock):
    try:
        ticker_data = yf.Ticker(ticker)

        with transaction.atomic():
            stock = Stock.objects.select_for_update().get(pk=element)
            new_price = get_current_price(ticker_data.info, stock.name)

            if stock.current_price != new_price:
                print(
                    f"Preis für {stock.name} wurde von {stock.current_price} auf {new_price} aktualisiert."
                )

            stock.current_price = new_price
            stock.save()

        for history in stock.history_entries.all():
            update_history(ticker_data, stock, history.name,
                           (history.period, history.interval))

    except Stock.DoesNotExist:
        print(f"Aktie mit ID {element} nicht gefunden.")

    except Exception as e:
        print(f"Fehler beim Aktualisieren der Daten für {ticker}: {e}")

    finally:
        with lock:
            progress.value += 1
            aktueller_fortschritt = int(progress.value / total * 10) * 10
            if aktueller_fortschritt > progress.last_progress.value:
                print(f"Fortschritt: {aktueller_fortschritt}%")
                progress.last_progress.value = aktueller_fortschritt


def stock_updater():
    load_stock_data()
    time.sleep(2)

    import multiprocessing as mp
    while True:
        print("Daten werden aktualisiert...")
        start_time = time.time()
        stocks = Stock.objects.all()

        with mp.Manager() as manager:
            progress = manager.Value('i', 0)
            progress.last_progress = manager.Value('i', 0)
            lock = manager.Lock()
            total = len(stocks)

            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = [
                    executor.submit(update_stock_data, stock.id, stock.ticker,
                                    progress, total, lock) for stock in stocks
                ]

                for future in futures:
                    future.result()

        time_taken = int(time.time() - start_time)
        print(
            f"Daten wurden in {time_taken} Sekunden erfolgreich aktualisiert.")
        time.sleep(max(0, 60 - time_taken))


background_thread = threading.Thread(target=stock_updater, daemon=True)


@receiver(request_started)
def start_background_task(sender, **kwargs):
    if not background_thread.is_alive():
        background_thread.start()
