"""Command Center cards and Needs Attention rows for the stock app's modules.

Each provider takes the user and returns {"section": {...} or None,
"attention": [...]}, already limited to what that user is allowed to see.
apps.core.dashboard runs them in order. A new module adds its own provider
there -- see the standing rule in CLAUDE.md.

Section: {key, title, icon, tone, href, linkLabel, stats: [{key, label, value,
href, tone}], and for Stock also headline + bars}. Attention row: {key, module,
count, label, href, tone ("danger" or "warning"), icon}. Stat keys and the
attention `module` are stable identifiers other pages look up (the Operations
page shows its own rows and per-workflow counts from them).
"""

from django.urls import reverse

from . import constants as stock_constants
from .selectors import (
    STALE_RECORD_DAYS,
    active_product_count,
    client_count,
    client_upgrade_needed_count,
    delivery_record_count,
    long_held_reservation_count,
    long_open_repair_count,
    low_stock_counts,
    overdue_client_upgrade_count,
    overdue_issue_count,
    pending_issue_count,
    pending_repair_count,
    pending_reservation_count,
    recent_receiving_count,
    repairs_without_vendor_count,
    stock_status_breakdown,
    supplier_count,
    user_can_use_stock_operations,
    user_can_view_stock,
)


def _attention(module, key, count, one, many, href, tone, icon):
    return {
        "key": key,
        "module": module,
        "count": count,
        "label": one if count == 1 else many,
        "href": href,
        "tone": tone,
        "icon": icon,
    }


def _stat(key, label, value, href, tone=None):
    return {"key": key, "label": label, "value": value, "href": href, "tone": tone}


def stock_dashboard(user):
    if not user_can_view_stock(user):
        return {"section": None, "attention": []}

    inventory = reverse("inventory")
    low, out = low_stock_counts()
    breakdown = stock_status_breakdown()

    attention = []
    if out:
        attention.append(
            _attention(
                "stock", "out_of_stock", out, "product is out of stock", "products are out of stock",
                f"{inventory}?stock=out", "danger", "package-x",
            )
        )
    if low:
        attention.append(
            _attention(
                "stock", "low_stock", low, "product is low on stock", "products are low on stock",
                f"{inventory}?stock=low", "warning", "triangle-alert",
            )
        )

    section = {
        "key": "stock",
        "title": "Stock",
        "icon": "boxes",
        "tone": "blue",
        "href": inventory,
        "linkLabel": "Open Inventory",
        "headline": {
            "value": breakdown["available"],
            "label": f"available of {breakdown['total']} in stock",
            "href": f"{inventory}?status=available",
        },
        "bars": breakdown["bars"],
        "stats": [
            _stat("products", "Products", active_product_count(), inventory),
            _stat("low_stock", "Low stock", low, f"{inventory}?stock=low", "warning" if low else None),
            _stat("out_of_stock", "Out of stock", out, f"{inventory}?stock=out", "danger" if out else None),
        ],
    }
    return {"section": section, "attention": attention}


def operations_dashboard(user):
    stats = []
    attention = []
    pending = reverse("operations_pending")

    if user.has_perm(stock_constants.VIEW_RESERVATION_RECORD):
        reservations = reverse("operations_reservations")
        stats.append(_stat("active_reservations", "Active reservations", pending_reservation_count(), reservations))
        held = long_held_reservation_count()
        if held:
            attention.append(
                _attention(
                    "operations", "long_held_reservations", held,
                    f"reservation held more than {STALE_RECORD_DAYS} days",
                    f"reservations held more than {STALE_RECORD_DAYS} days",
                    reservations, "warning", "clock-3",
                )
            )

    if user.has_perm(stock_constants.VIEW_ISSUE_RECORD):
        stats.append(_stat("active_assignments", "On temporary assignment", pending_issue_count(), reverse("operations_issues")))
        overdue = overdue_issue_count()
        if overdue:
            attention.append(
                _attention(
                    "operations", "overdue_assignments", overdue,
                    "temporary assignment is overdue", "temporary assignments are overdue",
                    pending, "danger", "user-check",
                )
            )

    if user.has_perm(stock_constants.VIEW_REPAIR_RECORD):
        repairs = reverse("operations_repairs")
        stats.append(_stat("open_repairs", "Open repairs", pending_repair_count(), repairs))
        no_vendor = repairs_without_vendor_count()
        if no_vendor:
            attention.append(
                _attention(
                    "operations", "repairs_without_supplier", no_vendor,
                    "repair has no supplier", "repairs have no supplier",
                    pending, "warning", "wrench",
                )
            )
        long_open = long_open_repair_count()
        if long_open:
            attention.append(
                _attention(
                    "operations", "long_open_repairs", long_open,
                    f"repair open more than {STALE_RECORD_DAYS} days",
                    f"repairs open more than {STALE_RECORD_DAYS} days",
                    repairs, "warning", "wrench",
                )
            )

    if user.has_perm(stock_constants.VIEW_RECEIVING_RECORD):
        stats.append(_stat("received_30_days", "Received, last 30 days", recent_receiving_count(), reverse("operations_receiving")))

    if user.has_perm(stock_constants.VIEW_DELIVERY_RECORD):
        stats.append(_stat("deliveries", "Deliveries", delivery_record_count(), reverse("operations_deliveries")))

    if not stats:
        return {"section": None, "attention": attention}

    section = {
        "key": "operations",
        "title": "Operations",
        "icon": "workflow",
        "tone": "green",
        "href": reverse("operations") if user_can_use_stock_operations(user) else None,
        "linkLabel": "Open Operations",
        "stats": stats,
    }
    return {"section": section, "attention": attention}


def clients_dashboard(user):
    stats = []
    attention = []

    if user.has_perm(stock_constants.VIEW_CLIENT):
        stats.append(_stat("clients", "Clients", client_count(), reverse("clients")))

    if user.has_perm(stock_constants.VIEW_SUPPLIER):
        stats.append(_stat("suppliers", "Suppliers", supplier_count(), reverse("suppliers")))

    if user.has_perm(stock_constants.VIEW_CLIENT_UPGRADE_RECORD):
        upgrades = reverse("operations_client_upgrades")
        needed = client_upgrade_needed_count()
        stats.append(
            _stat("upgrades_needed", "Need an upgrade", needed, f"{upgrades}?filter=needs_upgrade", "warning" if needed else None)
        )
        overdue = overdue_client_upgrade_count()
        if overdue:
            attention.append(
                _attention(
                    "clients", "overdue_client_upgrades", overdue,
                    "client upgrade is past its planned date",
                    "client upgrades are past their planned date",
                    f"{upgrades}?filter=overdue", "danger", "refresh-cw",
                )
            )

    if not stats:
        return {"section": None, "attention": attention}

    section = {
        "key": "clients",
        "title": "Clients & Suppliers",
        "icon": "clients",
        "tone": "cyan",
        "href": reverse("clients") if user.has_perm(stock_constants.VIEW_CLIENT) else None,
        "linkLabel": "Open Clients",
        "stats": stats,
    }
    return {"section": section, "attention": attention}
