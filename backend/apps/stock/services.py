from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    DeliveryItem,
    DeliveryRecord,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    StockMovement,
)


def _clean_serial_numbers(serial_numbers):
    if not serial_numbers:
        return []

    cleaned = [str(serial).strip() for serial in serial_numbers if str(serial).strip()]
    if len(cleaned) != len(set(cleaned)):
        raise ValidationError("Serial numbers must be unique within a receiving item.")
    return cleaned


def create_stock_movement(
    *,
    product_unit,
    movement_type,
    from_status="",
    to_status="",
    reason="",
    notes="",
    performed_by=None,
    movement_date=None,
    receiving_record=None,
    delivery_record=None,
    reference="",
):
    return StockMovement.objects.create(
        product_unit=product_unit,
        product=product_unit.product,
        movement_type=movement_type,
        from_status=from_status or "",
        to_status=to_status or "",
        reason=(reason or "").strip()[:150],
        notes=notes or "",
        performed_by=performed_by,
        movement_date=movement_date or timezone.localdate(),
        receiving_record=receiving_record,
        delivery_record=delivery_record,
        reference=(reference or "").strip()[:150],
    )


def _create_receiving_item(receiving, supplier, received_date, item_data, created_by=None):
    product = item_data["product"]
    quantity = int(item_data.get("quantity") or 1)
    serial_numbers = _clean_serial_numbers(item_data.get("serial_numbers"))
    cost = item_data.get("cost", 0)
    notes = item_data.get("notes", "")
    product_unit = item_data.get("product_unit")

    if quantity < 1:
        raise ValidationError("Receiving item quantity must be at least 1.")
    if product_unit and serial_numbers:
        raise ValidationError("Use either product_unit or serial_numbers, not both.")
    if product_unit:
        ReceivingItem.objects.create(
            receiving=receiving,
            product=product_unit.product,
            product_unit=product_unit,
            quantity=1,
            cost=cost,
            notes=notes,
        )
        create_stock_movement(
            product_unit=product_unit,
            movement_type=StockMovement.TYPE_RECEIVED,
            from_status=product_unit.status,
            to_status=product_unit.status,
            reason="Linked to receiving record",
            notes=notes,
            performed_by=created_by,
            movement_date=received_date,
            receiving_record=receiving,
            reference=receiving.receiving_number,
        )
        return
    if serial_numbers and len(serial_numbers) != quantity:
        raise ValidationError("Serial number count must match quantity.")

    if serial_numbers:
        existing_serials = set(
            ProductUnit.objects.filter(serial_number__in=serial_numbers).values_list(
                "serial_number",
                flat=True,
            )
        )
        if existing_serials:
            raise ValidationError(
                "Serial numbers already exist: "
                + ", ".join(sorted(existing_serials))
            )

        for serial_number in serial_numbers:
            unit = ProductUnit.objects.create(
                product=product,
                serial_number=serial_number,
                status=ProductUnit.STATUS_AVAILABLE,
                supplier=supplier,
                cost=cost,
                purchase_date=received_date,
                notes=notes,
            )
            ReceivingItem.objects.create(
                receiving=receiving,
                product=product,
                product_unit=unit,
                quantity=1,
                serial_number=serial_number,
                cost=cost,
                notes=notes,
            )
            create_stock_movement(
                product_unit=unit,
                movement_type=StockMovement.TYPE_RECEIVED,
                from_status="",
                to_status=ProductUnit.STATUS_AVAILABLE,
                reason="Received stock",
                notes=notes,
                performed_by=created_by,
                movement_date=received_date,
                receiving_record=receiving,
                reference=receiving.receiving_number,
            )
        return

    ReceivingItem.objects.create(
        receiving=receiving,
        product=product,
        quantity=quantity,
        cost=cost,
        notes=notes,
    )


@transaction.atomic
def create_receiving_record(
    *,
    items,
    supplier=None,
    reference_number="",
    received_date=None,
    notes="",
    created_by=None,
):
    if not items:
        raise ValidationError("At least one receiving item is required.")

    receiving = ReceivingRecord.objects.create(
        supplier=supplier,
        reference_number=(reference_number or "").strip(),
        received_date=received_date or timezone.localdate(),
        notes=notes,
        created_by=created_by,
    )

    for item_data in items:
        _create_receiving_item(
            receiving=receiving,
            supplier=supplier,
            received_date=receiving.received_date,
            item_data=item_data,
            created_by=created_by,
        )

    return receiving


@transaction.atomic
def create_delivery_record(
    *,
    unit_ids,
    customer_name,
    receiver_name="",
    delivery_date=None,
    notes="",
    created_by=None,
    status=DeliveryRecord.STATUS_COMPLETED,
):
    delivery = DeliveryRecord.objects.create(
        customer_name=(customer_name or "").strip(),
        receiver_name=(receiver_name or "").strip(),
        delivery_date=delivery_date or timezone.localdate(),
        notes=notes,
        status=status,
        created_by=created_by,
    )
    units = (
        ProductUnit.objects.select_related("product")
        .filter(pk__in=unit_ids)
        .order_by("product__descript", "serial_number")
    )
    for unit in units:
        from_status = unit.status
        DeliveryItem.objects.create(
            delivery=delivery,
            product_unit=unit,
            product=unit.product,
        )
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = delivery.delivery_date
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_DELIVERED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_SOLD,
            reason="Delivered stock",
            notes=notes,
            performed_by=created_by,
            movement_date=delivery.delivery_date,
            delivery_record=delivery,
            reference=delivery.delivery_number,
        )

    return delivery


def _unit_has_delivery(unit):
    try:
        unit.delivery_item
    except ObjectDoesNotExist:
        return False
    return True


def _unit_can_be_corrected(unit):
    return (
        unit.isactive
        and unit.status == ProductUnit.STATUS_AVAILABLE
        and not _unit_has_delivery(unit)
    )


def _delivery_unit_can_be_corrected(item):
    unit = item.product_unit
    if not item.isactive or not unit:
        return False
    try:
        current_delivery_item = unit.delivery_item
    except ObjectDoesNotExist:
        return False
    return (
        unit.isactive
        and unit.status == ProductUnit.STATUS_SOLD
        and current_delivery_item.pk == item.pk
    )


@transaction.atomic
def update_receiving_record_header(
    receiving,
    *,
    supplier=None,
    reference_number=None,
    received_date=None,
    notes=None,
    items=None,
):
    if receiving.status == ReceivingRecord.STATUS_CANCELLED:
        raise ValidationError("Cancelled receiving records cannot be edited.")

    if supplier is not None:
        receiving.supplier = supplier
    if reference_number is not None:
        receiving.reference_number = reference_number.strip()
    if received_date is not None:
        receiving.received_date = received_date
    if notes is not None:
        receiving.notes = notes
    receiving.save(
        update_fields=(
            "supplier",
            "reference_number",
            "received_date",
            "notes",
        )
    )

    for item_data in items or []:
        item_id = item_data.get("id")
        if not item_id:
            continue
        try:
            item = receiving.items.select_related("product_unit").get(pk=item_id)
        except ReceivingItem.DoesNotExist:
            continue

        update_fields = []
        if "cost" in item_data:
            item.cost = item_data["cost"]
            update_fields.append("cost")
        if "notes" in item_data:
            item.notes = item_data["notes"]
            update_fields.append("notes")
        if update_fields:
            item.save(update_fields=update_fields)

    for item in receiving.items.select_related("product_unit"):
        unit = item.product_unit
        if unit and _unit_can_be_corrected(unit):
            unit.supplier = receiving.supplier
            unit.purchase_date = receiving.received_date
            unit.cost = item.cost
            unit.save(update_fields=("supplier", "purchase_date", "cost"))

    return receiving


@transaction.atomic
def cancel_receiving_record(receiving, *, cancelled_by=None, cancel_reason=""):
    if receiving.status == ReceivingRecord.STATUS_CANCELLED:
        return receiving

    items = list(receiving.items.select_related("product_unit"))
    linked_units = [item.product_unit for item in items if item.product_unit_id]
    blocked_units = [
        unit.serial_number
        for unit in linked_units
        if not _unit_can_be_corrected(unit)
    ]
    if blocked_units:
        raise ValidationError(
            "Cannot cancel receiving record because these stock units are already used: "
            + ", ".join(sorted(blocked_units))
        )

    receiving.status = ReceivingRecord.STATUS_CANCELLED
    receiving.isactive = False
    receiving.cancel_reason = (cancel_reason or "").strip()
    receiving.cancelled_at = timezone.now()
    receiving.cancelled_by = cancelled_by
    receiving.save(
        update_fields=(
            "status",
            "isactive",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
        )
    )

    for item in items:
        if item.isactive:
            item.isactive = False
            item.save(update_fields=("isactive",))

    for unit in linked_units:
        from_status = unit.status
        unit.status = ProductUnit.STATUS_INACTIVE
        unit.isactive = False
        unit.save(update_fields=("status", "isactive", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_RECEIVING_CANCELLED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_INACTIVE,
            reason=receiving.cancel_reason,
            notes=receiving.cancel_reason,
            performed_by=cancelled_by,
            movement_date=timezone.localdate(),
            receiving_record=receiving,
            reference=receiving.receiving_number,
        )

    return receiving


@transaction.atomic
def update_delivery_record_header(
    delivery,
    *,
    customer_name=None,
    receiver_name=None,
    delivery_date=None,
    notes=None,
    items=None,
):
    if delivery.status == DeliveryRecord.STATUS_CANCELLED:
        raise ValidationError("Cancelled delivery records cannot be edited.")

    item_rows = list(delivery.items.select_related("product_unit"))
    if delivery_date is not None:
        blocked_units = [
            item.product_unit.serial_number
            for item in item_rows
            if not _delivery_unit_can_be_corrected(item)
        ]
        if blocked_units:
            raise ValidationError(
                "Cannot change delivery date because these stock units are no longer untouched sold units: "
                + ", ".join(sorted(blocked_units))
            )

    if customer_name is not None:
        delivery.customer_name = customer_name.strip()
    if receiver_name is not None:
        delivery.receiver_name = receiver_name.strip()
    if delivery_date is not None:
        delivery.delivery_date = delivery_date
    if notes is not None:
        delivery.notes = notes
    delivery.save(
        update_fields=(
            "customer_name",
            "receiver_name",
            "delivery_date",
            "notes",
        )
    )

    for item_data in items or []:
        item_id = item_data.get("id")
        if not item_id:
            continue
        try:
            item = delivery.items.get(pk=item_id)
        except DeliveryItem.DoesNotExist:
            continue
        if "notes" in item_data:
            item.notes = item_data["notes"]
            item.save(update_fields=("notes",))

    if delivery_date is not None:
        for item in item_rows:
            unit = item.product_unit
            if unit and _delivery_unit_can_be_corrected(item):
                unit.sold_date = delivery.delivery_date
                unit.save(update_fields=("sold_date",))

    return delivery


@transaction.atomic
def cancel_delivery_record(delivery, *, cancelled_by=None, cancel_reason=""):
    if delivery.status == DeliveryRecord.STATUS_CANCELLED:
        return delivery

    items = list(delivery.items.select_related("product_unit"))
    blocked_units = [
        item.product_unit.serial_number
        for item in items
        if not _delivery_unit_can_be_corrected(item)
    ]
    if blocked_units:
        raise ValidationError(
            "Cannot cancel delivery record because these stock units are no longer untouched sold units: "
            + ", ".join(sorted(blocked_units))
        )

    delivery.status = DeliveryRecord.STATUS_CANCELLED
    delivery.cancel_reason = (cancel_reason or "").strip()
    delivery.cancelled_at = timezone.now()
    delivery.cancelled_by = cancelled_by
    delivery.save(
        update_fields=(
            "status",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
        )
    )

    for item in items:
        if item.isactive:
            item.isactive = False
            item.save(update_fields=("isactive",))

    for item in items:
        unit = item.product_unit
        from_status = unit.status
        unit.status = ProductUnit.STATUS_AVAILABLE
        unit.sold_date = None
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_DELIVERY_CANCELLED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_AVAILABLE,
            reason=delivery.cancel_reason,
            notes=delivery.cancel_reason,
            performed_by=cancelled_by,
            movement_date=timezone.localdate(),
            delivery_record=delivery,
            reference=delivery.delivery_number,
        )

    return delivery
