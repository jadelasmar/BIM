from django.urls import path

from . import views

app_name = "bim_accounts"

urlpatterns = [
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path(
        "setup/<uidb64>/<token>/",
        views.password_setup_confirm,
        name="password_setup_confirm",
    ),
]
