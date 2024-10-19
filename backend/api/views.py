from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from stocks.models import Stock, StockHolding

from .serializers import (
    StockHoldingSerializer,
    StockSerializer,
    TransactionSerializer,
    UserSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """View zum Erstellen neuer Benutzer."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


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


class TransactionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Viewset zum Erstellen neuer Transaktionen."""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    queryset = None
