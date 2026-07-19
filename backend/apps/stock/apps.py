from django.apps import AppConfig
from django.db.models.signals import post_migrate


class BimStockConfig(AppConfig):
    name = "apps.stock"
    label = "bim_stock"
    verbose_name = "Inventory"

    def ready(self):
        post_migrate.connect(
            prepare_bimpos_roles,
            sender=self,
            dispatch_uid="bim_stock.prepare_bimpos_roles",
        )


def prepare_bimpos_roles(sender, **kwargs):
    from .roles import prepare_bimpos_groups

    prepare_bimpos_groups()
