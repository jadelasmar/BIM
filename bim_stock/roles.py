from django.contrib.auth.models import Group, Permission


BIMPOS_GROUPS = ("Admin", "Stock Manager", "IT Support", "Viewer")


def prepare_bimpos_groups():
    stock_permissions = Permission.objects.filter(
        content_type__app_label="bim_stock",
    )
    stock_view_permissions = stock_permissions.filter(codename__startswith="view_")
    stock_edit_permissions = stock_permissions.exclude(codename__startswith="delete_")

    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(stock_permissions)

    stock_manager_group, _ = Group.objects.get_or_create(name="Stock Manager")
    stock_manager_group.permissions.set(stock_edit_permissions)

    it_support_group, _ = Group.objects.get_or_create(name="IT Support")
    it_support_group.permissions.set(stock_view_permissions)

    viewer_group, _ = Group.objects.get_or_create(name="Viewer")
    viewer_group.permissions.set(stock_view_permissions)

    return Group.objects.filter(name__in=BIMPOS_GROUPS)
