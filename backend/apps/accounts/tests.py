from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class LoginViewTests(TestCase):
    def test_login_mailto_uses_percent_encoding_for_subject_and_body(self):
        auth_pages_source = (
            Path(settings.BASE_DIR).parent
            / "frontend"
            / "src"
            / "pages"
            / "auth"
            / "AuthPages.jsx"
        ).read_text(encoding="utf-8")

        self.assertNotIn("new URLSearchParams", auth_pages_source)
        self.assertIn("subject=${encodeURIComponent(subject)}", auth_pages_source)
        self.assertIn("body=${encodeURIComponent(body)}", auth_pages_source)

    @override_settings(BIM_ADMIN_EMAIL="support@example.com")
    def test_login_page_exposes_configured_administrator_email(self):
        response = self.client.get(reverse("bim_accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["initial_data"]["page"]["adminEmail"],
            "support@example.com",
        )

    def test_failed_login_preserves_only_trimmed_username(self):
        response = self.client.post(
            reverse("bim_accounts:login"),
            {
                "username": "  office.user@example.com  ",
                "password": "incorrect-secret",
            },
        )

        self.assertEqual(response.status_code, 200)
        page_data = response.context["initial_data"]["page"]
        self.assertEqual(page_data["username"], "office.user@example.com")
        self.assertEqual(
            page_data["errors"],
            ["Invalid username/email or password."],
        )
        self.assertNotIn("password", page_data)
        self.assertNotIn("incorrect-secret", str(page_data))


class PasswordSetupViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="pending-office.user",
            email="office.user@example.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.setup_url = f"/accounts/setup/{uidb64}/{token}/"

    def test_failed_setup_preserves_non_sensitive_values_only(self):
        response = self.client.post(
            self.setup_url,
            {
                "username": "office.user",
                "first_name": "Office",
                "last_name": "User",
                "new_password1": "SecretPass123!",
                "new_password2": "different-secret",
            },
        )

        self.assertEqual(response.status_code, 200)
        page_data = response.context["initial_data"]["page"]
        self.assertEqual(page_data["username"], "office.user")
        self.assertEqual(page_data["firstName"], "Office")
        self.assertEqual(page_data["lastName"], "User")
        self.assertEqual(
            page_data["errors"]["new_password2"],
            ["The two password fields didn’t match."],
        )
        self.assertNotIn("new_password1", page_data)
        self.assertNotIn("new_password2", page_data)
        self.assertNotIn("SecretPass123!", str(page_data))
        self.assertNotIn("different-secret", str(page_data))
        self.assertNotContains(response, "SecretPass123!")
        self.assertNotContains(response, "different-secret")

    def test_missing_required_setup_fields_return_field_errors(self):
        response = self.client.post(
            self.setup_url,
            {
                "username": "office.user",
                "first_name": "",
                "last_name": "",
                "new_password1": "",
                "new_password2": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        errors = response.context["initial_data"]["page"]["errors"]
        self.assertEqual(errors["first_name"], ["This field is required."])
        self.assertEqual(errors["last_name"], ["This field is required."])
        self.assertEqual(errors["new_password1"], ["This field is required."])
        self.assertEqual(errors["new_password2"], ["This field is required."])

    def test_setup_page_controls_safe_fields_and_validates_required_fields(self):
        auth_pages_source = (
            Path(settings.BASE_DIR).parent
            / "frontend"
            / "src"
            / "pages"
            / "auth"
            / "AuthPages.jsx"
        ).read_text(encoding="utf-8")

        self.assertIn('useState(data.username || "")', auth_pages_source)
        self.assertIn('useState(data.firstName || "")', auth_pages_source)
        self.assertIn('useState(data.lastName || "")', auth_pages_source)
        self.assertIn('"First name is required."', auth_pages_source)
        self.assertIn('"Last name is required."', auth_pages_source)
        self.assertIn('"Password is required."', auth_pages_source)
        self.assertIn('"Password confirmation is required."', auth_pages_source)
        self.assertIn("onSubmit={handleSubmit}", auth_pages_source)
        self.assertIn("noValidate", auth_pages_source)
