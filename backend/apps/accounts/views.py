from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_http_methods

from .forms import EmailOrUsernameAuthenticationForm, UsernameAndPasswordSetupForm


def _get_setup_user(uidb64):
    UserModel = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        return None


def _form_errors(form):
    return {
        field: [error["message"] for error in errors]
        for field, errors in form.errors.get_json_data().items()
    }


def _safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next") or "/"
    if next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    return "/"


@require_http_methods(["GET", "POST"])
def login_view(request):
    redirect_to = _safe_next_url(request)
    submitted_username = request.POST.get("username", "").strip()
    form = EmailOrUsernameAuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        return redirect(redirect_to)

    errors = []
    if request.method == "POST":
        errors = _form_errors(form).get("__all__", [])

    return render(
        request,
        "bim/react_app.html",
        {
            "page_title": "BIM Nexus Login",
            "initial_data": {
                "page": {
                    "type": "login",
                    "title": "Welcome Back",
                    "action": reverse("bim_accounts:login"),
                    "csrfToken": get_token(request),
                    "errors": errors,
                    "next": redirect_to if redirect_to != "/" else "",
                    "adminEmail": settings.BIM_ADMIN_EMAIL,
                    "username": submitted_username,
                },
            },
        },
    )


@require_http_methods(["GET", "POST"])
def password_setup_confirm(request, uidb64, token):
    user = _get_setup_user(uidb64)
    validlink = user is not None and default_token_generator.check_token(user, token)

    if not validlink:
        return render(
            request,
            "bim/react_app.html",
            {
                "page_title": "Create BIM Nexus Account",
                "initial_data": {
                    "page": {
                        "type": "password_setup",
                        "title": "This password setup link is invalid",
                        "validlink": False,
                    },
                },
            },
        )

    form = UsernameAndPasswordSetupForm(user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your BIM Nexus account has been created.")
        return redirect("/accounts/login/")

    return render(
        request,
        "bim/react_app.html",
        {
            "page_title": "Create BIM Nexus Account",
            "initial_data": {
                "page": {
                    "type": "password_setup",
                    "title": "Create your BIM Nexus account",
                    "action": request.path,
                    "csrfToken": get_token(request),
                    "errors": _form_errors(form),
                    "validlink": True,
                    "usernamePlaceholder": form.fields["username"].widget.attrs.get(
                        "placeholder",
                        "",
                    ),
                },
            },
        },
    )
