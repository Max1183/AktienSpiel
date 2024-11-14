from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_player, name="register_player"),
    path(
        "validate_activation_token/<str:token>/",
        views.validate_activation_token,
        name="validate_activation_token",
    ),
]
