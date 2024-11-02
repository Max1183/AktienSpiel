from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stocks import views as stock_views

from . import views

router = DefaultRouter()
router.register(r"stocks", views.StockViewSet, basename="stock")
router.register(r"stockholdings", views.StockHoldingViewSet, basename="stockholding")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")

urlpatterns = [
    path("search/", stock_views.search_stocks, name="stock-search"),
    path("", include(router.urls)),
    path("users/create/", views.CreateUserView.as_view(), name="create-user"),
    path("team/", views.TeamViewSet.as_view(), name="team-detail"),
]
