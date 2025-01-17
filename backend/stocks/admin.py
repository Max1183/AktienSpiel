from django.contrib import admin

from .models import (
    History,
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
    UserProfile,
    Watchlist,
)


class HistoryInline(admin.TabularInline):
    model = History
    readonly_fields = ["name", "period", "interval", "values"]

    def has_add_permission(self, request, obj=None):
        return False


class StockHoldingInline(admin.TabularInline):
    model = StockHolding
    extra = 0


class WatchlistInline(admin.TabularInline):
    model = Watchlist
    extra = 0


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    readonly_fields = ["user", "team"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "activated", "user")
    readonly_fields = ["email", "created_at", "activated"]
    search_fields = ["email", "user"]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    inlines = [HistoryInline]
    list_display = ["name", "ticker", "current_price"]
    search_fields = ["name", "ticker"]
    readonly_fields = ["current_price"]
    fields = ["name", "ticker", "current_price"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline, StockHoldingInline, WatchlistInline]
    list_display = ["name", "team_member_count", "portfolio_value", "rank"]
    search_fields = ["name"]
    readonly_fields = ["team_member_count", "portfolio_value", "code"]
    fields = ["name", "balance", "portfolio_value", "code", "portfolio_history"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "team"]
    search_fields = ["user__username", "user__email"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "team",
        "stock",
        "status",
        "transaction_type",
        "amount",
        "formatted_total_price",
    ]
    list_filter = ["status", "transaction_type", "team", "stock"]
    ordering = ("-date",)
    search_fields = ["stock__name", "stock__ticker", "team__name"]
    readonly_fields = [
        "team",
        "stock",
        "transaction_type",
        "amount",
        "price",
        "fee",
        "date",
    ]
    fields = [
        "team",
        "stock",
        "status",
        "transaction_type",
        "amount",
        "price",
        "fee",
        "date",
    ]
