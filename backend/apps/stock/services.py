from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    ClientReturnItem,
    ClientReturnRecord,
    DeliveryItem,
    DeliveryRecord,
    IssueItem,
    IssueRecord,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    RepairItem,
    RepairRecord,
    ReservationItem,
    ReservationRecord,
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
    reservation_record=None,
    issue_record=None,
    repair_record=None,
    client_return_record=None,
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
        reservation_record=reservation_record,
        issue_record=issue_record,
        repair_record=repair_record,
        client_return_record=client_return_record,
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
    customer_name="",
    client=None,
    receiver_name="",
    delivery_date=None,
    notes="",
    created_by=None,
    status=DeliveryRecord.STATUS_COMPLETED,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one available stock unit is required.")

    units = list(
        ProductUnit.objects.select_for_update()
        .select_related("product")
        .filter(pk__in=unique_ids)
        .order_by("product__descript", "serial_number")
    )
    units_by_id = {unit.pk: unit for unit in units}
    missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]
    if missing_ids:
        raise ValidationError("One or more stock units were not found.")

    unavailable_units = [
        unit.serial_number
        for unit in units
        if not unit.isactive or unit.status != ProductUnit.STATUS_AVAILABLE
    ]
    if unavailable_units:
        raise ValidationError(
            "Only active available stock units can be delivered: "
            + ", ".join(sorted(unavailable_units))
        )

    client_name = client.name if client else ""
    delivery = DeliveryRecord.objects.create(
        client=client,
        customer_name=(customer_name or client_name or "").strip(),
        receiver_name=(receiver_name or "").strip(),
        delivery_date=delivery_date or timezone.localdate(),
        notes=notes,
        status=status,
        created_by=created_by,
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


def _active_client_return_item_for_unit(unit):
    return unit.client_return_items.filter(isactive=True).first()


@transaction.atomic
def create_client_return_record(
    *,
    unit_ids,
    resolution,
    delivery=None,
    client=None,
    customer_name="",
    received_from="",
    return_date=None,
    reason="",
    notes="",
    received_by=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one sold stock unit is required.")
    if resolution not in (
        ClientReturnRecord.RESOLUTION_AVAILABLE,
        ClientReturnRecord.RESOLUTION_REPAIR,
    ):
        raise ValidationError("Client returns can only move units to available or repair.")

    units = list(
        ProductUnit.objects.select_for_update()
        .select_related("product")
        .filter(pk__in=unique_ids)
        .order_by("product__descript", "serial_number")
    )
    units_by_id = {unit.pk: unit for unit in units}
    missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]
    if missing_ids:
        raise ValidationError("One or more stock units were not found.")

    invalid_units = [
        unit.serial_number or str(unit.pk)
        for unit in units
        if not unit.isactive or unit.status != ProductUnit.STATUS_SOLD
    ]
    if invalid_units:
        raise ValidationError(
            "Client return can only use active sold units: " + ", ".join(invalid_units)
        )

    delivery_items = list(
        DeliveryItem.objects.select_for_update()
        .select_related("delivery", "product", "product_unit")
        .filter(product_unit_id__in=unique_ids)
    )
    delivery_items_by_unit_id = {item.product_unit_id: item for item in delivery_items}
    blocked_units = []
    for unit in units:
        item = delivery_items_by_unit_id.get(unit.pk)
        active_return = _active_client_return_item_for_unit(unit)
        if (
            item is None
            or not item.isactive
            or not item.delivery.isactive
            or item.delivery.status != DeliveryRecord.STATUS_COMPLETED
            or active_return is not None
            or (delivery is not None and item.delivery_id != delivery.pk)
        ):
            blocked_units.append(unit.serial_number or str(unit.pk))
    if blocked_units:
        raise ValidationError(
            "Client return requires active sold units linked to completed deliveries: "
            + ", ".join(blocked_units)
        )

    delivery_ids = {item.delivery_id for item in delivery_items_by_unit_id.values()}
    record_delivery = delivery
    if record_delivery is None and len(delivery_ids) == 1:
        record_delivery = next(iter(delivery_items_by_unit_id.values())).delivery

    record_client = client or (record_delivery.client if record_delivery else None)
    client_return = ClientReturnRecord.objects.create(
        delivery=record_delivery,
        client=record_client,
        customer_name=(
            customer_name
            or (record_client.name if record_client else "")
            or (record_delivery.customer_name if record_delivery else "")
        ).strip(),
        received_from=(received_from or "").strip(),
        return_date=return_date or timezone.localdate(),
        reason=(reason or "").strip(),
        resolution=resolution,
        notes=notes,
        received_by=received_by,
    )

    movement_type = (
        StockMovement.TYPE_CLIENT_RETURNED_AVAILABLE
        if resolution == ProductUnit.STATUS_AVAILABLE
        else StockMovement.TYPE_CLIENT_RETURNED_REPAIR
    )
    for unit in units:
        item = delivery_items_by_unit_id[unit.pk]
        ClientReturnItem.objects.create(
            client_return=client_return,
            delivery_item=item,
            product_unit=unit,
            product=unit.product,
            notes=notes,
        )
        from_status = unit.status
        unit.status = resolution
        unit.sold_date = None
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=movement_type,
            from_status=from_status,
            to_status=resolution,
            reason=client_return.reason,
            notes=notes,
            performed_by=received_by,
            movement_date=client_return.return_date,
            delivery_record=item.delivery,
            client_return_record=client_return,
            reference=client_return.return_number,
        )

    return client_return


def _active_reservation_item_for_unit(unit):
    return unit.reservation_items.filter(isactive=True).first()


@transaction.atomic
def create_reservation_record(
    *,
    unit_ids,
    reserved_for,
    reason="",
    expected_release_date=None,
    notes="",
    reserved_by=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one stock unit is required.")

    units = list(
        ProductUnit.objects.select_for_update()
        .select_related("product")
        .filter(pk__in=unique_ids)
        .order_by("product__descript", "serial_number")
    )
    units_by_id = {unit.pk: unit for unit in units}
    missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]
    if missing_ids:
        raise ValidationError("One or more stock units were not found.")

    unavailable_units = [
        unit.serial_number
        for unit in units
        if not unit.isactive or unit.status != ProductUnit.STATUS_AVAILABLE
    ]
    if unavailable_units:
        raise ValidationError(
            "Only active available stock units can be reserved: "
            + ", ".join(sorted(unavailable_units))
        )

    reservation = ReservationRecord.objects.create(
        reserved_for=(reserved_for or "").strip(),
        reason=(reason or "").strip(),
        expected_release_date=expected_release_date,
        notes=notes,
        reserved_by=reserved_by,
    )

    for unit in units:
        from_status = unit.status
        ReservationItem.objects.create(
            reservation=reservation,
            product_unit=unit,
            product=unit.product,
        )
        unit.status = ProductUnit.STATUS_RESERVED
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_RESERVED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_RESERVED,
            reason=reservation.reason,
            notes=notes,
            performed_by=reserved_by,
            movement_date=timezone.localdate(),
            reservation_record=reservation,
            reference=reservation.reservation_number,
        )

    return reservation


def _reservation_item_can_be_released(item):
    unit = item.product_unit
    if not item.isactive or not unit:
        return False
    active_item = _active_reservation_item_for_unit(unit)
    return (
        unit.isactive
        and unit.status == ProductUnit.STATUS_RESERVED
        and active_item
        and active_item.pk == item.pk
    )


@transaction.atomic
def release_reservation_record(
    reservation,
    *,
    released_by=None,
    release_reason="",
    cancel=False,
):
    reservation = ReservationRecord.objects.select_for_update().get(pk=reservation.pk)
    if reservation.status != ReservationRecord.STATUS_ACTIVE:
        raise ValidationError("Only active reservation records can be released.")

    items = list(
        reservation.items.select_for_update()
        .select_related("product_unit", "product")
        .filter()
        .order_by("product__descript", "product_unit__serial_number")
    )
    blocked_units = [
        item.product_unit.serial_number
        for item in items
        if not _reservation_item_can_be_released(item)
    ]
    if blocked_units:
        raise ValidationError(
            "Cannot release reservation because these stock units are no longer untouched reserved units: "
            + ", ".join(sorted(blocked_units))
        )

    reservation.status = (
        ReservationRecord.STATUS_CANCELLED if cancel else ReservationRecord.STATUS_RELEASED
    )
    reservation.release_reason = (release_reason or "").strip()
    reservation.released_at = timezone.now()
    reservation.released_by = released_by
    reservation.save(
        update_fields=(
            "status",
            "release_reason",
            "released_at",
            "released_by",
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
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_RESERVATION_RELEASED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_AVAILABLE,
            reason=reservation.release_reason,
            notes=reservation.release_reason,
            performed_by=released_by,
            movement_date=timezone.localdate(),
            reservation_record=reservation,
            reference=reservation.reservation_number,
        )

    return reservation


def _active_issue_item_for_unit(unit):
    return unit.issue_items.filter(isactive=True).first()


@transaction.atomic
def create_issue_record(
    *,
    unit_ids,
    issued_to,
    department="",
    branch_or_site="",
    reason="",
    issue_date=None,
    expected_return_date=None,
    notes="",
    issued_by=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one stock unit is required.")

    units = list(
        ProductUnit.objects.select_for_update()
        .select_related("product")
        .filter(pk__in=unique_ids)
        .order_by("product__descript", "serial_number")
    )
    units_by_id = {unit.pk: unit for unit in units}
    missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]
    if missing_ids:
        raise ValidationError("One or more stock units were not found.")

    unavailable_units = [
        unit.serial_number
        for unit in units
        if not unit.isactive or unit.status != ProductUnit.STATUS_AVAILABLE
    ]
    if unavailable_units:
        raise ValidationError(
            "Only active available stock units can be issued: "
            + ", ".join(sorted(unavailable_units))
        )

    issue = IssueRecord.objects.create(
        issued_to=(issued_to or "").strip(),
        department=(department or "").strip(),
        branch_or_site=(branch_or_site or "").strip(),
        reason=(reason or "").strip(),
        issue_date=issue_date or timezone.localdate(),
        expected_return_date=expected_return_date,
        notes=notes,
        issued_by=issued_by,
    )

    for unit in units:
        from_status = unit.status
        IssueItem.objects.create(
            issue=issue,
            product_unit=unit,
            product=unit.product,
        )
        unit.status = ProductUnit.STATUS_ISSUED
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_ISSUED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_ISSUED,
            reason=issue.reason,
            notes=notes,
            performed_by=issued_by,
            movement_date=issue.issue_date,
            issue_record=issue,
            reference=issue.issue_number,
        )

    return issue


def _issue_item_can_be_returned(item):
    unit = item.product_unit
    if not item.isactive or not unit:
        return False
    active_item = _active_issue_item_for_unit(unit)
    return (
        unit.isactive
        and unit.status == ProductUnit.STATUS_ISSUED
        and active_item
        and active_item.pk == item.pk
    )


@transaction.atomic
def return_issue_record(
    issue,
    *,
    returned_by=None,
    return_reason="",
    returned_date=None,
):
    issue = IssueRecord.objects.select_for_update().get(pk=issue.pk)
    if issue.status != IssueRecord.STATUS_ACTIVE:
        raise ValidationError("Only active issue records can be returned.")

    items = list(
        issue.items.select_for_update()
        .select_related("product_unit", "product")
        .filter()
        .order_by("product__descript", "product_unit__serial_number")
    )
    blocked_units = [
        item.product_unit.serial_number
        for item in items
        if not _issue_item_can_be_returned(item)
    ]
    if blocked_units:
        raise ValidationError(
            "Cannot return issue because these stock units are no longer untouched issued units: "
            + ", ".join(sorted(blocked_units))
        )

    issue.status = IssueRecord.STATUS_RETURNED
    issue.return_reason = (return_reason or "").strip()
    issue.returned_date = returned_date or timezone.localdate()
    issue.returned_at = timezone.now()
    issue.returned_by = returned_by
    issue.save(
        update_fields=(
            "status",
            "return_reason",
            "returned_date",
            "returned_at",
            "returned_by",
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
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_ISSUE_RETURNED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_AVAILABLE,
            reason=issue.return_reason,
            notes=issue.return_reason,
            performed_by=returned_by,
            movement_date=issue.returned_date,
            issue_record=issue,
            reference=issue.issue_number,
        )

    return issue


def _active_repair_item_for_unit(unit):
    return unit.repair_items.filter(isactive=True).first()


@transaction.atomic
def create_repair_record(
    *,
    unit_ids,
    repair_reason,
    reported_by_name="",
    repair_location="",
    technician="",
    repair_date=None,
    expected_resolution_date=None,
    notes="",
    sent_by=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one stock unit is required.")

    units = list(
        ProductUnit.objects.select_for_update()
        .select_related("product")
        .filter(pk__in=unique_ids)
        .order_by("product__descript", "serial_number")
    )
    units_by_id = {unit.pk: unit for unit in units}
    missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]
    if missing_ids:
        raise ValidationError("One or more stock units were not found.")

    unavailable_units = [
        unit.serial_number
        for unit in units
        if not unit.isactive or unit.status != ProductUnit.STATUS_AVAILABLE
    ]
    if unavailable_units:
        raise ValidationError(
            "Only active available stock units can be sent to repair: "
            + ", ".join(sorted(unavailable_units))
        )

    repair = RepairRecord.objects.create(
        repair_reason=(repair_reason or "").strip(),
        reported_by_name=(reported_by_name or "").strip(),
        repair_location=(repair_location or "").strip(),
        technician=(technician or "").strip(),
        repair_date=repair_date or timezone.localdate(),
        expected_resolution_date=expected_resolution_date,
        notes=notes,
        sent_by=sent_by,
    )

    for unit in units:
        from_status = unit.status
        RepairItem.objects.create(
            repair=repair,
            product_unit=unit,
            product=unit.product,
        )
        unit.status = ProductUnit.STATUS_REPAIR
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_SENT_TO_REPAIR,
            from_status=from_status,
            to_status=ProductUnit.STATUS_REPAIR,
            reason=repair.repair_reason,
            notes=notes,
            performed_by=sent_by,
            movement_date=repair.repair_date,
            repair_record=repair,
            reference=repair.repair_number,
        )

    return repair


def _repair_item_can_be_resolved(item):
    unit = item.product_unit
    if not item.isactive or not unit:
        return False
    active_item = _active_repair_item_for_unit(unit)
    return (
        unit.isactive
        and unit.status == ProductUnit.STATUS_REPAIR
        and active_item
        and active_item.pk == item.pk
    )


@transaction.atomic
def resolve_repair_record(
    repair,
    *,
    resolution,
    resolved_by=None,
    resolution_notes="",
    resolved_date=None,
):
    repair = RepairRecord.objects.select_for_update().get(pk=repair.pk)
    if repair.status != RepairRecord.STATUS_ACTIVE:
        raise ValidationError("Only active repair records can be resolved.")
    if resolution not in (
        ProductUnit.STATUS_AVAILABLE,
        ProductUnit.STATUS_INACTIVE,
    ):
        raise ValidationError("Repair resolution must be available or inactive.")

    items = list(
        repair.items.select_for_update()
        .select_related("product_unit", "product")
        .filter()
        .order_by("product__descript", "product_unit__serial_number")
    )
    blocked_units = [
        item.product_unit.serial_number
        for item in items
        if not _repair_item_can_be_resolved(item)
    ]
    if blocked_units:
        raise ValidationError(
            "Cannot resolve repair because these stock units are no longer untouched repair units: "
            + ", ".join(sorted(blocked_units))
        )

    repair.status = RepairRecord.STATUS_RESOLVED
    repair.resolution = resolution
    repair.resolution_notes = (resolution_notes or "").strip()
    repair.resolved_date = resolved_date or timezone.localdate()
    repair.resolved_at = timezone.now()
    repair.resolved_by = resolved_by
    repair.save(
        update_fields=(
            "status",
            "resolution",
            "resolution_notes",
            "resolved_date",
            "resolved_at",
            "resolved_by",
        )
    )

    for item in items:
        if item.isactive:
            item.isactive = False
            item.resolution_notes = repair.resolution_notes
            item.save(update_fields=("isactive", "resolution_notes"))

    movement_type = (
        StockMovement.TYPE_REPAIR_RESOLVED
        if resolution == ProductUnit.STATUS_AVAILABLE
        else StockMovement.TYPE_REPAIR_DEACTIVATED
    )
    for item in items:
        unit = item.product_unit
        from_status = unit.status
        unit.status = resolution
        if resolution == ProductUnit.STATUS_INACTIVE:
            unit.isactive = False
        unit.save(update_fields=("status", "isactive", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=movement_type,
            from_status=from_status,
            to_status=resolution,
            reason=repair.resolution_notes,
            notes=repair.resolution_notes,
            performed_by=resolved_by,
            movement_date=repair.resolved_date,
            repair_record=repair,
            reference=repair.repair_number,
        )

    return repair


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
