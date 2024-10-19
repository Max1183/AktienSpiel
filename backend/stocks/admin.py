from django.contrib import admin

from .models import History, Stock, StockHolding, Team, Transaction, UserProfile


class HistoryInline(admin.TabularInline):
    model = History
    extra = 0
    readonly_fields = ["name", "period", "interval", "values"]


class StockHoldingInline(admin.TabularInline):
    model = StockHolding
    extra = 0
    readonly_fields = ["stock", "amount"]


class UserProfileInLine(admin.StackedInline):
    model = UserProfile
    max_num = 0
    can_delete = False
    readonly_fields = ["user"]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    inlines = [HistoryInline]
    fields = ["name", "ticker", "current_price"]
    list_display = ["name", "ticker", "current_price"]
    search_fields = ["name", "ticker"]
    readonly_fields = ["current_price"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [UserProfileInLine, StockHoldingInline]
    fields = ["name", "team_member_count", "balance", "portfolio_value"]
    list_display = ["name", "team_member_count", "portfolio_value"]
    search_fields = ["name"]
    readonly_fields = ["balance", "team_member_count", "portfolio_value"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = ["user", "team"]
    list_display = ["user", "team"]
    search_fields = ["user"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "stock",
        "status",
        "transaction_type",
        "amount",
        "total_price",
    ]
    list_filter = ["status", "transaction_type", "team", "stock"]
    ordering = ("-date",)
    search_fields = ["stock", "transaction_type"]
    readonly_fields = [
        "team",
        "stock",
        "status",
        "transaction_type",
        "amount",
        "price",
        "total_price",
        "fee",
        "date",
    ]
