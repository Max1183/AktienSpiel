from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import generics, pagination, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from stocks.models import (
    RegistrationRequest,
    Stock,
    StockHolding,
    Team,
    Transaction,
    UserProfile,
    get_team_ranking_queryset,
)
from stocks.services import calculate_stock_profit
from stocks.transactions import execute_transaction

from .serializers import (
    MyTokenObtainPairSerializer,
    RegistrationRequestSerializer,
    StockAnalysisSerializer,
    StockHoldingSerializer,
    StockSerializer,
    TeamRankingSerializer,
    TeamSerializer,
    TransactionCreateSerializer,
    TransactionListSerializer,
    TransactionUpdateSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
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
        page_size = 10
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
            total_profit = calculate_stock_profit(transactions, stock.current_price)
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

    def post(self, request):  # Noqa: C901
        try:
            field = request.data.get("field")
            value = request.data.get("value")
            message = ""

            if field == "username":
                if User.objects.filter(username=value).exists():
                    message = "Dieser Benutzername existiert bereits."

            elif field == "password":
                if len(value) < 8:
                    message = "Das Passwort muss mindestens 8 Zeichen lang sein."
                elif len(value) > 30:
                    message = "Das Passwort kann maximal 30 Zeichen lang sein."
                elif not any(char.isdigit() for char in value):
                    message = "Das Passwort muss mindestens eine Zahl enthalten."
                elif not any(char.isalpha() for char in value):
                    message = "Das Passwort muss mindestens einen Buchstaben enthalten."

            elif field == "team_code":
                try:
                    team = Team.objects.get(code=value)

                    if team.members.count() >= 4:
                        message = "Das Team ist bereits voll."
                    else:
                        return Response(
                            {"valid": True, "team_name": team.name},
                            status=status.HTTP_200_OK,
                        )

                except Team.DoesNotExist:
                    message = "Ungültiger Teamcode."

            elif field == "team_name":
                if Team.objects.filter(name=value).exists():
                    message = "Ein Team mit diesem Namen existiert bereits."

            else:
                return Response(
                    {"valid": False, "message": "Ungültige Anfrage!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception:
            return Response(
                {"valid": False, "message": "Fehler beim Validieren des Feldes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if message == "":
            return Response({"valid": True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"valid": False, "message": message}, status=status.HTTP_200_OK
            )
