from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
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


def _format_count(value):
    if isinstance(value, int):
        return f"{value:,}"

    return value


def _user_display_name(user):
    full_name = user.get_full_name().strip()
    return full_name or user.get_username()


def _command_center_initial_data(
    request,
    user,
    metrics,
    quick_actions,
    modules,
    recent_activity,
):
    total_products = metrics[0]["value"]
    available_stock = metrics[1]["value"]
    damaged_stock = metrics[2]["value"]
    recent_deliveries = metrics[4]["value"]
    recent_receiving = metrics[5]["value"]

    return {
        "user": {
            "username": user.get_username(),
            "displayName": _user_display_name(user),
            "initials": "".join(
                part[:1] for part in _user_display_name(user).split()[:2]
            ).upper()
            or user.get_username()[:1].upper(),
            "isStaff": user.is_staff,
        },
        "csrfToken": get_token(request),
        "logoutHref": reverse("logout"),
        "navigation": {
            "primary": [
                {
                    "name": "Command Center",
                    "href": reverse("module_launcher"),
                    "active": True,
                    "icon": "layout-dashboard",
                }
            ],
            "secondary": [
                {
                    "name": "Settings",
                    "href": "/admin/" if user.is_staff else None,
                    "enabled": user.is_staff,
                    "icon": "settings",
                }
            ],
        },
        "hero": {
            "greeting": f"Good evening, {_user_display_name(user)}",
            "title": "BIM Nexus",
            "subtitle": "Internal IT Operations Platform",
            "tenant": "BIMPOS",
            "searchPlaceholder": "Search assets, products, deliveries, suppliers, knowledge base...",
        },
        "kpis": [
            {
                "label": "Total Products",
                "value": _format_count(total_products),
                "detail": "catalogue items",
                "trend": "+34 this week",
                "tone": "neutral",
                "icon": "database",
            },
            {
                "label": "Available Stock",
                "value": _format_count(available_stock),
                "detail": "ready for issue",
                "trend": "-12 since yesterday",
                "tone": "stock",
                "icon": "layers",
            },
            {
                "label": "Assets In Use",
                "value": "0",
                "detail": "module pending",
                "trend": "Company Assets pending",
                "tone": "neutral",
                "icon": "cpu",
            },
            {
                "label": "Low Stock Alerts",
                "value": _format_count(damaged_stock),
                "detail": "need review",
                "trend": "+4 since yesterday",
                "tone": "warning",
                "icon": "triangle-alert",
            },
        ],
        "overview": [
            {"label": "Sites", "value": "0", "detail": "module pending", "tone": "blue"},
            {
                "label": "Suppliers",
                "value": _format_count(Supplier.objects.count()),
                "detail": "registered vendor",
                "tone": "purple",
            },
            {
                "label": "Total Assets",
                "value": "0",
                "detail": "module pending",
                "tone": "green",
            },
            {
                "label": "Knowledge Docs",
                "value": "0",
                "detail": "module pending",
                "tone": "yellow",
            },
            {
                "label": "Recent Deliveries",
                "value": _format_count(recent_deliveries),
                "detail": "sold stock proxy",
                "tone": "orange",
            },
            {
                "label": "Recent Receiving",
                "value": _format_count(recent_receiving),
                "detail": "new stock proxy",
                "tone": "blue",
            },
        ],
        "modules": modules,
        "quickActions": quick_actions,
        "recentActivity": recent_activity,
    }


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
            "href": "/admin/bim_stock/product/add/",
            "enabled": user.has_perm("bim_stock.add_product"),
            "description": "Register new item to catalogue",
            "icon": "plus",
        },
        {
            "label": "Receive Stock",
            "href": "/admin/bim_stock/productunit/add/",
            "enabled": user.has_perm("bim_stock.add_productunit"),
            "description": "Record incoming stock receipt",
            "icon": "download",
        },
        {
            "label": "Create Delivery",
            "href": None,
            "enabled": False,
            "note": "Delivery app pending",
            "description": "Initiate outbound delivery order",
            "icon": "upload",
        },
    ]

    modules = [
        {
            "name": "BIM Stock",
            "description": "Products, stock levels, categories",
            "href": reverse("bim_stock:dashboard") if can_view_stock else None,
            "enabled": can_view_stock,
            "count": Product.objects.filter(isactive=True).count()
            if can_view_stock
            else None,
            "meta": "products",
            "icon": "database",
            "tone": "blue",
        },
        {
            "name": "Operations",
            "description": "Receiving, deliveries, movements",
            "href": None,
            "enabled": False,
            "count": 0,
            "meta": "events this month",
            "icon": "trending-up",
            "tone": "green",
        },
        {
            "name": "Assets",
            "description": "Hardware, devices, peripherals",
            "href": None,
            "enabled": False,
            "count": 0,
            "meta": "registered",
            "icon": "cpu",
            "tone": "purple",
        },
        {
            "name": "Knowledge Base",
            "description": "Procedures, guides, documentation",
            "href": None,
            "enabled": False,
            "count": 0,
            "meta": "articles",
            "icon": "book-open",
            "tone": "yellow",
        },
        {
            "name": "Reports",
            "description": "Analytics, exports, summaries",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "Last run: today",
            "icon": "bar-chart-3",
            "tone": "orange",
        },
    ]

    recent_activity = _recent_stock_activity() if can_view_stock else []
    initial_data = _command_center_initial_data(
        request=request,
        user=user,
        metrics=metrics,
        quick_actions=quick_actions,
        modules=modules,
        recent_activity=recent_activity,
    )

    context = {
        "metrics": metrics,
        "quick_actions": quick_actions,
        "modules": modules,
        "recent_activity": recent_activity,
        "can_view_stock": can_view_stock,
        "initial_data": initial_data,
        "vite_dev_server": settings.BIM_VITE_DEV_SERVER,
    }

    return render(request, "bim/react_app.html", context)
