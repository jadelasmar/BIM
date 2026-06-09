from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_http_methods

from .forms import UsernameAndPasswordSetupForm


def _get_setup_user(uidb64):
    UserModel = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        return None


@require_http_methods(["GET", "POST"])
def password_setup_confirm(request, uidb64, token):
    user = _get_setup_user(uidb64)
    validlink = user is not None and default_token_generator.check_token(user, token)

    if not validlink:
        return render(
            request,
            "registration/password_setup_confirm.html",
            {
                "validlink": False,
            },
        )

    form = UsernameAndPasswordSetupForm(user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your BIM Nexus account has been created.")
        return redirect("login")

    return render(
        request,
        "registration/password_setup_confirm.html",
        {
            "form": form,
            "validlink": True,
        },
    )
