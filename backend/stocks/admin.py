from django.contrib import admin

from .models import History, Stock


class HistoryInline(admin.TabularInline):
    model = History
    extra = 1
    readonly_fields = ["name", "period", "interval", "values"]


class StockAdmin(admin.ModelAdmin):
    inlines = [HistoryInline]
    fields = ["name", "ticker", "current_price"]
    list_display = ["name", "ticker", "current_price"]
    search_fields = ["name", "ticker"]
    readonly_fields = ["current_price"]


admin.site.register(Stock, StockAdmin)
