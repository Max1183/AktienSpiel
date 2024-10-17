from django.contrib.auth.models import User

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from stocks.models import Stock, StockHolding

from .serializers import StockHoldingSerializer, StockSerializer, TransactionSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class StockDetailView(generics.RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]


class StockViewSet(generics.ListAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()
    permission_classes = [IsAdminUser]


class StockHoldingViewSet(viewsets.ModelViewSet):
    serializer_class = StockHoldingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        team = self.request.user.team
        return StockHolding.objects.filter(team=team)


class TransactionCreateView(generics.CreateAPIView):
    queryset = StockHolding.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
