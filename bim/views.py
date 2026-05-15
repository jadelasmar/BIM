from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def module_launcher(request):
    user = request.user
    modules = []

    if user.has_perm("bim_stock.view_product") or user.has_perm(
        "bim_stock.view_productunit"
    ):
        modules.append(
            {
                "name": "Stock & Inventory",
                "description": "Products, stock units, and current inventory.",
                "url": "bim_stock:dashboard",
            }
        )

    if user.is_staff:
        modules.append(
            {
                "name": "Django Admin",
                "description": "Backend management for authorized staff.",
                "url": "admin:index",
            }
        )

    return render(request, "bim/module_launcher.html", {"modules": modules})
