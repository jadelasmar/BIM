from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from bim_stock.models import Product, ProductUnit, Supplier


def _stock_permission(user):
    return user.has_perm("bim_stock.view_product") or user.has_perm(
        "bim_stock.view_productunit"
    )


def _recent_stock_activity():
    units = (
        ProductUnit.objects.filter(isactive=True)
        .select_related("product", "supplier")
        .filter(
            Q(crdate__isnull=False)
            | Q(sold_date__isnull=False)
            | Q(status=ProductUnit.STATUS_DAMAGED)
        )
        .order_by("-crdate")[:8]
    )
    activity = []

    for unit in units:
        if unit.status == ProductUnit.STATUS_SOLD:
            activity_type = "Delivery"
            reference = unit.serial_number
            activity_date = unit.sold_date or unit.crdate
        elif unit.status == ProductUnit.STATUS_DAMAGED:
            activity_type = "Stock Update"
            reference = unit.serial_number
            activity_date = unit.crdate
        else:
            activity_type = "Receiving"
            reference = unit.serial_number
            activity_date = unit.purchase_date or unit.crdate

        activity.append(
            {
                "type": activity_type,
                "reference": reference,
                "related": unit.supplier.name if unit.supplier else "Not connected",
                "user": "Admin workflow",
                "date": activity_date,
                "status": unit.get_status_display(),
                "status_class": unit.status,
            }
        )

    return activity


@login_required
def module_launcher(request):
    user = request.user
    can_view_stock = _stock_permission(user)
    recent_window = timezone.now() - timedelta(days=30)

    metrics = [
        {
            "label": "Total Products",
            "value": Product.objects.filter(isactive=True).count()
            if can_view_stock
            else "-",
            "tone": "orange",
        },
        {
            "label": "Available Stock",
            "value": ProductUnit.objects.filter(
                status=ProductUnit.STATUS_AVAILABLE,
                isactive=True,
            ).count()
            if can_view_stock
            else "-",
            "tone": "green",
        },
        {
            "label": "Damaged Stock",
            "value": ProductUnit.objects.filter(
                status=ProductUnit.STATUS_DAMAGED,
                isactive=True,
            ).count()
            if can_view_stock
            else "-",
            "tone": "red",
        },
        {
            "label": "Company Assets",
            "value": 0,
            "tone": "black",
            "note": "Module pending",
        },
        {
            "label": "Recent Deliveries",
            "value": ProductUnit.objects.filter(
                status=ProductUnit.STATUS_SOLD,
                sold_date__gte=recent_window.date(),
                isactive=True,
            ).count()
            if can_view_stock
            else "-",
            "tone": "blue",
            "note": "Using sold stock until Delivery exists",
        },
        {
            "label": "Recent Receiving",
            "value": ProductUnit.objects.filter(
                crdate__gte=recent_window,
                isactive=True,
            ).count()
            if can_view_stock
            else "-",
            "tone": "green",
            "note": "Using stock units until Receiving exists",
        },
    ]

    quick_actions = [
        {
            "label": "Add Product",
            "path": "/admin/bim_stock/product/add/",
            "enabled": user.has_perm("bim_stock.add_product"),
        },
        {
            "label": "Receive Stock",
            "path": "/admin/bim_stock/productunit/add/",
            "enabled": user.has_perm("bim_stock.add_productunit"),
        },
        {
            "label": "Create Delivery Note",
            "enabled": False,
            "note": "Delivery app pending",
        },
        {
            "label": "Add Company Asset",
            "enabled": False,
            "note": "Assets app pending",
        },
        {
            "label": "Add IT Document",
            "enabled": False,
            "note": "Knowledge Base pending",
        },
    ]

    modules = [
        {
            "name": "Command Center",
            "description": "Operational homepage and summaries.",
            "url": "module_launcher",
            "enabled": True,
            "active": True,
        },
        {
            "name": "Inventory",
            "description": "Products, stock units, suppliers, and availability.",
            "url": "bim_stock:dashboard",
            "enabled": can_view_stock,
        },
        {
            "name": "Stock Movement",
            "description": "Movement audit trail and transfers.",
            "enabled": False,
        },
        {
            "name": "Receiving / Delivery",
            "description": "Inbound receiving and outbound delivery notes.",
            "enabled": False,
        },
        {
            "name": "Companies / Sites",
            "description": "Company and site directory.",
            "enabled": False,
        },
        {
            "name": "Suppliers",
            "description": "Supplier records managed in Django admin.",
            "path": "/admin/bim_stock/supplier/",
            "enabled": user.has_perm("bim_stock.view_supplier") and user.is_staff,
            "count": Supplier.objects.count()
            if user.has_perm("bim_stock.view_supplier")
            else None,
        },
        {
            "name": "Company Assets",
            "description": "Assigned devices and owned IT assets.",
            "enabled": False,
        },
        {
            "name": "Knowledge Base",
            "description": "Internal IT documentation.",
            "enabled": False,
        },
        {
            "name": "Reports",
            "description": "Operational reports and exports.",
            "enabled": False,
        },
        {
            "name": "Settings",
            "description": "Admin, users, groups, and permissions.",
            "path": "/admin/",
            "enabled": user.is_staff,
        },
    ]

    context = {
        "metrics": metrics,
        "quick_actions": quick_actions,
        "modules": modules,
        "recent_activity": _recent_stock_activity() if can_view_stock else [],
        "can_view_stock": can_view_stock,
    }

    return render(request, "bim/module_launcher.html", context)
