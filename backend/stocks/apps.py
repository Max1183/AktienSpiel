from django.apps import AppConfig


class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocks'

    def ready(self):
        import stocks.tasks  # noqa F401
        import stocks.signals  # noqa F401
