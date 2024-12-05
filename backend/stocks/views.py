from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import RegistrationRequest, Stock


def search_stocks(request):
    query = request.GET.get("q", "")

    if query:
        results = Stock.objects.filter(name__icontains=query, current_price__gt=0)
        data = [
            {"id": stock.pk, "name": stock.name, "current_price": stock.current_price}
            for stock in results
        ]
    else:
        data = []

    return JsonResponse(data, safe=False)


@staff_member_required
def register_player(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            if User.objects.filter(email=email).exists():
                messages.error(
                    request,
                    f"Ein Benutzer mit der E-Mail-Adresse {email} existiert bereits.",
                )
            else:
                registration_request, created = (
                    RegistrationRequest.objects.get_or_create(email=email)
                )
                if created:
                    registration_request.send_activation_email()
                    messages.success(
                        request, f"Eine Aktivierungs-E-Mail wurde an {email} gesendet."
                    )
                else:
                    messages.warning(
                        request,
                        f"Eine Registrierungsanfrage für {email} existiert bereits.",
                    )

        except Exception as e:  # Fange allgemeine Ausnahmen ab
            messages.error(
                request, f"Fehler beim Senden der E-Mail: {e}"
            )  # Gib den Fehler aus
        return redirect("admin:index")  # Oder wo immer du hin möchtest nach dem POST

    return render(request, "stocks/register_player.html")


def validate_activation_token(request, token):
    try:
        registration_request = get_object_or_404(
            RegistrationRequest, activation_token=token
        )
    except ValidationError:
        return JsonResponse({"valid": False, "message": "Ungültiges Token"})

    if registration_request.activated:
        return JsonResponse({"valid": False, "message": "Bereits aktiviert"})

    return JsonResponse({"valid": True, "email": registration_request.email})
