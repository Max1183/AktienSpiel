from django.apps import AppConfig


class StocksConfig(AppConfig):
    name = "stocks"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import stocks.signals  # noqa F401
