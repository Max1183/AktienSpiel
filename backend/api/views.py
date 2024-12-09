from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import generics, mixins, pagination, serializers, status, viewsets
from rest_framework.decorators import action
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
    Watchlist,
)

from .serializers import (
    MyTokenObtainPairSerializer,
    RegistrationRequestSerializer,
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


class TeamRankingViewSet(viewsets.ModelViewSet):
    """Viewset für die Team-Ranking-Liste."""

    queryset = Team.objects.all()
    serializer_class = TeamRankingSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def ranking(self, request):
        page_size = 20
        page_number = int(request.GET.get("page", 1))

        queryset = Team.objects.all().exclude(name="default")
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


class RegistrationRequestView(generics.CreateAPIView):
    """View zum Erstellen neuer Registrierungsanfragen."""

    queryset = RegistrationRequest.objects.all()
    serializer_class = RegistrationRequestSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        registration_request = serializer.save()
        registration_request.send_activation_email()


class CreateUserView(generics.CreateAPIView):
    """View zum Erstellen neuer Benutzer."""

    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class UserProfileViewSet(generics.RetrieveAPIView):
    """Viewset für Benutzerprofile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


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
        team = self.request.user.profile.team
        if Watchlist.objects.filter(
            team=team, stock=serializer.validated_data["stock"]
        ).exists():
            raise serializers.ValidationError("Stock is already in the watchlist.")
        elif serializer.is_valid():
            serializer.save(team=self.request.user.profile.team)
        else:
            print(serializer.errors)

    def create(self, request, *args, **kwargs):  # Überschreibe die create-Methode
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Wirft eine Exception, wenn ungültig
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"id": serializer.instance.id, "message": "Watchlist item created"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


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
    queryset = Stock.objects.filter(current_price__gt=0)
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
                {"valid": False, "message": "Fehler beim Validieren des Formulars."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if message == "":
            return Response({"valid": True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"valid": False, "message": message}, status=status.HTTP_200_OK
            )
