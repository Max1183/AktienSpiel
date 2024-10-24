import os
import threading

from django.apps import AppConfig

background_thread = None


class StocksConfig(AppConfig):
    name = "stocks"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import stocks.signals  # noqa F401

        from .tasks import stock_updater

        global background_thread
        background_thread = threading.Thread(target=stock_updater, daemon=True)

        current_settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
        alive = background_thread.is_alive()
        if current_settings_module != "your_project.settings.test" and not alive:
            background_thread.start()
            print("Background Thread started")
