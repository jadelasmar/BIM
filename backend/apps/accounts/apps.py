from django.apps import AppConfig


class BimAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "bim_accounts"
    verbose_name = "BIM Accounts"

    def ready(self):
        import apps.accounts.signals  # noqa: F401
