from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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
    client_count,
    delivery_record_count,
    low_stock_alerts,
    low_stock_counts,
    pending_issue_count,
    pending_repair_count,
    pending_reservation_count,
    recent_deliveries,
    recent_receiving,
    recent_receiving_count,
    recent_stock_activity,
    reserved_unit_count,
    supplier_count,
    user_can_use_stock_operations,
    user_can_view_stock,
)


WRITE_PAGE_PERMISSIONS = {
    "inventory_add_product": (stock_constants.ADD_PRODUCT,),
    "inventory_add_stock_unit": (stock_constants.ADD_PRODUCT_UNIT,),
    "operations_receive_stock": (
        stock_constants.ADD_RECEIVING_RECORD,
        stock_constants.ADD_PRODUCT_UNIT,
    ),
    "operations_create_delivery": (
        stock_constants.ADD_DELIVERY_RECORD,
        stock_constants.CHANGE_PRODUCT_UNIT,
    ),
    "operations_create_reservation": (
        stock_constants.ADD_RESERVATION_RECORD,
        stock_constants.CHANGE_PRODUCT_UNIT,
    ),
    "operations_create_issue": (
        stock_constants.ADD_ISSUE_RECORD,
        stock_constants.CHANGE_PRODUCT_UNIT,
    ),
    "operations_create_repair": (
        stock_constants.ADD_REPAIR_RECORD,
        stock_constants.CHANGE_PRODUCT_UNIT,
    ),
    "operations_create_removal": (
        stock_constants.ADD_REMOVAL_RECORD,
        stock_constants.CHANGE_PRODUCT_UNIT,
    ),
    "operations_create_client_return": (
        stock_constants.ADD_CLIENT_RETURN_RECORD,
        stock_constants.CHANGE_PRODUCT_UNIT,
    ),
    "supplier_new": (stock_constants.ADD_SUPPLIER,),
    "client_new": (stock_constants.ADD_CLIENT,),
}


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


def _pending_actions_detail(reservations, issues, repairs):
    counts = (reservations, issues, repairs)
    if not all(isinstance(count, int) for count in counts):
        return "Operations data unavailable"

    parts = []
    if reservations:
        parts.append(f"{_format_count(reservations)} {_plural(reservations, 'reservation')}")
    if issues:
        parts.append(f"{_format_count(issues)} {_plural(issues, 'temporary assignment')}")
    if repairs:
        parts.append(f"{_format_count(repairs)} {_plural(repairs, 'repair')}")

    return ", ".join(parts) if parts else "Nothing awaiting action"


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
    pending_reservations,
    pending_issues,
    pending_repairs,
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
    pending_counts = (pending_reservations, pending_issues, pending_repairs)
    pending_actions_total = (
        sum(pending_counts) if all(isinstance(count, int) for count in pending_counts) else "-"
    )

    can_create_delivery = user.has_perm(
        stock_constants.ADD_DELIVERY_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_reservation = user.has_perm(
        stock_constants.ADD_RESERVATION_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_issue = user.has_perm(
        stock_constants.ADD_ISSUE_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_repair = user.has_perm(
        stock_constants.ADD_REPAIR_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_removal = user.has_perm(
        stock_constants.ADD_REMOVAL_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_client_return = user.has_perm(
        stock_constants.ADD_CLIENT_RETURN_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_receive_stock = user.has_perm(
        stock_constants.ADD_RECEIVING_RECORD
    ) and user.has_perm(stock_constants.ADD_PRODUCT_UNIT)
    can_change_product_unit = user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)

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
        "permissions": {
            "canCreateProduct": user.has_perm(stock_constants.ADD_PRODUCT),
            "canEditProduct": user.has_perm(stock_constants.CHANGE_PRODUCT),
            "canAddStockUnit": user.has_perm(stock_constants.ADD_PRODUCT_UNIT),
            "canEditStockUnit": can_change_product_unit,
            "canReceiveStock": can_receive_stock,
            "canEditReceiving": user.has_perm(stock_constants.CHANGE_RECEIVING_RECORD),
            "canCancelReceiving": user.has_perm(stock_constants.CHANGE_RECEIVING_RECORD)
            and can_change_product_unit,
            "canCreateDelivery": can_create_delivery,
            "canEditDelivery": user.has_perm(stock_constants.CHANGE_DELIVERY_RECORD),
            "canCancelDelivery": user.has_perm(stock_constants.CHANGE_DELIVERY_RECORD)
            and can_change_product_unit,
            "canCreateReservation": can_create_reservation,
            "canReleaseReservation": user.has_perm(
                stock_constants.CHANGE_RESERVATION_RECORD
            )
            and can_change_product_unit,
            "canCancelReservation": user.has_perm(
                stock_constants.CHANGE_RESERVATION_RECORD
            )
            and can_change_product_unit,
            "canCreateIssue": can_create_issue,
            "canReturnIssue": user.has_perm(stock_constants.CHANGE_ISSUE_RECORD)
            and can_change_product_unit,
            "canCreateRepair": can_create_repair,
            "canResolveRepair": user.has_perm(stock_constants.CHANGE_REPAIR_RECORD)
            and can_change_product_unit,
            "canCreateRemoval": can_create_removal,
            "canCreateClientReturn": can_create_client_return,
            "canCreateSupplier": user.has_perm(stock_constants.ADD_SUPPLIER),
            "canEditSupplier": user.has_perm(stock_constants.CHANGE_SUPPLIER),
            "canCreateClient": user.has_perm(stock_constants.ADD_CLIENT),
            "canEditClient": user.has_perm(stock_constants.CHANGE_CLIENT),
            "canViewMovementHistory": user.has_perm(stock_constants.VIEW_STOCK_MOVEMENT),
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
            "search": "/api/stock/search/",
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
            "repairs": "/api/stock/repairs/",
            "repairDetail": "/api/stock/repairs/{id}/",
            "removals": "/api/stock/removals/",
            "removalDetail": "/api/stock/removals/{id}/",
            "clientReturns": "/api/stock/client-returns/",
            "clientReturnDetail": "/api/stock/client-returns/{id}/",
            "receivingRecords": "/api/stock/receiving-records/",
            "receivingRecordDetail": "/api/stock/receiving-records/{id}/",
            "suppliers": "/api/stock/suppliers/",
            "clients": "/api/stock/clients/",
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
            "createRepair": reverse("operations_create_repair"),
            "createRemoval": reverse("operations_create_removal"),
            "createClientReturn": reverse("operations_create_client_return"),
            "suppliers": reverse("suppliers"),
            "supplierNew": reverse("supplier_new"),
            "receivingRecords": reverse("operations_receiving"),
            "deliveryRecords": reverse("operations_deliveries"),
            "reservationRecords": reverse("operations_reservations"),
            "issueRecords": reverse("operations_issues"),
            "repairRecords": reverse("operations_repairs"),
            "removalRecords": reverse("operations_removals"),
            "clientReturnRecords": reverse("operations_client_returns"),
            "clients": reverse("clients"),
            "clientNew": reverse("client_new"),
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
        "kpis": [
            {
                "value": _format_count(total_products),
                "detail": "Active in catalogue",
                "trend": "",
                "href": reverse("inventory"),
                **ui_item("total_products"),
            },
            {
                "value": _format_count(available_stock),
                "detail": "Ready to allocate",
                "trend": "",
                "href": f"{reverse('inventory')}?status={ProductUnit.STATUS_AVAILABLE}",
                **ui_item("available_stock"),
            },
            {
                "value": _format_count(reserved_stock),
                "detail": "On hold, awaiting pickup or delivery",
                "trend": "",
                "href": f"{reverse('inventory')}?status={ProductUnit.STATUS_RESERVED}",
                **ui_item("reserved_stock"),
            },
            {
                "value": _format_count(low_stock),
                "detail": "Review items" if isinstance(low_stock, int) and low_stock > 0 else "None right now",
                "trend": "",
                "href": f"{reverse('inventory')}?stock=low",
                "todo": "Replace with backend low-stock filter when product stock filters move server-side.",
                **ui_item("low_stock", tone=low_stock_tone),
            },
            {
                "value": _format_count(out_of_stock),
                "detail": "Reorder needed" if isinstance(out_of_stock, int) and out_of_stock > 0 else "None right now",
                "trend": "",
                "href": f"{reverse('inventory')}?stock=out",
                "todo": "Replace with backend out-of-stock filter when product stock filters move server-side.",
                **ui_item("out_of_stock", tone=out_of_stock_tone),
            },
            {
                "value": _format_count(pending_actions_total),
                "detail": _pending_actions_detail(pending_reservations, pending_issues, pending_repairs),
                "trend": "",
                "href": operations_href,
                **ui_item("pending_actions"),
            },
        ],
        "overview": [
            {
                "value": _format_count(supplier_count()),
                "detail": "active suppliers",
                "href": reverse("suppliers"),
                "enabled": True,
                **ui_item("suppliers"),
            },
            {
                "value": _format_count(recent_receiving),
                "detail": "Last 30 days",
                "href": reverse("operations_receiving"),
                **ui_item("receiving_records"),
            },
            {
                "value": _format_count(recent_deliveries),
                "detail": "All-time total",
                "href": reverse("operations_deliveries"),
                **ui_item("delivery_records"),
            },
            {
                "value": _format_count(client_count()),
                "detail": "active clients",
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
    pending_reservations = pending_reservation_count() if can_view_stock else "-"
    pending_issues = pending_issue_count() if can_view_stock else "-"
    pending_repairs = pending_repair_count() if can_view_stock else "-"
    can_create_delivery = user.has_perm(
        stock_constants.ADD_DELIVERY_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_reservation = user.has_perm(
        stock_constants.ADD_RESERVATION_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_issue = user.has_perm(
        stock_constants.ADD_ISSUE_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_repair = user.has_perm(
        stock_constants.ADD_REPAIR_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_removal = user.has_perm(
        stock_constants.ADD_REMOVAL_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_create_client_return = user.has_perm(
        stock_constants.ADD_CLIENT_RETURN_RECORD
    ) and user.has_perm(stock_constants.CHANGE_PRODUCT_UNIT)
    can_receive_stock = user.has_perm(
        stock_constants.ADD_RECEIVING_RECORD
    ) and user.has_perm(stock_constants.ADD_PRODUCT_UNIT)

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
            "description": "Temporarily assign stock to a person that is expected to come back",
            **ui_item("create_issue"),
        },
        {
            "href": reverse("operations_create_repair")
            if can_create_repair
            else None,
            "enabled": can_create_repair,
            "description": "Move available stock into repair or testing",
            **ui_item("create_repair"),
        },
        {
            "href": reverse("operations_create_removal")
            if can_create_removal
            else None,
            "enabled": can_create_removal,
            "description": "Permanently remove a unit for damage, loss, theft, or write-off",
            **ui_item("create_removal"),
        },
        {
            "href": reverse("operations_create_client_return")
            if can_create_client_return
            else None,
            "enabled": can_create_client_return,
            "description": "Record sold stock returned by a client",
            **ui_item("create_client_return"),
        },
        {
            "href": reverse("operations_receive_stock")
            if can_receive_stock
            else None,
            "enabled": can_receive_stock,
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
            "href": reverse("supplier_new")
            if user.has_perm(stock_constants.ADD_SUPPLIER)
            else None,
            "enabled": user.has_perm(stock_constants.ADD_SUPPLIER),
            "description": "Create supplier master data",
            **ui_item("add_supplier"),
        },
        {
            "href": reverse("client_new")
            if user.has_perm(stock_constants.ADD_CLIENT)
            else None,
            "enabled": user.has_perm(stock_constants.ADD_CLIENT),
            "description": "Create client master data",
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
            "description": "Receiving, delivery, reservation, temporary assignment, repair, unit removal, client returns, stock history",
            "href": reverse("operations") if can_use_operations else None,
            "enabled": can_use_operations,
            "count": 7,
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

    recent_activity = recent_stock_activity(user) if can_view_stock else []
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
        pending_reservations=pending_reservations,
        pending_issues=pending_issues,
        pending_repairs=pending_repairs,
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
    route_name = request.resolver_match.url_name
    required_permissions = WRITE_PAGE_PERMISSIONS.get(route_name, ())
    if required_permissions and not all(
        request.user.has_perm(permission) for permission in required_permissions
    ):
        raise PermissionDenied

    initial_data = _build_command_center_initial_data(request)

    context = {
        "initial_data": initial_data,
        "vite_dev_server": settings.BIM_VITE_DEV_SERVER,
    }

    return render(request, "bim/react_app.html", context)
