from datetime import date, timedelta

from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone

from . import constants as stock_constants
from .models import (
    Client,
    ClientReturnRecord,
    DeliveryRecord,
    IssueRecord,
    Product,
    ProductUnit,
    ReceivingRecord,
    RemovalRecord,
    RepairRecord,
    ReservationRecord,
    Supplier,
)


def user_can_view_stock(user):
    return user.has_perm(stock_constants.VIEW_PRODUCT) or user.has_perm(
        stock_constants.VIEW_PRODUCT_UNIT
    )


def user_can_use_stock_operations(user):
    return user.has_perm(stock_constants.ADD_PRODUCT_UNIT) or user.has_perm(
        stock_constants.CHANGE_PRODUCT_UNIT
    )


def active_product_count():
    return Product.objects.filter(isactive=True).count()


def available_unit_count():
    return ProductUnit.objects.filter(
        status=ProductUnit.STATUS_AVAILABLE,
        isactive=True,
    ).count()


def reserved_unit_count():
    return ProductUnit.objects.filter(
        status=ProductUnit.STATUS_RESERVED,
        isactive=True,
    ).count()


def delivery_record_count():
    return DeliveryRecord.objects.filter(isactive=True).count()


def pending_reservation_count():
    return ReservationRecord.objects.filter(status=ReservationRecord.STATUS_ACTIVE).count()


def pending_issue_count():
    return IssueRecord.objects.filter(status=IssueRecord.STATUS_ACTIVE).count()


def pending_repair_count():
    return RepairRecord.objects.filter(status=RepairRecord.STATUS_ACTIVE).count()


def recent_receiving_count():
    recent_window = timezone.now() - timedelta(days=30)
    return ReceivingRecord.objects.filter(
        crdate__gte=recent_window,
        isactive=True,
    ).count()


def supplier_count():
    return Supplier.objects.filter(isactive=True).count()


def client_count():
    return Client.objects.filter(isactive=True).count()


def low_stock_counts():
    products = Product.objects.filter(isactive=True)
    low_count = 0
    out_of_stock_count = 0

    for product in products:
        if product.available_units == 0:
            out_of_stock_count += 1
        elif product.is_low_stock:
            low_count += 1

    return low_count, out_of_stock_count


def stock_status_breakdown():
    """Reserved/Issued/Repair counts for the Command Center stock status
    bar chart, plus Available and Total (available + the three bars) as
    separate context figures -- Available is always the dominant status by
    a wide margin, so it's shown as a stat rather than a bar that would
    flatten the other three. "Sold" and "Removed" are deliberately excluded
    entirely: Sold has permanently left inventory (Product Detail's Stock
    Summary panel still shows that count), and Removed is a terminal/
    historical state, not an active stock status alongside Reserved/Issued/
    Repair. This is the only place stock_status_breakdown()'s data is used
    (the chart), so both are dropped from the query itself rather than
    just filtered out of the chart's rendering. "inactive"-status units are
    decommissioned/deactivated stock, not a lifecycle state -- excluded
    here same as everywhere else total_units is computed."""
    counts = {
        row["status"]: row["count"]
        for row in ProductUnit.objects.filter(isactive=True)
        .values("status")
        .annotate(count=Count("id"))
    }
    labels = dict(ProductUnit.STATUS_CHOICES)
    bar_order = (
        ProductUnit.STATUS_RESERVED,
        ProductUnit.STATUS_ISSUED,
        ProductUnit.STATUS_REPAIR,
    )
    bars = [
        {
            "status": status,
            "label": labels[status],
            "count": counts.get(status, 0),
            # Same filtered-inventory link the old per-status KPI cards used
            # (e.g. Reserved Stock) -- each bar/row is now that card's
            # replacement, so it needs the identical href.
            "href": f"{reverse('inventory')}?status={status}",
        }
        for status in bar_order
    ]
    available = counts.get(ProductUnit.STATUS_AVAILABLE, 0)
    total = available + sum(bar["count"] for bar in bars)
    return {"available": available, "total": total, "bars": bars}


RECENT_ACTIVITY_LIMIT = 8


def _items_summary(record, fallback_label):
    # Unlike delivery/receiving items, Reservation/Issue/Repair items get
    # isactive=False once released/returned/resolved -- that only means the
    # unit has moved on to a new claim, not that the record's history should
    # be blanked out. Show every item ever linked to the record so concluded
    # records still display real product info instead of the fallback.
    items = list(record.items.all())
    if not items:
        return fallback_label
    if len(items) == 1:
        return f"1 {items[0].product}"
    return f"{len(items)} stock units"


def recent_stock_activity(user, limit=RECENT_ACTIVITY_LIMIT, offset=0):
    """Merge the most recent record of every stock-movement workflow type
    the given user can view, newest first. When a new record type/model is
    added to the app, add its group here too -- see the standing rule in
    CLAUDE.md (the same one that applies to global_search()).

    `offset`/`limit` support the Command Center "Recent Activity" infinite
    scroll: fetching the top `offset + limit` rows from every type (instead
    of a fixed cap) before merging and slicing is what guarantees the
    global page [offset:offset+limit] is correct regardless of how the
    activity is distributed across types -- see recent_activity_page()."""
    activity = []
    per_type_limit = offset + limit

    if user.has_perm(stock_constants.VIEW_DELIVERY_RECORD):
        deliveries = (
            DeliveryRecord.objects.filter(isactive=True)
            .select_related("created_by", "client")
            .prefetch_related("items__product")
            .order_by("-crdate")[:per_type_limit]
        )
        for delivery in deliveries:
            activity.append(
                {
                    "type": "Delivery",
                    "reference": delivery.delivery_number,
                    "related": delivery_record_summary(delivery),
                    "party": delivery.client.name if delivery.client_id else delivery.customer_name,
                    "user": _user_display_name(delivery.created_by)
                    if delivery.created_by
                    else "",
                    "date": delivery.delivery_date,
                    "status": "Delivered",
                    "status_class": "delivered",
                    "href": reverse("operations_delivery_detail", kwargs={"pk": delivery.pk}),
                }
            )

    if user.has_perm(stock_constants.VIEW_RECEIVING_RECORD):
        receiving_records = (
            ReceivingRecord.objects.filter(isactive=True)
            .select_related("supplier", "created_by")
            .prefetch_related("items__product")
            .order_by("-crdate")[:per_type_limit]
        )
        for receiving in receiving_records:
            activity.append(
                {
                    "type": "Receiving",
                    "reference": receiving.receiving_number,
                    "related": receiving_record_summary(receiving),
                    "party": receiving.supplier.name if receiving.supplier_id else "",
                    "user": _user_display_name(receiving.created_by)
                    if receiving.created_by
                    else "",
                    "date": receiving.received_date,
                    "status": "Received",
                    "status_class": "received",
                    "href": reverse("operations_receiving_detail", kwargs={"pk": receiving.pk}),
                }
            )

    if user.has_perm(stock_constants.VIEW_RESERVATION_RECORD):
        reservations = (
            ReservationRecord.objects.filter(isactive=True)
            .select_related("reserved_by")
            .prefetch_related("items__product")
            .order_by("-reserved_at")[:per_type_limit]
        )
        for reservation in reservations:
            activity.append(
                {
                    "type": "Reservation",
                    "reference": reservation.reservation_number,
                    "related": _items_summary(reservation, "Reservation record"),
                    "party": reservation.reserved_for,
                    "user": _user_display_name(reservation.reserved_by)
                    if reservation.reserved_by
                    else "",
                    "date": reservation.reserved_at.date() if reservation.reserved_at else None,
                    "status": "Reserved",
                    "status_class": "reserved",
                    "href": reverse("operations_reservation_detail", kwargs={"pk": reservation.pk}),
                }
            )

    if user.has_perm(stock_constants.VIEW_ISSUE_RECORD):
        issues = (
            IssueRecord.objects.filter(isactive=True)
            .select_related("issued_by")
            .prefetch_related("items__product")
            .order_by("-issue_date")[:per_type_limit]
        )
        for issue in issues:
            activity.append(
                {
                    "type": "Temporary Assignment",
                    "reference": issue.issue_number,
                    "related": _items_summary(issue, "Temporary assignment record"),
                    "party": issue.issued_to,
                    "user": _user_display_name(issue.issued_by) if issue.issued_by else "",
                    "date": issue.issue_date,
                    "status": "Issued",
                    "status_class": "issued",
                    "href": reverse("operations_issue_detail", kwargs={"pk": issue.pk}),
                }
            )

    if user.has_perm(stock_constants.VIEW_REPAIR_RECORD):
        repairs = (
            RepairRecord.objects.filter(isactive=True)
            .select_related("sent_by")
            .prefetch_related("items__product")
            .order_by("-repair_date")[:per_type_limit]
        )
        for repair in repairs:
            activity.append(
                {
                    "type": "Repair",
                    "reference": repair.repair_number,
                    "related": _items_summary(repair, "Repair record"),
                    "party": "",
                    "user": _user_display_name(repair.sent_by) if repair.sent_by else "",
                    "date": repair.repair_date,
                    "status": "In Repair",
                    "status_class": "repair",
                    "href": reverse("operations_repair_detail", kwargs={"pk": repair.pk}),
                }
            )

    if user.has_perm(stock_constants.VIEW_CLIENT_RETURN_RECORD):
        client_returns = (
            ClientReturnRecord.objects.filter(isactive=True)
            .select_related("received_by", "client")
            .prefetch_related("items__product")
            .order_by("-return_date")[:per_type_limit]
        )
        for client_return in client_returns:
            activity.append(
                {
                    "type": "Client Return",
                    "reference": client_return.return_number,
                    "related": _items_summary(client_return, "Client return record"),
                    "party": client_return.client.name
                    if client_return.client_id
                    else client_return.customer_name,
                    "user": _user_display_name(client_return.received_by)
                    if client_return.received_by
                    else "",
                    "date": client_return.return_date,
                    "status": "Returned",
                    "status_class": "released",
                    "href": reverse(
                        "operations_client_return_detail", kwargs={"pk": client_return.pk}
                    ),
                }
            )

    if user.has_perm(stock_constants.VIEW_REMOVAL_RECORD):
        removals = (
            RemovalRecord.objects.filter(isactive=True)
            .select_related("removed_by")
            .prefetch_related("items__product")
            .order_by("-removal_date")[:per_type_limit]
        )
        for removal in removals:
            activity.append(
                {
                    "type": "Removal",
                    "reference": removal.removal_number,
                    "related": _items_summary(removal, "Removal record"),
                    "party": "",
                    "user": _user_display_name(removal.removed_by)
                    if removal.removed_by
                    else "",
                    "date": removal.removal_date,
                    "status": "Removed",
                    "status_class": "removed",
                    "href": reverse("operations_removal_detail", kwargs={"pk": removal.pk}),
                }
            )

    activity.sort(key=lambda item: str(item["date"] or ""), reverse=True)
    return activity[offset:offset + limit]


def recent_activity_page(user, limit=RECENT_ACTIVITY_LIMIT, offset=0):
    """One page of recent_stock_activity() plus whether another page exists,
    for the Command Center "Recent Activity" infinite scroll."""
    page = recent_stock_activity(user, limit=limit + 1, offset=offset)
    has_more = len(page) > limit
    return page[:limit], has_more


def low_stock_alerts(limit=4):
    products = Product.objects.filter(isactive=True).select_related("category", "model")

    candidates = [
        product
        for product in products
        if product.available_units > 0 and product.is_low_stock
    ]
    # Closest to zero first -- the most urgent restocks lead the preview,
    # not whichever products happen to sort first alphabetically.
    candidates.sort(key=lambda product: (product.available_units, str(product)))

    return [
        {
            "productName": str(product),
            "category": product.category.name if product.category_id else "",
            "availableQuantity": product.available_units,
            "reorderThreshold": product.reorder_stock_level,
            "href": reverse("inventory_product_detail", kwargs={"pk": product.pk}),
            "status": "Low Stock",
            "status_class": "low_stock",
        }
        for product in candidates[:limit]
    ]


def _last_movement_date(product):
    movement = product.stock_movements.order_by("-movement_date", "-crdate").first()
    return movement.movement_date if movement else date.min


def out_of_stock_products(limit=4):
    products = Product.objects.filter(isactive=True).select_related("category", "model")

    candidates = [product for product in products if product.available_units == 0]
    # Most-recently-gone-out-of-stock first. There's no dedicated "went out
    # of stock at" timestamp and no sales/demand history to rank by instead,
    # so the latest StockMovement touching the product (received, sold,
    # removed, etc.) is the best available proxy for "when did this
    # actually run out" -- a product with fresher history is more likely to
    # need immediate attention than one that's been sitting empty for a
    # long time. Products with no movement history at all sort last.
    candidates.sort(key=_last_movement_date, reverse=True)

    return [
        {
            "productName": str(product),
            "category": product.category.name if product.category_id else "",
            "href": reverse("inventory_product_detail", kwargs={"pk": product.pk}),
            "status": "Out of Stock",
            "status_class": "out_of_stock",
        }
        for product in candidates[:limit]
    ]


def delivery_record_summary(delivery):
    items = [item for item in delivery.items.all() if item.isactive]
    if not items:
        return "Delivery record"
    if len(items) == 1:
        return f"1 {items[0].product}"
    return f"{len(items)} stock units"


def receiving_record_summary(receiving):
    items = [item for item in receiving.items.all() if item.isactive]
    total_quantity = sum(item.quantity for item in items)
    if not items:
        return "Receiving record"
    if total_quantity == 1:
        return f"1 {items[0].product}"
    return f"{total_quantity} stock units"


def _user_display_name(user):
    full_name = user.get_full_name().strip()
    return full_name or user.get_username()


GLOBAL_SEARCH_MIN_QUERY_LENGTH = 2
GLOBAL_SEARCH_RESULT_LIMIT = 5


def _search_group(key, label, queryset, mapper, limit):
    total = queryset.count()
    if not total:
        return None
    return {
        "key": key,
        "label": label,
        "count": total,
        "results": [mapper(obj) for obj in queryset[:limit]],
    }


def global_search(user, query, limit=GLOBAL_SEARCH_RESULT_LIMIT):
    """Search across every record type the given user can view.

    Every group here corresponds to one searchable model. When a new record
    type/model is added to the app, add its group here too -- see the
    standing rule in CLAUDE.md.
    """
    query = (query or "").strip()
    groups = []
    if len(query) < GLOBAL_SEARCH_MIN_QUERY_LENGTH:
        return groups

    if user.has_perm(stock_constants.VIEW_PRODUCT):
        matches = Product.objects.filter(isactive=True).filter(
            Q(descript__icontains=query)
            | Q(sku__icontains=query)
            | Q(barcode__icontains=query)
        ).order_by("descript")
        group = _search_group(
            "products",
            "Products",
            matches,
            lambda product: {
                "id": product.pk,
                "title": product.descript,
                "subtitle": product.sku,
                "href": reverse("inventory_product_detail", kwargs={"pk": product.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_SUPPLIER):
        matches = Supplier.objects.filter(isactive=True).filter(
            Q(name__icontains=query) | Q(contact_person__icontains=query)
        ).order_by("name")
        group = _search_group(
            "suppliers",
            "Suppliers",
            matches,
            lambda supplier: {
                "id": supplier.pk,
                "title": supplier.name,
                "subtitle": supplier.contact_person or supplier.phone or "",
                "href": reverse("supplier_detail", kwargs={"pk": supplier.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_CLIENT):
        matches = Client.objects.filter(isactive=True).filter(
            Q(name__icontains=query) | Q(contact_person__icontains=query)
        ).order_by("name")
        group = _search_group(
            "clients",
            "Clients",
            matches,
            lambda client: {
                "id": client.pk,
                "title": client.name,
                "subtitle": client.contact_person or client.phone or "",
                "href": reverse("client_detail", kwargs={"pk": client.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_RECEIVING_RECORD):
        matches = ReceivingRecord.objects.select_related("supplier").filter(
            Q(receiving_number__icontains=query)
            | Q(po_number__icontains=query)
            | Q(supplier_invoice_number__icontains=query)
        ).order_by("-received_date", "-receiving_number")
        group = _search_group(
            "receiving_records",
            "Receiving Records",
            matches,
            lambda receiving: {
                "id": receiving.pk,
                "title": receiving.receiving_number,
                "subtitle": receiving.supplier.name if receiving.supplier_id else "Manual entry",
                "href": reverse("operations_receiving_detail", kwargs={"pk": receiving.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_DELIVERY_RECORD):
        matches = DeliveryRecord.objects.select_related("client").filter(
            Q(delivery_number__icontains=query) | Q(invoice_number__icontains=query)
        ).order_by("-delivery_date", "-delivery_number")
        group = _search_group(
            "delivery_records",
            "Delivery Records",
            matches,
            lambda delivery: {
                "id": delivery.pk,
                "title": delivery.delivery_number,
                "subtitle": delivery.client.name if delivery.client_id else delivery.customer_name,
                "href": reverse("operations_delivery_detail", kwargs={"pk": delivery.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_RESERVATION_RECORD):
        matches = ReservationRecord.objects.filter(
            Q(reservation_number__icontains=query)
            | Q(reserved_for__icontains=query)
            | Q(reason__icontains=query)
        ).order_by("-reserved_at", "-reservation_number")
        group = _search_group(
            "reservations",
            "Reservations",
            matches,
            lambda reservation: {
                "id": reservation.pk,
                "title": reservation.reservation_number,
                "subtitle": reservation.reserved_for,
                "href": reverse("operations_reservation_detail", kwargs={"pk": reservation.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_ISSUE_RECORD):
        matches = IssueRecord.objects.filter(
            Q(issue_number__icontains=query)
            | Q(issued_to__icontains=query)
            | Q(reason__icontains=query)
        ).order_by("-issue_date", "-issue_number")
        group = _search_group(
            "temporary_assignments",
            "Temporary Assignments",
            matches,
            lambda issue: {
                "id": issue.pk,
                "title": issue.issue_number,
                "subtitle": issue.issued_to,
                "href": reverse("operations_issue_detail", kwargs={"pk": issue.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_REPAIR_RECORD):
        matches = RepairRecord.objects.filter(
            Q(repair_number__icontains=query)
            | Q(repair_reason__icontains=query)
            | Q(technician__icontains=query)
        ).order_by("-repair_date", "-repair_number")
        group = _search_group(
            "repairs",
            "Repairs",
            matches,
            lambda repair: {
                "id": repair.pk,
                "title": repair.repair_number,
                "subtitle": repair.repair_reason,
                "href": reverse("operations_repair_detail", kwargs={"pk": repair.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_REMOVAL_RECORD):
        matches = RemovalRecord.objects.filter(
            Q(removal_number__icontains=query)
            | Q(reason__icontains=query)
            | Q(notes__icontains=query)
        ).order_by("-removal_date", "-removal_number")
        group = _search_group(
            "removals",
            "Removals",
            matches,
            lambda removal: {
                "id": removal.pk,
                "title": removal.removal_number,
                "subtitle": removal.get_reason_display(),
                "href": reverse("operations_removal_detail", kwargs={"pk": removal.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    if user.has_perm(stock_constants.VIEW_CLIENT_RETURN_RECORD):
        matches = ClientReturnRecord.objects.select_related("client").filter(
            Q(return_number__icontains=query)
            | Q(client__name__icontains=query)
            | Q(customer_name__icontains=query)
            | Q(received_from__icontains=query)
            | Q(reason__icontains=query)
        ).order_by("-return_date", "-return_number")
        group = _search_group(
            "client_returns",
            "Client Returns",
            matches,
            lambda client_return: {
                "id": client_return.pk,
                "title": client_return.return_number,
                "subtitle": client_return.client.name if client_return.client_id else client_return.customer_name,
                "href": reverse("operations_client_return_detail", kwargs={"pk": client_return.pk}),
            },
            limit,
        )
        if group:
            groups.append(group)

    return groups
