from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .forms import BimUserChangeForm, BimUserCreationForm
from .utils import build_password_setup_url


admin.site.unregister(User)


@admin.register(User)
class BimUserAdmin(UserAdmin):
    form = BimUserChangeForm
    add_form = BimUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email",),
            },
        ),
    )
    actions = ("send_password_setup_links",)

    @admin.action(description="Generate manual account setup links")
    def send_password_setup_links(self, request, queryset):
        generated_count = 0
        skipped_count = 0

        for user in queryset:
            if not user.email:
                skipped_count += 1
                continue

            user.set_unusable_password()
            user.is_active = True
            user.save(update_fields=("password", "is_active"))
            setup_url = build_password_setup_url(user, request)
            self.message_user(
                request,
                f"Manual setup link for {user.email}: {setup_url}",
                messages.SUCCESS,
            )
            generated_count += 1

        message = f"Generated {generated_count} manual account setup link(s)."
        if skipped_count:
            message += f" Skipped {skipped_count} user(s) without email."

        self.message_user(request, message, messages.SUCCESS)
