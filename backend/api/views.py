from django.contrib.auth.models import User

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from stocks.models import Stock, StockHolding

from .serializers import StockHoldingSerializer, StockSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class StockViewSet(generics.ListAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()
    permission_classes = [AllowAny]


class StockHoldingViewSet(viewsets.ModelViewSet):
    serializer_class = StockHoldingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        team = self.request.user.team
        return StockHolding.objects.filter(team=team)
