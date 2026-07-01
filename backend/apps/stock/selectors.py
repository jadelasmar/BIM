from datetime import timedelta

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from . import constants as stock_constants
from .models import DeliveryRecord, Product, ProductUnit, ReceivingRecord, Supplier


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


def recent_receiving_count():
    recent_window = timezone.now() - timedelta(days=30)
    receiving_records = ReceivingRecord.objects.filter(
        crdate__gte=recent_window,
        isactive=True,
    ).count()
    legacy_units = ProductUnit.objects.filter(
        crdate__gte=recent_window,
        isactive=True,
        supplier__isnull=False,
        receiving_item__isnull=True,
    ).count()
    return receiving_records + legacy_units


def supplier_count():
    return Supplier.objects.count()


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


def recent_stock_activity():
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
                "related": delivery_record_summary(delivery),
                "user": _user_display_name(delivery.created_by)
                if delivery.created_by
                else "",
                "date": delivery.delivery_date,
                "status": "Delivered",
                "status_class": "delivered",
                "href": reverse("operations_delivery_detail", kwargs={"pk": delivery.pk}),
            }
        )

    receiving_records = (
        ReceivingRecord.objects.filter(isactive=True)
        .select_related("supplier", "created_by")
        .prefetch_related("items__product")
        .order_by("-crdate")[:8]
    )
    for receiving in receiving_records:
        activity.append(
            {
                "type": "Receiving",
                "reference": receiving.receiving_number,
                "related": receiving_record_summary(receiving),
                "user": _user_display_name(receiving.created_by)
                if receiving.created_by
                else "",
                "date": receiving.received_date,
                "status": "Received",
                "status_class": "received",
                "href": reverse("operations_receiving_detail", kwargs={"pk": receiving.pk}),
            }
        )

    received_unit_filter = Q(supplier__isnull=False)
    fallback_units = (
        ProductUnit.objects.filter(isactive=True)
        .select_related("product", "supplier")
        .filter(
            Q(crdate__isnull=False)
            | Q(sold_date__isnull=False)
        )
        .filter(delivery_item__isnull=True)
        .filter(receiving_item__isnull=True)
        .filter(Q(status=ProductUnit.STATUS_SOLD) | received_unit_filter)
        .order_by("-crdate")[:8]
    )
    for unit in fallback_units:
        if unit.status == ProductUnit.STATUS_SOLD:
            activity_type = "Delivery"
            activity_date = unit.sold_date or unit.crdate
            reference = operational_reference("DLV", activity_date, unit.pk)
            status_label = "Delivered"
            status_class = "delivered"
            href = reverse("operations_delivery_detail", kwargs={"pk": unit.pk})
        else:
            activity_type = "Receiving"
            activity_date = unit.purchase_date or unit.crdate
            reference = operational_reference("RCV", activity_date, unit.pk)
            status_label = "Received"
            status_class = "received"
            href = reverse("operations_receiving_detail", kwargs={"pk": unit.pk})

        activity.append(
            {
                "type": activity_type,
                "reference": reference,
                "related": str(unit.product),
                "user": "",
                "date": activity_date,
                "status": status_label,
                "status_class": status_class,
                "href": href,
            }
        )

    return sorted(
        activity,
        key=lambda item: str(item["date"] or ""),
        reverse=True,
    )[:8]


def low_stock_alerts(limit=4):
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
                "href": reverse("inventory_product_detail", kwargs={"pk": product.pk}),
                "status": "Low Stock",
                "status_class": "low_stock",
            }
        )

        if len(alerts) >= limit:
            break

    return alerts


def recent_deliveries(limit=4):
    deliveries = (
        DeliveryRecord.objects.filter(isactive=True)
        .prefetch_related("items__product")
        .order_by("-delivery_date", "-delivery_number")[:limit]
    )

    return [
        {
            "reference": delivery.delivery_number,
            "title": delivery.customer_name,
            "detail": delivery_record_summary(delivery),
            "href": reverse("operations_delivery_detail", kwargs={"pk": delivery.pk}),
            "date": delivery.delivery_date,
            "status": "Delivered",
            "status_class": "delivered",
        }
        for delivery in deliveries
    ]


def recent_receiving(limit=4):
    records = (
        ReceivingRecord.objects.filter(isactive=True)
        .select_related("supplier")
        .prefetch_related("items__product")
        .order_by("-received_date", "-receiving_number")[:limit]
    )
    items = [
        {
            "reference": receiving.receiving_number,
            "title": receiving.supplier.name if receiving.supplier else "Manual receiving",
            "detail": receiving_record_summary(receiving),
            "href": reverse("operations_receiving_detail", kwargs={"pk": receiving.pk}),
            "date": receiving.received_date,
            "status": "Received",
            "status_class": "received",
        }
        for receiving in records
    ]
    remaining = max(limit - len(items), 0)
    if not remaining:
        return items

    units = (
        ProductUnit.objects.filter(isactive=True, crdate__isnull=False)
        .select_related("product")
        .filter(delivery_item__isnull=True)
        .filter(receiving_item__isnull=True)
        .filter(supplier__isnull=False)
        .exclude(status=ProductUnit.STATUS_SOLD)
        .order_by("-crdate")[:remaining]
    )

    items.extend(
        {
            "reference": operational_reference(
                "RCV",
                unit.purchase_date or unit.crdate,
                unit.pk,
            ),
            "title": str(unit.product),
            "detail": unit.product.category.name if unit.product.category_id else "",
            "href": reverse("operations_receiving_detail", kwargs={"pk": unit.pk}),
            "date": unit.purchase_date or unit.crdate,
            "status": "Received",
            "status_class": "received",
        }
        for unit in units
    )
    return items


def operational_reference(prefix, activity_date, number):
    year = getattr(activity_date, "year", timezone.localdate().year)
    return f"{prefix}-{year}-{number:04d}"


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
