import os
import threading

from django.apps import AppConfig


class StocksConfig(AppConfig):
    name = "stocks"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import stocks.signals  # noqa F401

        run_once = os.environ.get("CMDLINERUNNER_RUN_ONCE")
        if run_once is not None:
            return
        os.environ["CMDLINERUNNER_RUN_ONCE"] = "True"

        from .tasks import stock_updater_loop

        thread = threading.Thread(target=stock_updater_loop, daemon=True)

        if not thread.is_alive():
            thread.start()
