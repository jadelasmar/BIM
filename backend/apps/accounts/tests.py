from django.test import TestCase, override_settings
from django.urls import reverse


class LoginViewTests(TestCase):
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
