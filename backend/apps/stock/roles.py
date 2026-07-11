from django.contrib.auth.models import Group, Permission

from .constants import APP_LABEL

BIMPOS_GROUPS = ("Administrator", "IT Support", "Viewer")
LEGACY_GROUPS = ("Operations Manager",)


def prepare_bimpos_groups():
    stock_permissions = Permission.objects.filter(
        content_type__app_label=APP_LABEL,
    )
    stock_view_permissions = stock_permissions.filter(codename__startswith="view_")
    stock_support_permissions = stock_permissions.exclude(codename__startswith="delete_")

    Group.objects.filter(name__in=LEGACY_GROUPS).delete()

    administrator_group, _ = Group.objects.get_or_create(name="Administrator")
    administrator_group.permissions.set(stock_permissions)

    it_support_group, _ = Group.objects.get_or_create(name="IT Support")
    it_support_group.permissions.set(stock_support_permissions)

    viewer_group, _ = Group.objects.get_or_create(name="Viewer")
    viewer_group.permissions.set(stock_view_permissions)

    return Group.objects.filter(name__in=BIMPOS_GROUPS)
