from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .ui_registry import disabled_ui_item, ui_item
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
        )
        .order_by("-crdate")[:8]
    )
    activity = []

    for unit in units:
        if unit.status == ProductUnit.STATUS_SOLD:
            activity_type = "Delivery"
            reference = unit.serial_number
            activity_date = unit.sold_date or unit.crdate
        else:
            activity_type = "Receiving"
            reference = unit.serial_number
            activity_date = unit.purchase_date or unit.crdate

        activity.append(
            {
                "type": activity_type,
                "reference": reference,
                "related": unit.supplier.name if unit.supplier else "",
                "user": "",
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


def _low_stock_counts():
    products = Product.objects.filter(isactive=True)
    low_count = 0
    critical_count = 0

    for product in products:
        if product.is_critical_stock:
            critical_count += 1
        elif product.is_low_stock:
            low_count += 1

    return low_count, critical_count


def _command_center_initial_data(
    request,
    user,
    metrics,
    quick_actions,
    modules,
    recent_activity,
):
    can_view_stock = request.user.has_perm("bim_stock.view_product")
    inventory_href = reverse("inventory") if can_view_stock else None
    can_use_operations = request.user.has_perm(
        "bim_stock.add_productunit"
    ) or request.user.has_perm("bim_stock.change_productunit")
    operations_href = reverse("operations") if can_use_operations else None
    current_path = request.path
    total_products = metrics[0]["value"]
    available_stock = metrics[1]["value"]
    critical_stock = metrics[2]["value"]
    low_stock = metrics[3]["value"]
    recent_deliveries = metrics[4]["value"]
    recent_receiving = metrics[5]["value"]
    critical_stock_tone = (
        "danger" if isinstance(critical_stock, int) and critical_stock > 0 else "neutral"
    )
    low_stock_tone = (
        "warning" if isinstance(low_stock, int) and low_stock > 0 else "neutral"
    )

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
        "currentPath": current_path,
        "theme": {
            "storageKey": "bim-nexus-theme",
            "default": "dark",
        },
        "api": {
            "summary": "/api/stock/summary/",
            "products": "/api/stock/products/",
            "productDetail": "/api/stock/products/{id}/",
            "productUnits": "/api/stock/product-units/",
            "productUnitDetail": "/api/stock/product-units/{id}/",
            "deliveries": "/api/stock/deliveries/",
            "suppliers": "/api/stock/suppliers/",
            "brands": "/api/stock/brands/",
            "models": "/api/stock/models/",
            "categories": "/api/stock/categories/",
            "types": "/api/stock/types/",
        },
        "routes": {
            "inventory": reverse("inventory"),
            "addProduct": reverse("inventory_add_product"),
            "receiveStock": reverse("inventory_receive_stock"),
            "createDelivery": reverse("inventory_create_delivery"),
        },
        "navigation": {
            "primary": [
                {
                    "href": reverse("module_launcher"),
                    "active": current_path == reverse("module_launcher"),
                    **ui_item("command_center"),
                },
                {
                    "href": inventory_href,
                    "active": current_path.startswith(reverse("inventory")),
                    "enabled": can_view_stock,
                    **ui_item("inventory"),
                },
                {
                    "href": operations_href,
                    "active": current_path.startswith(reverse("operations")),
                    "enabled": can_use_operations,
                    **ui_item("operations"),
                }
            ],
            "secondary": [
                {
                    "href": reverse("settings"),
                    "enabled": True,
                    "active": current_path.startswith(reverse("settings")),
                    **ui_item("settings"),
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
                "value": _format_count(total_products),
                "detail": "catalogue items",
                "trend": "",
                **ui_item("total_products"),
            },
            {
                "value": _format_count(available_stock),
                "detail": "ready for issue",
                "trend": "",
                **ui_item("available_stock"),
            },
            {
                "value": _format_count(critical_stock),
                "detail": "at or below minimum level",
                "trend": "",
                "tone": critical_stock_tone,
                **ui_item("critical_stock", tone=critical_stock_tone),
            },
            {
                "value": _format_count(low_stock),
                "detail": "at or below reorder level",
                "trend": "",
                **ui_item("low_stock", tone=low_stock_tone),
            },
        ],
        "overview": [
            {
                "value": _format_count(Supplier.objects.count()),
                "detail": "registered vendor",
                **ui_item("suppliers"),
            },
            {
                "value": _format_count(recent_deliveries),
                "detail": "stock units marked sold",
                **ui_item("sold_units"),
            },
            {
                "value": _format_count(recent_receiving),
                "detail": "created this month",
                **ui_item("new_stock_units"),
            },
            disabled_ui_item(
                "assets",
                value="-",
                detail="module pending",
            ),
            disabled_ui_item(
                "knowledge_base",
                value="-",
                detail="module pending",
            ),
        ],
        "modules": modules,
        "quickActions": quick_actions,
        "recentActivity": recent_activity,
    }


@login_required
def module_launcher(request, *args, **kwargs):
    user = request.user
    can_view_stock = _stock_permission(user)
    can_use_operations = user.has_perm("bim_stock.add_productunit") or user.has_perm(
        "bim_stock.change_productunit"
    )
    recent_window = timezone.now() - timedelta(days=30)
    low_stock_count, critical_stock_count = _low_stock_counts() if can_view_stock else ("-", 0)

    metrics = [
        {
            "value": Product.objects.filter(isactive=True).count()
            if can_view_stock
            else "-",
            **ui_item("total_products"),
        },
        {
            "value": ProductUnit.objects.filter(
                status=ProductUnit.STATUS_AVAILABLE,
                isactive=True,
            ).count()
            if can_view_stock
            else "-",
            **ui_item("available_stock"),
        },
        {
            "value": critical_stock_count,
            **ui_item("critical_stock"),
        },
        {
            "value": low_stock_count,
            **ui_item("low_stock"),
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
            "href": reverse("inventory_add_product")
            if user.has_perm("bim_stock.add_product")
            else None,
            "enabled": user.has_perm("bim_stock.add_product"),
            "description": "Register new item to catalogue",
            **ui_item("add_product"),
        },
        {
            "href": reverse("inventory_receive_stock")
            if user.has_perm("bim_stock.add_productunit")
            else None,
            "enabled": user.has_perm("bim_stock.add_productunit"),
            "description": "Record incoming stock receipt",
            **ui_item("receive_stock"),
        },
        {
            "href": reverse("inventory_create_delivery")
            if user.has_perm("bim_stock.change_productunit")
            else None,
            "enabled": user.has_perm("bim_stock.change_productunit"),
            "description": "Initiate outbound delivery order",
            **ui_item("create_delivery"),
        },
    ]

    modules = [
        {
            "description": "Products, stock levels, categories",
            "href": reverse("inventory") if can_view_stock else None,
            "enabled": can_view_stock,
            "count": Product.objects.filter(isactive=True).count()
            if can_view_stock
            else None,
            "meta": "products",
            **ui_item("inventory", name="BIM Stock"),
        },
        {
            "description": "Receiving, deliveries, movements",
            "href": reverse("operations") if can_use_operations else None,
            "enabled": can_use_operations,
            "count": 2,
            "meta": "active workflows",
            **ui_item("operations"),
        },
        {
            "description": "Hardware, devices, peripherals",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "module pending",
            **ui_item("assets"),
        },
        {
            "description": "Procedures, guides, documentation",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "module pending",
            **ui_item("knowledge_base"),
        },
        {
            "description": "Analytics, exports, summaries",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "module pending",
            **ui_item("reports"),
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
