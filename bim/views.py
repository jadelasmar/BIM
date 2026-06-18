from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .ui_registry import disabled_ui_item, ui_item
from bim_stock.models import DeliveryRecord, Product, ProductUnit, Supplier


def _stock_permission(user):
    return user.has_perm("bim_stock.view_product") or user.has_perm(
        "bim_stock.view_productunit"
    )


def _operational_reference(prefix, activity_date, number):
    year = getattr(activity_date, "year", timezone.localdate().year)
    return f"{prefix}-{year}-{number:04d}"


def _delivery_record_summary(delivery):
    items = [item for item in delivery.items.all() if item.isactive]
    if not items:
        return "Delivery record"
    if len(items) == 1:
        return f"1 {items[0].product}"
    return f"{len(items)} stock units"


def _recent_stock_activity():
    activity = []

    deliveries = (
        DeliveryRecord.objects.filter(isactive=True)
        .select_related("created_by")
        .prefetch_related("items__product")
        .order_by("-crdate")[:8]
    )
    for delivery in deliveries:
        activity.append(
            {
                "type": "Delivery",
                "reference": delivery.delivery_number,
                "related": _delivery_record_summary(delivery),
                "user": _user_display_name(delivery.created_by)
                if delivery.created_by
                else "",
                "date": delivery.delivery_date,
                "status": "Delivered",
                "status_class": "delivered",
            }
        )

    fallback_units = (
        ProductUnit.objects.filter(isactive=True)
        .select_related("product", "supplier")
        .filter(
            Q(crdate__isnull=False)
            | Q(sold_date__isnull=False)
        )
        .filter(delivery_item__isnull=True)
        .order_by("-crdate")[:8]
    )
    for unit in fallback_units:
        if unit.status == ProductUnit.STATUS_SOLD:
            activity_type = "Delivery"
            activity_date = unit.sold_date or unit.crdate
            reference = _operational_reference("DLV", activity_date, unit.pk)
            status_label = "Delivered"
            status_class = "delivered"
        else:
            activity_type = "Receiving"
            activity_date = unit.purchase_date or unit.crdate
            reference = _operational_reference("RCV", activity_date, unit.pk)
            status_label = "Received"
            status_class = "received"

        activity.append(
            {
                "type": activity_type,
                "reference": reference,
                "related": str(unit.product),
                "user": "",
                "date": activity_date,
                "status": status_label,
                "status_class": status_class,
            }
        )

    return sorted(
        activity,
        key=lambda item: str(item["date"] or ""),
        reverse=True,
    )[:8]


def _product_detail_href(product):
    return reverse("inventory_product_detail", kwargs={"pk": product.pk})


def _low_stock_alerts(limit=4):
    alerts = []
    products = (
        Product.objects.filter(isactive=True)
        .select_related("category", "model")
        .order_by("descript")
    )

    for product in products:
        if product.available_units == 0 or not product.is_low_stock:
            continue

        alerts.append(
            {
                "productName": str(product),
                "category": product.category.name if product.category_id else "",
                "availableQuantity": product.available_units,
                "reorderThreshold": product.reorder_stock_level,
                "href": _product_detail_href(product),
                "status": "Low Stock",
                "status_class": "low_stock",
            }
        )

        if len(alerts) >= limit:
            break

    return alerts


def _recent_deliveries(limit=4):
    deliveries = (
        DeliveryRecord.objects.filter(isactive=True)
        .prefetch_related("items__product")
        .order_by("-delivery_date", "-delivery_number")[:limit]
    )

    return [
        {
            "reference": delivery.delivery_number,
            "title": delivery.customer_name,
            "detail": _delivery_record_summary(delivery),
            "href": None,
            "futureHref": f"/inventory/deliveries/{delivery.pk}/",
            "date": delivery.delivery_date,
            "status": "Delivered",
            "status_class": "delivered",
        }
        for delivery in deliveries
    ]


def _recent_receiving(limit=4):
    units = (
        ProductUnit.objects.filter(isactive=True, crdate__isnull=False)
        .select_related("product")
        .filter(delivery_item__isnull=True)
        .exclude(status=ProductUnit.STATUS_SOLD)
        .order_by("-crdate")[:limit]
    )

    return [
        {
            "reference": _operational_reference(
                "RCV",
                unit.purchase_date or unit.crdate,
                unit.pk,
            ),
            "title": str(unit.product),
            "detail": unit.product.category.name if unit.product.category_id else "",
            "href": _product_detail_href(unit.product),
            "futureHref": None,
            "date": unit.purchase_date or unit.crdate,
            "status": "Received",
            "status_class": "received",
        }
        for unit in units
    ]


def _format_count(value):
    if isinstance(value, int):
        return f"{value:,}"

    return value


def _plural(value, singular, plural=None):
    if not isinstance(value, int):
        return plural or f"{singular}s"

    if value == 1:
        return singular

    return plural or f"{singular}s"


def _product_count_detail(value, suffix):
    return f"{_format_count(value)} {_plural(value, 'product')} {suffix}"


def _user_display_name(user):
    full_name = user.get_full_name().strip()
    return full_name or user.get_username()


def _low_stock_counts():
    products = Product.objects.filter(isactive=True)
    low_count = 0
    out_of_stock_count = 0

    for product in products:
        if product.available_units == 0:
            out_of_stock_count += 1
        elif product.is_low_stock:
            low_count += 1

    return low_count, out_of_stock_count


def _command_center_initial_data(
    request,
    user,
    metrics,
    quick_actions,
    modules,
    recent_activity,
    low_stock_alerts,
    recent_deliveries_panel,
    recent_receiving_panel,
    current_path=None,
):
    can_view_stock = request.user.has_perm("bim_stock.view_product")
    inventory_href = reverse("inventory") if can_view_stock else None
    can_use_operations = request.user.has_perm(
        "bim_stock.add_productunit"
    ) or request.user.has_perm("bim_stock.change_productunit")
    operations_href = reverse("operations") if can_use_operations else None
    can_access_admin = user.is_staff or user.is_superuser
    current_path = current_path or request.path
    total_products = metrics[0]["value"]
    available_stock = metrics[1]["value"]
    out_of_stock = metrics[2]["value"]
    low_stock = metrics[3]["value"]
    recent_deliveries = metrics[4]["value"]
    recent_receiving = metrics[5]["value"]
    out_of_stock_tone = (
        "danger" if isinstance(out_of_stock, int) and out_of_stock > 0 else "neutral"
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
            "canAccessAdmin": can_access_admin,
        },
        "csrfToken": get_token(request),
        "logoutHref": reverse("logout"),
        "currentPath": current_path,
        "theme": {
            "storageKey": "bim-nexus-theme",
            "default": "dark",
        },
        "api": {
            "commandCenter": reverse("command_center_data"),
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
                ui_item(
                    "administration",
                    href=reverse("admin:index"),
                    enabled=True,
                    active=False,
                    detail="Django admin",
                )
            ] if can_access_admin else [],
        },
        "hero": {
            "greeting": f"Good evening, {_user_display_name(user)}",
            "greetingName": _user_display_name(user),
            "title": "BIM Nexus",
            "subtitle": "Internal IT Operations Platform",
            "tenant": "BIMPOS",
            "searchPlaceholder": "Search products, stock units, deliveries, suppliers, companies...",
        },
        "kpis": [
            {
                "value": _format_count(total_products),
                "detail": _product_count_detail(total_products, "in BIM Stock"),
                "trend": "",
                **ui_item("total_products"),
            },
            {
                "value": _format_count(available_stock),
                "detail": f"{_format_count(available_stock)} {_plural(available_stock, 'unit')} ready for issue",
                "trend": "",
                **ui_item("available_stock"),
            },
            {
                "value": _format_count(out_of_stock),
                "detail": _product_count_detail(out_of_stock, "out of stock"),
                "trend": "",
                **ui_item("out_of_stock", tone=out_of_stock_tone),
            },
            {
                "value": _format_count(low_stock),
                "detail": _product_count_detail(low_stock, "with low stock"),
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
                "detail": "operational dispatches",
                **ui_item("delivery_records"),
            },
            {
                "value": _format_count(recent_receiving),
                "detail": "created this month",
                **ui_item("new_stock_units"),
            },
            disabled_ui_item(
                "assets",
                value="-",
                detail="Coming later",
            ),
            disabled_ui_item(
                "knowledge_base",
                value="-",
                detail="Coming later",
            ),
        ],
        "modules": modules,
        "quickActions": quick_actions,
        "recentActivity": recent_activity,
        "lowStockAlerts": low_stock_alerts,
        "recentDeliveries": recent_deliveries_panel,
        "recentReceiving": recent_receiving_panel,
        "pollIntervalMs": 60000,
    }


def _build_command_center_initial_data(request, current_path=None):
    user = request.user
    can_view_stock = _stock_permission(user)
    can_use_operations = user.has_perm("bim_stock.add_productunit") or user.has_perm(
        "bim_stock.change_productunit"
    )
    recent_window = timezone.now() - timedelta(days=30)
    low_stock_count, out_of_stock_count = _low_stock_counts() if can_view_stock else ("-", 0)

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
            "value": out_of_stock_count,
            **ui_item("out_of_stock"),
        },
        {
            "value": low_stock_count,
            **ui_item("low_stock"),
        },
        {
            "value": DeliveryRecord.objects.filter(isactive=True).count()
            if can_view_stock
            else "-",
            **ui_item("delivery_records"),
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
        {
            "href": None,
            "enabled": False,
            "description": "Coming later",
            **ui_item("add_supplier"),
        },
    ]

    modules = [
        {
            "description": "Products, stock units, availability",
            "href": reverse("inventory") if can_view_stock else None,
            "enabled": can_view_stock,
            "count": Product.objects.filter(isactive=True).count()
            if can_view_stock
            else None,
            "meta": "products",
            **ui_item("inventory"),
        },
        {
            "description": "Receiving records, delivery records, stock history",
            "href": reverse("operations") if can_use_operations else None,
            "enabled": can_use_operations,
            "count": 2,
            "meta": "active workflows",
            **ui_item("operations"),
        },
        {
            "description": "Company-owned equipment",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "Coming later",
            **ui_item("assets"),
        },
        {
            "description": "Procedures, guides, documentation",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "Coming later",
            **ui_item("knowledge_base"),
        },
        {
            "description": "Stock and operations summaries",
            "href": None,
            "enabled": False,
            "count": None,
            "meta": "Coming later",
            **ui_item("reports"),
        },
    ]

    recent_activity = _recent_stock_activity() if can_view_stock else []
    low_stock_alerts = _low_stock_alerts() if can_view_stock else []
    recent_deliveries_panel = _recent_deliveries() if can_view_stock else []
    recent_receiving_panel = _recent_receiving() if can_view_stock else []
    initial_data = _command_center_initial_data(
        request=request,
        user=user,
        metrics=metrics,
        quick_actions=quick_actions,
        modules=modules,
        recent_activity=recent_activity,
        low_stock_alerts=low_stock_alerts,
        recent_deliveries_panel=recent_deliveries_panel,
        recent_receiving_panel=recent_receiving_panel,
        current_path=current_path,
    )

    return initial_data


@login_required
def command_center_data(request):
    return JsonResponse(
        _build_command_center_initial_data(
            request,
            current_path=reverse("module_launcher"),
        )
    )


@login_required
def module_launcher(request, *args, **kwargs):
    initial_data = _build_command_center_initial_data(request)

    context = {
        "initial_data": initial_data,
        "vite_dev_server": settings.BIM_VITE_DEV_SERVER,
    }

    return render(request, "bim/react_app.html", context)
