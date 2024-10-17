from django.urls import path

from stocks import views as stock_views

from . import views

urlpatterns = [
    path("search/", stock_views.search_stocks, name="stock-search"),
    path("stocks/", views.StockViewSet.as_view(), name="stock-list"),
    path("stocks/<int:pk>/",
         views.StockDetailView.as_view(),
         name="stock-detail"),
    path("transactions/create/",
         views.TransactionCreateView.as_view(),
         name="transaction-create"),
]
