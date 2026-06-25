from django.apps import AppConfig


class BimAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bim_accounts"
    verbose_name = "BIM Accounts"

    def ready(self):
        import bim_accounts.signals  # noqa: F401
