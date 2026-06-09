from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
    UserChangeForm,
    UsernameField,
)
from django.contrib.auth.models import Group


PENDING_USERNAME_PREFIX = "pending-"
DEFAULT_USER_GROUP = "Viewer"


def is_pending_username(username):
    return username.startswith(PENDING_USERNAME_PREFIX)


def make_username_from_email(email, max_length=150):
    local_part = email.split("@", 1)[0].strip().lower()
    username_chars = []

    for char in local_part:
        if char.isalnum() or char in "@.+-_":
            username_chars.append(char)
        else:
            username_chars.append("-")

    return ("".join(username_chars).strip(".+-_") or "user")[:max_length]


def make_setup_username(user):
    if is_pending_username(user.username):
        return make_username_from_email(user.email)

    return user.username


def make_pending_username(email):
    UserModel = get_user_model()
    base = f"{PENDING_USERNAME_PREFIX}{make_username_from_email(email)}"
    base = base[:140]
    candidate = base
    counter = 2

    while UserModel._default_manager.filter(username__iexact=candidate).exists():
        suffix = f"-{counter}"
        candidate = f"{base[:150 - len(suffix)]}{suffix}"
        counter += 1

    return candidate


class UniqueEmailMixin:
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            return email

        UserModel = get_user_model()
        users = UserModel._default_manager.filter(email__iexact=email)

        if self.instance and self.instance.pk:
            users = users.exclude(pk=self.instance.pk)

        existing_user = users.first()
        if existing_user:
            raise forms.ValidationError(
                f"Email is already used by {existing_user.username} ({existing_user.email})."
            )

        return email


class BimUserCreationForm(UniqueEmailMixin, forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = make_pending_username(user.email)
        user.set_unusable_password()
        user.is_active = True

        if commit:
            user.save()
            default_group, _ = Group.objects.get_or_create(name=DEFAULT_USER_GROUP)
            user.groups.add(default_group)
            self.save_m2m()

        return user


class BimUserChangeForm(UniqueEmailMixin, UserChangeForm):
    email = forms.EmailField(required=True)


class UsernameAndPasswordSetupForm(SetPasswordForm):
    username = UsernameField(label="Username", max_length=150, required=False)
    first_name = forms.CharField(label="First name", max_length=150, required=True)
    last_name = forms.CharField(label="Last name", max_length=150, required=True)

    field_order = ("username", "first_name", "last_name", "new_password1", "new_password2")

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        setup_username = make_setup_username(user)
        self.fields["username"].initial = setup_username
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name

        self.fields["username"].widget.attrs.update(
            {
                "autocomplete": "username",
                "placeholder": setup_username,
            }
        )
        self.fields["first_name"].widget.attrs.update({"autocomplete": "given-name"})
        self.fields["last_name"].widget.attrs.update({"autocomplete": "family-name"})

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            username = make_setup_username(self.user)

        users = self.user.__class__._default_manager.filter(username__iexact=username)

        if self.user.pk:
            users = users.exclude(pk=self.user.pk)

        if users.exists():
            raise forms.ValidationError("Username is already used.")

        if is_pending_username(username):
            raise forms.ValidationError("Choose a personal username.")

        return username

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def save(self, commit=True):
        self.user.username = self.cleaned_data["username"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.set_password(self.cleaned_data["new_password1"])

        if commit:
            self.user.save()

        return self.user


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email or Username")

    error_messages = {
        "invalid_login": (
            "Invalid username/email or password."
        ),
        "inactive": "This account is inactive.",
    }
