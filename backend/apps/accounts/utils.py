from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def build_password_setup_url(user, request):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse(
        "bim_accounts:password_setup_confirm",
        kwargs={
            "uidb64": uidb64,
            "token": token,
        },
    )
    return request.build_absolute_uri(path)


def send_password_setup_email(user, request):
    if not user.email:
        return False

    setup_url = build_password_setup_url(user, request)
    send_mail(
        "Set up your BIM Nexus account",
        (
            "Hello,\n\n"
            "Use this secure link to choose your BIM Nexus username and password:\n"
            f"{setup_url}\n\n"
            "If you leave username blank, BIM Nexus will use the name before @ in your email.\n\n"
            "If you did not expect this email, contact your administrator."
        ),
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return True
