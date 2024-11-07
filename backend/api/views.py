from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from stocks.models import Stock, StockHolding, Transaction

from .serializers import (
    StockHoldingSerializer,
    StockSerializer,
    TeamSerializer,
    TransactionCreateSerializer,
    TransactionListSerializer,
    TransactionUpdateSerializer,
    UserSerializer,
    WatchlistCreateSerializer,
    WatchlistSerializer,
    WatchlistUpdateSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """View zum Erstellen neuer Benutzer."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TeamViewSet(generics.RetrieveAPIView):
    """Viewset für Teams."""

    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile.team


class WatchlistList(viewsets.ReadOnlyModelViewSet):
    """Viewset für die Watchlist."""

    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.team.watchlist.all()


class WatchlistCreate(generics.CreateAPIView):
    """Viewset für das Erstellen einer Watchlist."""

    serializer_class = WatchlistCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(team=self.request.user.profile.team)
        else:
            print(serializer.errors)


class WatchlistUpdate(generics.UpdateAPIView):
    """Viewset für das Aktualisieren einer Watchlist."""

    serializer_class = WatchlistUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.team.watchlist.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        instance.note = serializer.validated_data.get("note", instance.note)
        instance.save()


class WatchlistDelete(generics.DestroyAPIView):
    """Viewset für das Löschen einer Watchlist."""

    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.team.watchlist.all()


class StockViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Viewset für Aktien Details."""

    serializer_class = StockSerializer
    queryset = Stock.objects.all()
    permission_classes = [IsAuthenticated]


class StockHoldingViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset für die Stock Holdings eines Teams (read-only)."""

    serializer_class = StockHoldingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StockHolding.objects.filter(
            team=self.request.user.profile.team
        ).select_related("team", "stock")


class TransactionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset zum Erstellen neuer Transaktionen."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return TransactionListSerializer
        elif self.action == "create":
            return TransactionCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return TransactionUpdateSerializer
        return TransactionListSerializer

    def get_queryset(self):
        return Transaction.objects.filter(team=self.request.user.profile.team)

    def perform_update(self, serializer):
        instance = self.get_object()
        instance.description = serializer.validated_data.get(
            "description", instance.description
        )
        instance.save()
