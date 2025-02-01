from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("token/", views.MyTokenObtainPairView.as_view(), name="get-token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", views.RegistrationRequestCreateView.as_view(), name="register"),
    path("stocks/<int:pk>/", views.StockDetailView.as_view(), name="stock-detail"),
    path("team/", views.TeamDetailView.as_view(), name="team-detail"),
    path("ranking/", views.TeamRankingListView.as_view(), name="ranking"),
    path(
        "watchlist/",
        views.WatchlistListView.as_view(),
        name="watchlist-list",
    ),
    path(
        "watchlist/create/",
        views.WatchlistCreateView.as_view(),
        name="watchlist-create",
    ),
    path(
        "watchlist/<int:pk>/update/",
        views.WatchlistUpdateView.as_view(),
        name="watchlist-update",
    ),
    path(
        "watchlist/<int:pk>/delete/",
        views.WatchlistDeleteView.as_view(),
        name="watchlist-delete",
    ),
    path("create-user/", views.CreateUserView.as_view(), name="create-user"),
    path("profile/", views.UserProfileDetailView.as_view(), name="user-profile"),
    path(
        "profile/update/",
        views.UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
    path("stockholdings/", views.StockHoldingListView.as_view(), name="stock-holdings"),
    path("transactions/", views.TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/create/",
        views.TransactionCreateView.as_view(),
        name="transaction-create",
    ),
    path(
        "transactions/<int:pk>/update/",
        views.TransactionUpdateView.as_view(),
        name="transaction-update",
    ),
    path("validate-form/", views.ValidateFormView.as_view(), name="validate-form"),
    path("analysis/", views.AnalysisView.as_view(), name="analysis"),
    path("search/", views.SearchStocksView.as_view(), name="stock-search"),
    path(
        "validate-token/<str:token>/",
        views.ValidateActivationTokenView.as_view(),
        name="validate-token",
    ),
]
