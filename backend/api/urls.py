from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stocks import views as stock_views

from . import views

router = DefaultRouter()
router.register(r"stockholdings", views.StockHoldingViewSet, basename="stockholding")
router.register(r"transactions", views.TransactionViewSet, basename="transaction")

urlpatterns = [
    path("token/", views.MyTokenObtainPairView.as_view(), name="get_token"),
    path("register/", views.RegistrationRequestCreateView.as_view(), name="register"),
    path("stocks/<int:pk>/", views.StockDetailView.as_view(), name="stock-detail"),
    path("create-user/", views.CreateUserView.as_view(), name="create-user"),
    path("team/", views.TeamDetailView.as_view(), name="team-detail"),
    path("ranking/", views.TeamRankingListView.as_view(), name="ranking"),
    path("profile/", views.UserProfileViewSet.as_view(), name="user-profile"),
    path(
        "watchlist/",
        views.WatchlistList.as_view({"get": "list"}),
        name="watchlist-list",
    ),
    path("watchlist/create/", views.WatchlistCreate.as_view(), name="watchlist-create"),
    path(
        "watchlist/<int:pk>/", views.WatchlistUpdate.as_view(), name="watchlist-update"
    ),
    path(
        "watchlist/delete/<int:pk>/",
        views.WatchlistDelete.as_view(),
        name="watchlist-delete",
    ),
    path("validate-form/", views.ValidateFormView.as_view(), name="validate-form"),
    path("analysis/", views.AnalysisView.as_view(), name="analysis"),
    path("search/", stock_views.search_stocks, name="stock-search"),
    path("", include(router.urls)),
]
