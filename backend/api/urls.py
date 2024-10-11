from django.urls import path

from stocks import views as stock_views

from . import views

urlpatterns = [
    path("stocks/", views.StockViewSet.as_view(), name="stocks"),
    path("search/", stock_views.search_stocks, name="search_stocks"),
]
