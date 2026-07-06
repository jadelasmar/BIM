from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse

from .ui_config import disabled_ui_item, ui_item
from apps.stock import constants as stock_constants
from apps.stock.models import ProductUnit
from apps.stock.selectors import (
    active_product_count,
    available_unit_count,
    delivery_record_count,
    low_stock_alerts,
    low_stock_counts,
    recent_deliveries,
    recent_receiving,
    recent_receiving_count,
    recent_stock_activity,
    reserved_unit_count,
    supplier_count,
    user_can_use_stock_operations,
    user_can_view_stock,
)


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
    can_view_stock = user_can_view_stock(request.user)
    inventory_href = reverse("inventory") if can_view_stock else None
    can_use_operations = user_can_use_stock_operations(request.user)
    operations_href = reverse("operations") if can_use_operations else None
    can_access_admin = user.is_staff or user.is_superuser
    current_path = current_path or request.path
    total_products = metrics[0]["value"]
    available_stock = metrics[1]["value"]
    reserved_stock = metrics[2]["value"]
    low_stock = metrics[3]["value"]
    out_of_stock = metrics[4]["value"]
    recent_deliveries = metrics[5]["value"]
    recent_receiving = metrics[6]["value"]
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
            "productMovements": "/api/stock/products/{id}/movements/",
            "productUnits": "/api/stock/product-units/",
            "productUnitDetail": "/api/stock/product-units/{id}/",
            "deliveries": "/api/stock/deliveries/",
            "deliveryDetail": "/api/stock/deliveries/{id}/",
            "reservations": "/api/stock/reservations/",
            "reservationDetail": "/api/stock/reservations/{id}/",
            "issues": "/api/stock/issues/",
            "issueDetail": "/api/stock/issues/{id}/",
            "receivingRecords": "/api/stock/receiving-records/",
            "receivingRecordDetail": "/api/stock/receiving-records/{id}/",
            "suppliers": "/api/stock/suppliers/",
            "brands": "/api/stock/brands/",
            "models": "/api/stock/models/",
            "categories": "/api/stock/categories/",
        },
        "routes": {
            "inventory": reverse("inventory"),
            "availableStock": f"{reverse('inventory')}?status={ProductUnit.STATUS_AVAILABLE}",
            "outOfStock": f"{reverse('inventory')}?stock=out",
            "lowStock": f"{reverse('inventory')}?stock=low",
            "addProduct": reverse("inventory_add_product"),
            "addStockUnit": reverse("inventory_add_stock_unit"),
            "receiveStock": reverse("operations_receive_stock"),
            "createDelivery": reverse("operations_create_delivery"),
            "createReservation": reverse("operations_create_reservation"),
            "createIssue": reverse("operations_create_issue"),
            "suppliers": reverse("suppliers"),
            "receivingRecords": reverse("operations_receiving"),
            "deliveryRecords": reverse("operations_deliveries"),
            "reservationRecords": reverse("operations_reservations"),
            "issueRecords": reverse("operations_issues"),
            "clients": reverse("clients"),
            "assets": reverse("assets"),
            "knowledgeBase": reverse("knowledge_base"),
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
            "searchPlaceholder": "Search products, stock units, deliveries, suppliers, clients...",
        },
        "kpis": [
            {
                "value": _format_count(total_products),
                "detail": _product_count_detail(total_products, "in BIM Stock"),
                "trend": "",
                "href": reverse("inventory"),
                **ui_item("total_products"),
            },
            {
                "value": _format_count(available_stock),
                "detail": f"{_format_count(available_stock)} {_plural(available_stock, 'unit')} ready for issue",
                "trend": "",
                "href": f"{reverse('inventory')}?status={ProductUnit.STATUS_AVAILABLE}",
                **ui_item("available_stock"),
            },
            {
                "value": _format_count(reserved_stock),
                "detail": f"{_format_count(reserved_stock)} {_plural(reserved_stock, 'unit')} pending allocation",
                "trend": "",
                "href": f"{reverse('inventory')}?status={ProductUnit.STATUS_RESERVED}",
                **ui_item("reserved_stock"),
            },
            {
                "value": _format_count(low_stock),
                "detail": _product_count_detail(low_stock, "with low stock"),
                "trend": "",
                "href": f"{reverse('inventory')}?stock=low",
                "todo": "Replace with backend low-stock filter when product stock filters move server-side.",
                **ui_item("low_stock", tone=low_stock_tone),
            },
            {
                "value": _format_count(out_of_stock),
                "detail": _product_count_detail(out_of_stock, "out of stock"),
                "trend": "",
                "href": f"{reverse('inventory')}?stock=out",
                "todo": "Replace with backend out-of-stock filter when product stock filters move server-side.",
                **ui_item("out_of_stock", tone=out_of_stock_tone),
            },
        ],
        "overview": [
            {
                "value": _format_count(supplier_count()),
                "detail": "registered vendor",
                "href": reverse("suppliers"),
                **ui_item("suppliers"),
            },
            {
                "value": _format_count(recent_receiving),
                "detail": "stock entry records",
                "href": reverse("operations_receiving"),
                **ui_item("receiving_records"),
            },
            {
                "value": _format_count(recent_deliveries),
                "detail": "stock exit records",
                "href": reverse("operations_deliveries"),
                **ui_item("delivery_records"),
            },
            {
                "value": "-",
                "detail": "Coming later",
                "href": reverse("clients"),
                "enabled": True,
                **ui_item("clients"),
            },
            disabled_ui_item(
                "assets",
                value="-",
                detail="Coming later",
                href=reverse("assets"),
            ),
            disabled_ui_item(
                "knowledge_base",
                value="-",
                detail="Coming later",
                href=reverse("knowledge_base"),
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
    can_view_stock = user_can_view_stock(user)
    can_use_operations = user_can_use_stock_operations(user)
    low_stock_count, out_of_stock_count = low_stock_counts() if can_view_stock else ("-", 0)
    can_create_delivery = user.has_perm(
        stock_constants.ADD_DELIVERY_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_reservation = user.has_perm(
        stock_constants.ADD_RESERVATION_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_issue = user.has_perm(
        stock_constants.ADD_ISSUE_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)

    metrics = [
        {
            "value": active_product_count() if can_view_stock else "-",
            **ui_item("total_products"),
        },
        {
            "value": available_unit_count() if can_view_stock else "-",
            **ui_item("available_stock"),
        },
        {
            "value": reserved_unit_count() if can_view_stock else "-",
            **ui_item("reserved_stock"),
        },
        {
            "value": low_stock_count,
            **ui_item("low_stock"),
        },
        {
            "value": out_of_stock_count,
            **ui_item("out_of_stock"),
        },
        {
            "value": delivery_record_count() if can_view_stock else "-",
            **ui_item("delivery_records"),
        },
        {
            "label": "Recent Receiving",
            "value": recent_receiving_count() if can_view_stock else "-",
            "tone": "green",
            "note": "Operational receiving records",
        },
    ]

    quick_actions = [
        {
            "href": reverse("inventory_add_product")
            if user.has_perm(stock_constants.ADD_PRODUCT)
            else None,
            "enabled": user.has_perm(stock_constants.ADD_PRODUCT),
            "description": "Register new item to catalogue",
            **ui_item("add_product"),
        },
        {
            "href": reverse("operations_create_delivery")
            if can_create_delivery
            else None,
            "enabled": can_create_delivery,
            "description": "Initiate outbound delivery order",
            **ui_item("create_delivery"),
        },
        {
            "href": reverse("operations_create_reservation")
            if can_create_reservation
            else None,
            "enabled": can_create_reservation,
            "description": "Hold available stock for a person, client, or job",
            **ui_item("create_reservation"),
        },
        {
            "href": reverse("operations_create_issue")
            if can_create_issue
            else None,
            "enabled": can_create_issue,
            "description": "Temporarily issue stock to a person, branch, or site",
            **ui_item("create_issue"),
        },
        {
            "href": reverse("operations_receive_stock")
            if user.has_perm(stock_constants.ADD_PRODUCT_UNIT)
            else None,
            "enabled": user.has_perm(stock_constants.ADD_PRODUCT_UNIT),
            "description": "Record supplier stock receipt",
            **ui_item("receive_stock"),
        },
        {
            "href": reverse("inventory_add_stock_unit")
            if user.has_perm(stock_constants.ADD_PRODUCT_UNIT)
            else None,
            "enabled": user.has_perm(stock_constants.ADD_PRODUCT_UNIT),
            "description": "Manual count or direct unit entry",
            **ui_item("add_stock_unit"),
        },
        {
            "href": None,
            "enabled": False,
            "description": "Coming later",
            **ui_item("add_supplier"),
        },
        {
            "href": None,
            "enabled": False,
            "description": "Coming later",
            **ui_item("add_client"),
        },
    ]

    modules = [
        {
            "description": "Products, stock units, availability",
            "href": reverse("inventory") if can_view_stock else None,
            "enabled": can_view_stock,
            "count": active_product_count() if can_view_stock else None,
            "meta": "products",
            **ui_item("inventory"),
        },
        {
            "description": "Receiving, delivery, reservation, issue, stock history",
            "href": reverse("operations") if can_use_operations else None,
            "enabled": can_use_operations,
            "count": 4,
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

    recent_activity = recent_stock_activity() if can_view_stock else []
    low_stock_alerts_panel = low_stock_alerts() if can_view_stock else []
    recent_deliveries_panel = recent_deliveries() if can_view_stock else []
    recent_receiving_panel = recent_receiving() if can_view_stock else []
    initial_data = _command_center_initial_data(
        request=request,
        user=user,
        metrics=metrics,
        quick_actions=quick_actions,
        modules=modules,
        recent_activity=recent_activity,
        low_stock_alerts=low_stock_alerts_panel,
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
