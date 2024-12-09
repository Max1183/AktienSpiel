import json
import logging
import queue
import threading
import time

import yfinance as yf
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import OperationalError

from ...models import History, Stock

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()  # Handler für die Konsolenausgabe
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)  # Formatierer erstellen
handler.setFormatter(formatter)
logger.addHandler(handler)

DATA_DIR = "Data/"


class Command(BaseCommand):
    help = "Updates stock prices and history periodically."  # Noqa: A003

    def handle(self, *args, **options):
        load_stock_data()
        updater = StockUpdater()
        updater.start()


class StockUpdater:
    def __init__(self, num_workers=16, update_interval=600):
        self.num_workers = num_workers
        self.update_interval = update_interval
        self.is_running = True
        self.history_intervals = {
            "Day": ["1d", "5m"],
            "5 Days": ["5d", "30m"],
            "Month": ["1mo", "90m"],
            "3 Months": ["3mo", "1d"],
            "Year": ["1y", "1wk"],
            "5 Years": ["5y", "1mo"],
        }
        self.stock_queue = queue.Queue()

    def start(self):
        yf.utils.get_json = lambda url, proxy=None, session=None: yf.utils._get_json(
            url, proxy, session, headers={"User-Agent": "Mozilla/5.0"}
        )
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self.worker_loop)
            worker.daemon = False
            worker.start()

        threading.Thread(target=self.queue_stocks, daemon=True).start()

    def queue_stocks(self):
        while self.is_running:
            start_time = time.time()

            try:
                logger.info("Updating all stocks...")
                stocks = Stock.objects.all()
                for stock in stocks:
                    self.stock_queue.put(stock)

                self.stock_queue.join()
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Updated all stocks in {elapsed_time:.2f} seconds")

            except OperationalError as e:
                logger.error(f"Database error: {e}")
                time.sleep(60)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

            time.sleep(self.update_interval)

    def worker_loop(self):
        while self.is_running:
            try:
                stock = self.stock_queue.get(timeout=1)
                self.update_stock(stock)
                self.stock_queue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Worker error: {e}")

    def update_stock(self, stock):
        ticker = stock.ticker
        try:
            ticker_data = yf.Ticker(ticker)

            current_price = ticker_data.info.get("currentPrice")
            if current_price is None:
                logger.warning(f"No price data found for {ticker}")
                return

            with transaction.atomic():
                stock.current_price = current_price
                stock.save()

            for name, (period, interval) in self.history_intervals.items():
                try:
                    valid_periods = ticker_data.history_metadata.get("validRanges")
                    if period not in valid_periods:
                        continue

                    hist = ticker_data.history(period=period, interval=interval)
                    values = [float(value["Close"]) for index, value in hist.iterrows()]

                    with transaction.atomic():
                        (
                            history,
                            created,
                        ) = History.objects.select_for_update().get_or_create(
                            stock=stock,
                            name=name,
                            period=period,
                            interval=interval,
                        )

                        history.values = values
                        history.save()

                except Exception as e:
                    logger.error(
                        f"Error updating history for {stock.name} ({name}): {e}"
                    )

        except (Stock.DoesNotExist, Exception) as e:
            logger.error(f"Could not update {ticker}: {e}")

    def stop(self):
        self.is_running = False


def load_stock_data():
    with open(f"{DATA_DIR}companies.json", "r") as file:
        companies = json.load(file)

    if len(companies) == len(Stock.objects.all()):
        logger.info("Daten wurden bereits geladen.")
        return

    try:
        with transaction.atomic():
            Stock.objects.all().delete()
            History.objects.all().delete()

            for ticker, name in companies.items():
                Stock.objects.create(name=name, ticker=ticker, current_price=0)
        logger.info("Daten wurden erfolgreich geladen.")

    except Exception as e:
        logger.error(f"Fehler beim Laden der Daten: {e}")
