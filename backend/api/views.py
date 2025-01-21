from decimal import Decimal

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, pagination, serializers, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from stocks.models import (
    RegistrationRequest,
    Stock,
    StockHolding,
    Transaction,
    UserProfile,
    get_team_ranking_queryset,
)
from stocks.services import calculate_stock_profit, execute_transaction

from .serializers import (
    MyTokenObtainPairSerializer,
    RegistrationRequestSerializer,
    StockAnalysisSerializer,
    StockHoldingSerializer,
    StockInfoSerializer,
    StockSerializer,
    TeamRankingSerializer,
    TeamSerializer,
    TransactionCreateSerializer,
    TransactionListSerializer,
    TransactionUpdateSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    ValidateFieldSerializer,
    WatchlistCreateSerializer,
    WatchlistSerializer,
    WatchlistUpdateSerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    """View zum Abrufen eines Tokens."""

    serializer_class = MyTokenObtainPairSerializer


class RegistrationRequestCreateView(generics.CreateAPIView):
    """View zum Erstellen neuer Registrierungsanfragen."""

    queryset = RegistrationRequest.objects.all()
    serializer_class = RegistrationRequestSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        registration_request = serializer.save()
        registration_request.send_activation_email()


class StockDetailView(generics.RetrieveAPIView):
    """Viewset für Aktien Details."""

    serializer_class = StockSerializer
    queryset = Stock.objects.filter(current_price__gt=0)
    permission_classes = [IsAuthenticated]


class TeamDetailView(generics.RetrieveAPIView):
    """Viewset für Teams."""

    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile.team


class TeamRankingListView(generics.ListAPIView):
    """Viewset für die Team-Ranking-Liste."""

    serializer_class = TeamRankingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return get_team_ranking_queryset()

    def get(self, request, *args, **kwargs):
        page_size = 2
        page_number = int(request.GET.get("page", 1))

        queryset = self.get_queryset()
        sorted_queryset = sorted(
            queryset, key=lambda team: team.total_balance, reverse=True
        )

        paginator = pagination.PageNumberPagination()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(sorted_queryset, request)

        serializer = TeamRankingSerializer(
            page, many=True, context={"request": request}
        )

        for i, item in enumerate(serializer.data):
            item["rank"] = (page_number - 1) * page_size + i + 1

        return Response(
            {
                "results": serializer.data,
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "current_page": page_number,
                "page_size": page_size,
            }
        )


class WatchlistListView(generics.ListAPIView):
    """Viewset für die Watchlist."""

    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.team.watchlist.all()


class WatchlistCreateView(generics.CreateAPIView):
    """Viewset für das Erstellen einer Watchlist."""

    serializer_class = WatchlistCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        team = self.request.user.profile.team
        serializer.save(team=team)


class WatchlistUpdateView(generics.UpdateAPIView):
    """Viewset für das Aktualisieren einer Watchlist."""

    serializer_class = WatchlistUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.team.watchlist.all()


class WatchlistDeleteView(generics.DestroyAPIView):
    """Viewset für das Löschen einer Watchlist."""

    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.team.watchlist.all()


class CreateUserView(generics.CreateAPIView):
    """View zum Erstellen neuer Benutzer."""

    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserProfileDetailView(generics.RetrieveAPIView):
    """Viewset für Benutzerprofile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()

    def get_object(self):
        return self.request.user.profile


class StockHoldingListView(generics.ListAPIView):
    """Viewset für die Stock-Holdings eines Teams."""

    serializer_class = StockHoldingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StockHolding.objects.filter(
            team=self.request.user.profile.team, amount__gt=0
        ).select_related("team", "stock")


class TransactionListView(generics.ListAPIView):
    """Viewset für die Transaktionen eines Teams."""

    serializer_class = TransactionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Transaction.objects.filter(team=self.request.user.profile.team)
            .order_by("-date")
            .select_related("stock")
        )


class TransactionUpdateView(generics.UpdateAPIView):
    """Viewset für das Aktualisieren von Transaktionen."""

    serializer_class = TransactionUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(team=self.request.user.profile.team)


class TransactionCreateView(generics.CreateAPIView):
    """Viewset für das Erstellen neuer Transaktionen."""

    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Erstellt eine neue Transaktion und führt sie aus."""
        team = self.request.user.profile.team
        validated_data = serializer.validated_data
        validated_data["team"] = team
        validated_data["price"] = validated_data["stock"].current_price
        fee = validated_data["stock"].calculate_fee(validated_data["amount"])
        validated_data["fee"] = fee
        transaction_created = serializer.save()
        execute_transaction(transaction_created)


class AnalysisView(APIView):
    """View zum Berechnen des Gewinns eines Teams."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        team = request.user.profile.team
        stock_profits = []
        unique_stocks = set(
            Transaction.objects.filter(team=team).values_list("stock", flat=True)
        )
        for stock_id in unique_stocks:
            stock = Stock.objects.get(id=stock_id)
            transactions = Transaction.objects.filter(team=team, stock=stock)
            total_profit = calculate_stock_profit(transactions)
            try:
                stock_holding = StockHolding.objects.get(team=team, stock=stock)
                current_holding = stock_holding.amount * stock.current_price
                total_profit += current_holding
            except StockHolding.DoesNotExist:
                current_holding = Decimal("0.00")

            stock_profits.append(
                {
                    "id": stock.pk,
                    "name": stock.name,
                    "ticker": stock.ticker,
                    "total_profit": total_profit,
                    "current_holding": current_holding,
                }
            )

        sorted_stock_profits = sorted(
            stock_profits, key=lambda x: x["total_profit"], reverse=True
        )
        serializer = StockAnalysisSerializer(sorted_stock_profits, many=True)
        return Response(serializer.data)


class ValidateFormView(APIView):
    """View zum Validieren von Formulardaten."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validates the form data"""
        serializer = ValidateFieldSerializer(data=request.data)
        if serializer.is_valid():
            field = request.data.get("field")
            value = serializer.validated_data.get("value")
            try:
                if field == "username":
                    serializer.validate_username(value)
                elif field == "password":
                    serializer.validate_password(value)
                elif field == "team_code":
                    return Response(
                        serializer.validate_team_code(value), status=status.HTTP_200_OK
                    )
                elif field == "team_name":
                    serializer.validate_team_name(value)
                else:
                    return Response(
                        {"valid": False, "message": "Ungültige Anfrage!"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response({"valid": True}, status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                return Response(
                    {"valid": False, "message": e.detail[0]}, status=status.HTTP_200_OK
                )
            except Exception:
                return Response(
                    {"valid": False, "message": "Fehler beim validieren des Feldes."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"valid": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SearchStocksView(APIView):
    """View to search stocks, and to return the results paginated."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get("q", "")
        if query:
            results = Stock.objects.filter(
                name__icontains=query, current_price__gt=0
            ).order_by("name")[:50]
        else:
            results = []

        serializer = StockInfoSerializer(results, many=True)
        return Response(serializer.data)


class ValidateActivationTokenView(APIView):
    """View for validating the activation token."""

    permission_classes = [AllowAny]

    def get(self, request, token):
        """Validates the token, and returns if the token is valid, or if it has already been activated."""
        try:
            registration_request = get_object_or_404(
                RegistrationRequest, activation_token=token
            )
        except Http404:
            return Response(
                {"valid": False, "message": "Ungültiges Token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if registration_request.activated:
            return Response(
                {"valid": False, "message": "Bereits aktiviert"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"valid": True, "email": registration_request.email},
            status=status.HTTP_200_OK,
        )
