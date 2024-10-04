from django.contrib import admin

from .models import History, Stock


class HistoryInline(admin.TabularInline):
    model = History
    extra = 1
    readonly_fields = ["name", "period", "interval", "values"]


class StockAdmin(admin.ModelAdmin):
    inlines = [HistoryInline]
    fields = ["name", "ticker", "current_price"]
    list_display = ["name", "current_price"]
    search_fields = ["name"]
    readonly_fields = ["current_price"]


admin.site.register(Stock, StockAdmin)
