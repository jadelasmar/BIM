from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import (
    Client,
    ClientReturnItem,
    ClientReturnRecord,
    ClientUpgradeRecord,
    RecordChange,
    DeliveryItem,
    DeliveryRecord,
    InternalParty,
    IssueItem,
    IssueRecord,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    RemovalItem,
    RemovalRecord,
    RepairItem,
    RepairRecord,
    ReservationItem,
    ReservationRecord,
    StockMovement,
    Supplier,
)


_UNSET = object()


def _resolve_internal_party(internal=None, name_input="", kind_input=""):
    """Return an existing InternalParty, or get-or-create one from a typed name
    (the picker's inline "create" option). Returns None when neither is given."""
    if internal is not None:
        return internal

    name = (name_input or "").strip()
    if not name:
        return None
    if len(name) > 150:
        raise ValidationError("Employee name must be 150 characters or fewer.")

    # Departments are no longer entered; anything new is an employee. Existing
    # department rows stay selectable.
    kind = (kind_input or "").strip() or InternalParty.KIND_EMPLOYEE
    if kind not in (InternalParty.KIND_EMPLOYEE, InternalParty.KIND_DEPARTMENT):
        raise ValidationError("Internal party must be an employee.")

    party, _created = InternalParty.objects.get_or_create(kind=kind, name=name)
    return party


def _resolve_supplier(supplier=None, name_input=""):
    """An existing Supplier, or one created from a typed name (the picker's inline
    "create" option), the same way Receiving creates a new supplier. Returns None
    when neither is given."""
    if supplier is not None:
        return supplier
    name = (name_input or "").strip()
    if not name:
        return None
    supplier, _created = Supplier.objects.get_or_create(name=name)
    return supplier


def _resolve_reservation_party(
    *,
    party_type,
    client=None,
    supplier=None,
    internal=None,
    internal_name_input="",
    internal_kind_input="",
    client_name_input="",
    supplier_name_input="",
):
    if party_type == ReservationRecord.TYPE_CLIENT:
        # A client typed into the picker's "create" option is created here, the
        # same way a new client is created from the Delivery form.
        if client is None and (client_name_input or "").strip():
            client, _created = Client.objects.get_or_create(name=client_name_input.strip())
        if client is None:
            raise ValidationError("Choose the client this reservation is for.")
        return party_type, client, None, None, client.name
    if party_type == ReservationRecord.TYPE_SUPPLIER:
        if supplier is None and (supplier_name_input or "").strip():
            supplier, _created = Supplier.objects.get_or_create(name=supplier_name_input.strip())
        if supplier is None:
            raise ValidationError("Choose the supplier this reservation is for.")
        return party_type, None, supplier, None, supplier.name
    if party_type == ReservationRecord.TYPE_INTERNAL:
        party = _resolve_internal_party(internal, internal_name_input, internal_kind_input)
        if party is None:
            raise ValidationError("Choose the employee this reservation is for.")
        return party_type, None, None, party, party.name
    raise ValidationError("Reserved for type must be client, supplier, or internal.")


def _resolve_repair_source(
    *,
    source,
    source_client=None,
    source_client_name_input="",
    source_internal=None,
    source_internal_name_input="",
    source_internal_kind_input="",
):
    if source == RepairRecord.SOURCE_INTERNAL_STOCK:
        return source, None, None
    if source in (RepairRecord.SOURCE_CLIENT_RETURN, RepairRecord.SOURCE_CLIENT_ITEM):
        # A client typed into the picker's "create" option is created here, the
        # same way a Delivery creates a new client.
        if source_client is None and (source_client_name_input or "").strip():
            source_client, _created = Client.objects.get_or_create(
                name=source_client_name_input.strip()
            )
        if source_client is None:
            raise ValidationError(
                "Choose the client this item belongs to."
                if source == RepairRecord.SOURCE_CLIENT_ITEM
                else "Choose the client this repair came from."
            )
        return source, source_client, None
    if source == RepairRecord.SOURCE_INTERNAL_PARTY:
        party = _resolve_internal_party(
            source_internal, source_internal_name_input, source_internal_kind_input
        )
        if party is None:
            raise ValidationError("Choose the employee this repair came from.")
        return source, None, party
    raise ValidationError("Repair source must be internal stock, client return, or employee.")


def _clean_serial_numbers(serial_numbers):
    if not serial_numbers:
        return []

    cleaned = [str(serial).strip() for serial in serial_numbers if str(serial).strip()]
    if len(cleaned) != len(set(cleaned)):
        raise ValidationError("Serial numbers must be unique within a receiving item.")
    return cleaned


# Fields shown in a record's edit history, as (attribute, label). Every update_*
# function below snapshots these before and after its changes and logs the
# difference with log_record_changes() -- add new editable fields here.
RECEIVING_HISTORY_FIELDS = (
    ("supplier", "Supplier"),
    ("po_number", "Purchase Order #"),
    ("supplier_invoice_number", "Supplier Invoice #"),
    ("received_date", "Received date"),
    ("notes", "Notes"),
)
DELIVERY_HISTORY_FIELDS = (
    ("customer_name", "Client"),
    ("invoice_number", "Invoice number"),
    ("delivery_date", "Delivery date"),
    ("notes", "Notes"),
)
RESERVATION_HISTORY_FIELDS = (
    ("reserved_for", "Reserved for"),
    ("reason", "Reason"),
    ("notes", "Notes"),
)
ISSUE_HISTORY_FIELDS = (
    ("issued_to", "Assigned to"),
    ("reason", "Reason"),
    ("issue_date", "Assignment date"),
    ("expected_return_date", "Expected return date"),
    ("notes", "Notes"),
)
REPAIR_HISTORY_FIELDS = (
    ("vendor", "Supplier"),
    ("repair_reason", "Reason"),
    ("repair_date", "Repair date"),
    ("notes", "Notes"),
)
CLIENT_RETURN_HISTORY_FIELDS = (
    ("received_from", "Received from"),
    ("return_date", "Return date"),
    ("reason", "Reason"),
    ("notes", "Notes"),
)
CLIENT_UPGRADE_HISTORY_FIELDS = (
    ("client_name", "Client"),
    ("status", "Status"),
    ("upgrade_date", "Date"),
    ("updater", "Updater"),
    ("notes", "Notes"),
)


def _snapshot(obj, fields):
    """{label: readable text} for the given (attribute, label) pairs."""
    values = {}
    for attr, label in fields:
        value = getattr(obj, attr)
        display = getattr(obj, f"get_{attr}_display", None)
        if value is None:
            text = ""
        elif display is not None:
            text = display()
        elif hasattr(value, "isoformat"):
            text = value.isoformat()
        else:
            text = str(value)
        values[label] = text
    return values


def log_record_changes(record_type, record, number, before, after, changed_by=None):
    """Write one RecordChange row for every label whose value differs between the
    two snapshots. Nothing is written when nothing actually changed."""
    rows = [
        RecordChange(
            record_type=record_type,
            record_id=record.pk,
            record_number=number or "",
            field_label=label,
            old_value=before.get(label, ""),
            new_value=value,
            changed_by=changed_by,
        )
        for label, value in after.items()
        if before.get(label, "") != value
    ]
    if rows:
        RecordChange.objects.bulk_create(rows)


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
    removal_record=None,
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
        removal_record=removal_record,
        reference=(reference or "").strip()[:150],
    )


def _create_receiving_item(receiving, supplier, received_date, item_data, created_by=None):
    product = item_data["product"]
    quantity = int(item_data.get("quantity") or 1)
    serial_numbers = _clean_serial_numbers(item_data.get("serial_numbers"))
    cost = item_data.get("cost", 0)
    notes = item_data.get("notes", "")
    product_unit = item_data.get("product_unit")

    created_units = []

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
        return created_units
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
            created_units.append(unit)
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
        return created_units

    ReceivingItem.objects.create(
        receiving=receiving,
        product=product,
        quantity=quantity,
        cost=cost,
        notes=notes,
    )
    return created_units


@transaction.atomic
def create_receiving_record(
    *,
    items,
    supplier=None,
    supplier_name_input="",
    po_number="",
    supplier_invoice_number="",
    received_date=None,
    notes="",
    created_by=None,
    idempotency_key="",
    reserve_for_client=None,
    reserve_client_name_input="",
):
    if not items:
        raise ValidationError("At least one receiving item is required.")

    idempotency_key = (idempotency_key or "").strip()
    if idempotency_key:
        # A retried/double-submitted request (e.g. a duplicate click before the
        # frontend's Save button re-disables) replays the same key -- return
        # the record that request already created instead of making another.
        # Manual-quantity receiving lines have no linked ProductUnit, so
        # nothing else guards against this the way unique serial numbers do
        # for serialized lines.
        existing = ReceivingRecord.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    if not supplier and supplier_name_input.strip():
        supplier, _created = Supplier.objects.get_or_create(name=supplier_name_input.strip())

    try:
        with transaction.atomic():
            receiving = ReceivingRecord.objects.create(
                supplier=supplier,
                po_number=(po_number or "").strip(),
                supplier_invoice_number=(supplier_invoice_number or "").strip(),
                received_date=received_date or timezone.localdate(),
                notes=notes,
                created_by=created_by,
                idempotency_key=idempotency_key,
            )
    except IntegrityError:
        # Two near-simultaneous requests both passed the check above before
        # either committed -- the unique constraint on idempotency_key caught
        # the loser. Return the winner's record rather than erroring out.
        if idempotency_key:
            existing = ReceivingRecord.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return existing
        raise

    units_to_reserve = []
    for item_data in items:
        created_units = _create_receiving_item(
            receiving=receiving,
            supplier=supplier,
            received_date=receiving.received_date,
            item_data=item_data,
            created_by=created_by,
        )
        if item_data.get("reserve", True):
            units_to_reserve.extend(created_units)

    # Stock bought for a client: reserve the received units for them in the same
    # step. Goes through create_reservation_record so the reservation, the unit
    # status change and the StockMovement rows are the normal ones.
    receiving.created_reservation = None
    if reserve_for_client is not None or (reserve_client_name_input or "").strip():
        if not units_to_reserve:
            raise ValidationError(
                "Tick at least one received line to reserve it for the client."
            )
        receiving.created_reservation = create_reservation_record(
            unit_ids=[unit.pk for unit in units_to_reserve],
            reserved_for_type=ReservationRecord.TYPE_CLIENT,
            reserved_for_client=reserve_for_client,
            client_name_input=reserve_client_name_input,
            reason=f"Reserved on receipt {receiving.receiving_number}",
            reserved_by=created_by,
        )

    return receiving


@transaction.atomic
def create_delivery_record(
    *,
    unit_ids,
    customer_name="",
    client=None,
    client_name_input="",
    invoice_number="",
    delivery_date=None,
    notes="",
    created_by=None,
    status=DeliveryRecord.STATUS_COMPLETED,
    unit_sale_prices=None,
    from_reservation=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one available stock unit is required.")

    # Delivering a reservation: its reserved units go straight to sold (never
    # via Available) and the reservation closes as delivered.
    reservation = None
    reservation_items = []
    if from_reservation is not None:
        reservation = ReservationRecord.objects.select_for_update().get(
            pk=from_reservation.pk
        )
        if reservation.status != ReservationRecord.STATUS_ACTIVE:
            raise ValidationError("Only active reservations can be delivered.")
        if reservation.reserved_for_type != ReservationRecord.TYPE_CLIENT:
            raise ValidationError("Only client reservations can be delivered.")
        reservation_items = list(
            reservation.items.select_for_update()
            .select_related("product_unit")
            .filter(isactive=True)
        )
        if set(unique_ids) != {item.product_unit_id for item in reservation_items}:
            raise ValidationError(
                "A delivery from a reservation must include all of that reservation's units."
            )
        if client is None and not client_name_input.strip():
            client = reservation.reserved_for_client

    if not client and client_name_input.strip():
        client, _created = Client.objects.get_or_create(name=client_name_input.strip())
    if client is None:
        # A client record is what later lets a Client Return derive who a unit
        # belongs to; free-text customer names alone are not enough.
        raise ValidationError("Choose a client for this delivery.")

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

    if reservation is not None:
        blocked_units = [
            item.product_unit.serial_number
            for item in reservation_items
            if not _reservation_item_can_be_released(item)
        ]
        if blocked_units:
            raise ValidationError(
                "Cannot deliver reservation because these stock units are no longer untouched reserved units: "
                + ", ".join(sorted(blocked_units))
            )
    else:
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

    sale_prices = unit_sale_prices or {}

    client_name = client.name if client else ""
    delivery = DeliveryRecord.objects.create(
        client=client,
        customer_name=(customer_name or client_name or "").strip(),
        invoice_number=(invoice_number or "").strip(),
        delivery_date=delivery_date or timezone.localdate(),
        notes=notes,
        status=status,
        from_reservation=reservation,
        created_by=created_by,
    )
    for unit in units:
        from_status = unit.status
        DeliveryItem.objects.create(
            delivery=delivery,
            product_unit=unit,
            product=unit.product,
            sale_price=sale_prices.get(str(unit.pk), sale_prices.get(unit.pk, 0)),
        )
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = delivery.delivery_date
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_DELIVERED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_SOLD,
            reason=f"Delivered from reservation {reservation.reservation_number}"
            if reservation
            else "Delivered stock",
            notes=notes,
            performed_by=created_by,
            movement_date=delivery.delivery_date,
            delivery_record=delivery,
            reservation_record=reservation,
            reference=delivery.delivery_number,
        )

    if reservation is not None:
        reservation.status = ReservationRecord.STATUS_DELIVERED
        reservation.save(update_fields=("status",))
        for item in reservation_items:
            item.isactive = False
            item.save(update_fields=("isactive",))

    return delivery


def _active_client_return_item_for_unit(unit):
    # A unit can be returned more than once (sold, returned, repaired, returned
    # to the client, returned again); the newest return line is the current one.
    return unit.client_return_items.filter(isactive=True).order_by("-pk").first()


def _latest_delivery_item_for_unit(unit):
    """The unit's current delivery line: the newest one created. Earlier lines
    (e.g. the original sale before a warranty return) are history."""
    return (
        unit.delivery_items.select_related("delivery", "delivery__client")
        .order_by("-pk")
        .first()
    )


def _latest_completed_delivery_item_for_unit(unit):
    return (
        unit.delivery_items.select_related("delivery", "delivery__client")
        .filter(isactive=True, delivery__isactive=True, delivery__status=DeliveryRecord.STATUS_COMPLETED)
        .order_by("-pk")
        .first()
    )


@transaction.atomic
def create_client_return_record(
    *,
    unit_ids,
    resolution,
    delivery=None,
    client=None,
    received_from="",
    return_date=None,
    reason="",
    repair_vendor=None,
    repair_vendor_name_input="",
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
    if resolution == ClientReturnRecord.RESOLUTION_REPAIR:
        repair_vendor = _resolve_supplier(repair_vendor, repair_vendor_name_input)
        if repair_vendor is None:
            raise ValidationError("Choose the supplier for units going to repair.")

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

    # The client always comes from each unit's latest completed delivery, never
    # from the request. A client sent in the request is only a cross-check.
    delivery_items_by_unit_id = {}
    blocked_units = []
    for unit in units:
        item = _latest_completed_delivery_item_for_unit(unit)
        latest_return = _active_client_return_item_for_unit(unit)
        if (
            item is None
            # Already returned under this same delivery line; a new sale (e.g. a
            # warranty return) creates a newer line that can be returned again.
            or (latest_return is not None and latest_return.delivery_item_id == item.pk)
            or (delivery is not None and item.delivery_id != delivery.pk)
        ):
            blocked_units.append(unit.serial_number or str(unit.pk))
        else:
            delivery_items_by_unit_id[unit.pk] = item
    if blocked_units:
        raise ValidationError(
            "Client return requires active sold units linked to completed deliveries: "
            + ", ".join(blocked_units)
        )

    no_client_deliveries = sorted(
        {
            item.delivery.delivery_number
            for item in delivery_items_by_unit_id.values()
            if item.delivery.client_id is None
        }
    )
    if no_client_deliveries:
        raise ValidationError(
            "This delivery has no client. Fix the delivery's client first. ("
            + ", ".join(no_client_deliveries)
            + ")"
        )
    client_ids = {item.delivery.client_id for item in delivery_items_by_unit_id.values()}
    if len(client_ids) > 1:
        raise ValidationError(
            "These units were delivered to different clients. Create a separate client return for each client."
        )
    record_client = next(iter(delivery_items_by_unit_id.values())).delivery.client
    if client is not None and client.pk != record_client.pk:
        raise ValidationError(
            f"The client must match the unit's latest delivery ({record_client.name})."
        )

    delivery_ids = {item.delivery_id for item in delivery_items_by_unit_id.values()}
    record_delivery = delivery
    if record_delivery is None and len(delivery_ids) == 1:
        record_delivery = next(iter(delivery_items_by_unit_id.values())).delivery

    client_return = ClientReturnRecord.objects.create(
        delivery=record_delivery,
        client=record_client,
        customer_name=record_client.name,
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

    repair_record = None
    if resolution == ProductUnit.STATUS_REPAIR:
        repair_record = RepairRecord.objects.create(
            client_return=client_return,
            vendor=repair_vendor,
            source=RepairRecord.SOURCE_CLIENT_RETURN,
            source_client=record_client,
            repair_reason=(client_return.reason or "Client return - repair needed").strip(),
            repair_date=client_return.return_date,
            notes=notes,
            sent_by=received_by,
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
        if repair_record is not None:
            RepairItem.objects.create(
                repair=repair_record,
                product_unit=unit,
                product=unit.product,
            )
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
            repair_record=repair_record,
            client_return_record=client_return,
            reference=client_return.return_number,
        )

    return client_return


def _client_return_item_can_be_cancelled(item):
    unit = item.product_unit
    if not item.isactive or not unit or not unit.isactive:
        return False

    client_return = item.client_return
    active_item = _active_client_return_item_for_unit(unit)
    if not active_item or active_item.pk != item.pk:
        return False
    if unit.status != client_return.resolution:
        return False

    if client_return.resolution == ProductUnit.STATUS_REPAIR:
        active_repair_item = _active_repair_item_for_unit(unit)
        if not active_repair_item or active_repair_item.repair.client_return_id != client_return.pk:
            return False
        if active_repair_item.repair.status != RepairRecord.STATUS_ACTIVE:
            return False

    return True


@transaction.atomic
def cancel_client_return_record(client_return, *, cancelled_by=None, cancel_reason=""):
    client_return = ClientReturnRecord.objects.select_for_update().get(pk=client_return.pk)
    if client_return.status == ClientReturnRecord.STATUS_CANCELLED:
        return client_return

    items = list(
        client_return.items.select_for_update()
        .select_related("product_unit", "delivery_item", "delivery_item__delivery")
        .filter(isactive=True)
    )
    blocked_units = [
        item.product_unit.serial_number
        for item in items
        if not _client_return_item_can_be_cancelled(item)
    ]
    if blocked_units:
        raise ValidationError(
            "Cannot cancel client return because these stock units are no longer untouched: "
            + ", ".join(sorted(blocked_units))
        )

    linked_repair = (
        RepairRecord.objects.select_for_update()
        .filter(client_return=client_return, status=RepairRecord.STATUS_ACTIVE)
        .first()
    )

    client_return.status = ClientReturnRecord.STATUS_CANCELLED
    client_return.cancel_reason = (cancel_reason or "").strip()
    client_return.cancelled_at = timezone.now()
    client_return.cancelled_by = cancelled_by
    client_return.save(
        update_fields=("status", "cancel_reason", "cancelled_at", "cancelled_by")
    )

    for item in items:
        item.isactive = False
        item.save(update_fields=("isactive",))

    if linked_repair is not None:
        linked_repair.status = RepairRecord.STATUS_CANCELLED
        linked_repair.save(update_fields=("status",))
        linked_repair.items.filter(isactive=True).update(isactive=False)

    for item in items:
        unit = item.product_unit
        from_status = unit.status
        delivery = item.delivery_item.delivery if item.delivery_item else None
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = delivery.delivery_date if delivery else timezone.localdate()
        unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_CLIENT_RETURN_CANCELLED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_SOLD,
            reason=client_return.cancel_reason,
            notes=client_return.cancel_reason,
            performed_by=cancelled_by,
            movement_date=timezone.localdate(),
            delivery_record=delivery,
            client_return_record=client_return,
            reference=client_return.return_number,
        )

    return client_return


def update_client_return_record_header(
    client_return,
    *,
    return_date=None,
    received_from=None,
    reason=None,
    notes=None,
    changed_by=None,
):
    if client_return.status == ClientReturnRecord.STATUS_CANCELLED:
        raise ValidationError("Cancelled client return records cannot be edited.")

    before = _snapshot(client_return, CLIENT_RETURN_HISTORY_FIELDS)

    if received_from is not None:
        client_return.received_from = received_from.strip()
    if return_date is not None:
        client_return.return_date = return_date
    if reason is not None:
        client_return.reason = reason.strip()
    if notes is not None:
        client_return.notes = notes
    client_return.save(
        update_fields=(
            "received_from",
            "return_date",
            "reason",
            "notes",
        )
    )
    log_record_changes(
        "client_return",
        client_return,
        client_return.return_number,
        before,
        _snapshot(client_return, CLIENT_RETURN_HISTORY_FIELDS),
        changed_by,
    )

    return client_return


def _active_reservation_item_for_unit(unit):
    return unit.reservation_items.filter(isactive=True).first()


@transaction.atomic
def create_reservation_record(
    *,
    unit_ids,
    reserved_for_type,
    reserved_for_client=None,
    reserved_for_supplier=None,
    reserved_for_internal=None,
    internal_name_input="",
    internal_kind_input="",
    client_name_input="",
    supplier_name_input="",
    reason="",
    notes="",
    reserved_by=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one stock unit is required.")

    party_type, party_client, party_supplier, party_internal, party_name = (
        _resolve_reservation_party(
            party_type=reserved_for_type,
            client=reserved_for_client,
            supplier=reserved_for_supplier,
            internal=reserved_for_internal,
            internal_name_input=internal_name_input,
            internal_kind_input=internal_kind_input,
            client_name_input=client_name_input,
            supplier_name_input=supplier_name_input,
        )
    )

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
        reserved_for=party_name,
        reserved_for_type=party_type,
        reserved_for_client=party_client,
        reserved_for_supplier=party_supplier,
        reserved_for_internal=party_internal,
        reason=(reason or "").strip(),
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


def update_reservation_record_header(
    reservation,
    *,
    reserved_for_type=None,
    reserved_for_client=None,
    reserved_for_supplier=None,
    reserved_for_internal=None,
    internal_name_input="",
    internal_kind_input="",
    client_name_input="",
    supplier_name_input="",
    reason=None,
    notes=None,
    changed_by=None,
):
    if reservation.status != ReservationRecord.STATUS_ACTIVE:
        raise ValidationError("Only active reservation records can be edited.")

    before = _snapshot(reservation, RESERVATION_HISTORY_FIELDS)

    if reserved_for_type is not None:
        party_type, party_client, party_supplier, party_internal, party_name = (
            _resolve_reservation_party(
                party_type=reserved_for_type,
                client=reserved_for_client,
                supplier=reserved_for_supplier,
                internal=reserved_for_internal,
                internal_name_input=internal_name_input,
                internal_kind_input=internal_kind_input,
                client_name_input=client_name_input,
                supplier_name_input=supplier_name_input,
            )
        )
        reservation.reserved_for = party_name
        reservation.reserved_for_type = party_type
        reservation.reserved_for_client = party_client
        reservation.reserved_for_supplier = party_supplier
        reservation.reserved_for_internal = party_internal
    if reason is not None:
        reservation.reason = reason.strip()
    if notes is not None:
        reservation.notes = notes
    reservation.save(
        update_fields=(
            "reserved_for",
            "reserved_for_type",
            "reserved_for_client",
            "reserved_for_supplier",
            "reserved_for_internal",
            "reason",
            "notes",
        )
    )
    log_record_changes(
        "reservation",
        reservation,
        reservation.reservation_number,
        before,
        _snapshot(reservation, RESERVATION_HISTORY_FIELDS),
        changed_by,
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
    assigned_to=None,
    assigned_to_name_input="",
    assigned_to_kind_input="",
    reason="",
    issue_date=None,
    expected_return_date=None,
    notes="",
    issued_by=None,
):
    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not unique_ids:
        raise ValidationError("At least one stock unit is required.")

    assignee = _resolve_internal_party(
        assigned_to, assigned_to_name_input, assigned_to_kind_input
    )
    if assignee is None:
        raise ValidationError("Choose the employee or department this assignment is for.")
    if (
        expected_return_date
        and issue_date
        and expected_return_date < issue_date
    ):
        raise ValidationError("Expected return date cannot be before the assignment date.")

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
        issued_to=assignee.name,
        assigned_to=assignee,
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


def update_issue_record_header(
    issue,
    *,
    assigned_to=None,
    assigned_to_name_input="",
    assigned_to_kind_input="",
    reason=None,
    issue_date=None,
    expected_return_date=_UNSET,
    notes=None,
    changed_by=None,
):
    if issue.status != IssueRecord.STATUS_ACTIVE:
        raise ValidationError("Only active issue records can be edited.")

    before = _snapshot(issue, ISSUE_HISTORY_FIELDS)

    assignee = _resolve_internal_party(
        assigned_to, assigned_to_name_input, assigned_to_kind_input
    )
    if assignee is not None:
        issue.issued_to = assignee.name
        issue.assigned_to = assignee
    if reason is not None:
        issue.reason = reason.strip()
    if issue_date is not None:
        issue.issue_date = issue_date
    if expected_return_date is not _UNSET:
        issue.expected_return_date = expected_return_date
    if (
        issue.expected_return_date
        and issue.issue_date
        and issue.expected_return_date < issue.issue_date
    ):
        raise ValidationError("Expected return date cannot be before the assignment date.")
    if notes is not None:
        issue.notes = notes
    issue.save(
        update_fields=(
            "issued_to",
            "assigned_to",
            "reason",
            "issue_date",
            "expected_return_date",
            "notes",
        )
    )
    log_record_changes(
        "issue",
        issue,
        issue.issue_number,
        before,
        _snapshot(issue, ISSUE_HISTORY_FIELDS),
        changed_by,
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


def _create_client_owned_units(client_items, client):
    """Create the units for items a client brought in that were never in the
    system (sold before it was used). They are born in Repair, owned by the
    client, and counted nowhere in our stock."""
    if not client_items:
        raise ValidationError("Enter at least one item: its product and serial number.")

    seen = set()
    units = []
    for entry in client_items:
        product = entry.get("product")
        serial = (entry.get("serial_number") or "").strip()
        if product is None:
            raise ValidationError("Choose the product for every item.")
        if not serial:
            raise ValidationError("Enter the serial number for every item.")
        if serial.lower() in seen:
            raise ValidationError(f"Serial number {serial} is entered twice.")
        seen.add(serial.lower())

        existing = ProductUnit.objects.filter(serial_number__iexact=serial).first()
        if existing is not None:
            hint = (
                " Use Create Client Return for it."
                if existing.status == ProductUnit.STATUS_SOLD
                else ""
            )
            raise ValidationError(
                f"Serial number {serial} is already in the system "
                f"({existing.get_status_display()}).{hint}"
            )

        units.append(
            ProductUnit.objects.create(
                product=product,
                serial_number=serial,
                status=ProductUnit.STATUS_REPAIR,
                owner_client=client,
            )
        )
    return units


@transaction.atomic
def create_repair_record(
    *,
    unit_ids=None,
    client_items=None,
    repair_reason,
    vendor=None,
    vendor_name_input="",
    source=RepairRecord.SOURCE_INTERNAL_STOCK,
    source_client=None,
    source_client_name_input="",
    source_internal=None,
    source_internal_name_input="",
    source_internal_kind_input="",
    repair_date=None,
    notes="",
    sent_by=None,
):
    is_client_item = source == RepairRecord.SOURCE_CLIENT_ITEM
    if is_client_item and unit_ids:
        raise ValidationError(
            "A client's item is entered by product and serial number, not picked from stock."
        )
    if not is_client_item and client_items:
        raise ValidationError(
            "Items can only be entered by serial number when the source is the client's item."
        )

    unique_ids = list(dict.fromkeys(unit_ids or []))
    if not is_client_item and not unique_ids:
        raise ValidationError("At least one stock unit is required.")
    vendor = _resolve_supplier(vendor, vendor_name_input)
    if vendor is None:
        raise ValidationError("Supplier is required.")

    source, source_client, source_internal = _resolve_repair_source(
        source=source,
        source_client=source_client,
        source_client_name_input=source_client_name_input,
        source_internal=source_internal,
        source_internal_name_input=source_internal_name_input,
        source_internal_kind_input=source_internal_kind_input,
    )

    new_client_unit_ids = set()
    if is_client_item:
        units = _create_client_owned_units(client_items, source_client)
        new_client_unit_ids = {unit.pk for unit in units}
    else:
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
        vendor=vendor,
        source=source,
        source_client=source_client,
        source_internal=source_internal,
        repair_date=repair_date or timezone.localdate(),
        notes=notes,
        sent_by=sent_by,
    )

    for unit in units:
        is_new_client_unit = unit.pk in new_client_unit_ids
        from_status = "" if is_new_client_unit else unit.status
        RepairItem.objects.create(
            repair=repair,
            product_unit=unit,
            product=unit.product,
        )
        if not is_new_client_unit:
            unit.status = ProductUnit.STATUS_REPAIR
            unit.save(update_fields=("status", "sold_date"))
        create_stock_movement(
            product_unit=unit,
            movement_type=(
                StockMovement.TYPE_CLIENT_ITEM_RECEIVED
                if is_new_client_unit
                else StockMovement.TYPE_SENT_TO_REPAIR
            ),
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


def update_repair_record_header(
    repair,
    *,
    repair_reason=None,
    vendor=None,
    vendor_name_input="",
    repair_date=None,
    notes=None,
    changed_by=None,
):
    if repair.status != RepairRecord.STATUS_ACTIVE:
        raise ValidationError("Only active repair records can be edited.")

    before = _snapshot(repair, REPAIR_HISTORY_FIELDS)
    vendor = _resolve_supplier(vendor, vendor_name_input)
    if repair_reason is not None:
        repair.repair_reason = repair_reason.strip()
    if vendor is not None:
        repair.vendor = vendor
    if repair_date is not None:
        repair.repair_date = repair_date
    if notes is not None:
        repair.notes = notes
    repair.save(update_fields=("repair_reason", "vendor", "repair_date", "notes"))
    log_record_changes(
        "repair",
        repair,
        repair.repair_number,
        before,
        _snapshot(repair, REPAIR_HISTORY_FIELDS),
        changed_by,
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
        ProductUnit.STATUS_SOLD,
    ):
        raise ValidationError("Repair resolution must be available, inactive, or returned to client.")
    if (
        resolution != ProductUnit.STATUS_SOLD
        and repair.items.filter(product_unit__owner_client__isnull=False).exists()
    ):
        raise ValidationError(
            "This item belongs to the client, so the repair can only be closed as Returned to Client."
        )
    if (
        resolution == ProductUnit.STATUS_SOLD
        and repair.source != RepairRecord.SOURCE_CLIENT_ITEM
        and (
            not repair.client_return_id
            or repair.client_return.status == ClientReturnRecord.STATUS_CANCELLED
        )
    ):
        raise ValidationError(
            "Returned to Client is only available for repairs created from a client return "
            "or for a client's own item."
        )

    return_client = None
    if resolution == ProductUnit.STATUS_SOLD:
        return_client = repair.source_client or (
            repair.client_return.client if repair.client_return_id else None
        )
        if return_client is None:
            raise ValidationError(
                "This repair has no client to return the units to. Fix the client first."
            )

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

    if resolution == ProductUnit.STATUS_AVAILABLE:
        movement_type = StockMovement.TYPE_REPAIR_RESOLVED
    elif resolution == ProductUnit.STATUS_SOLD:
        movement_type = StockMovement.TYPE_REPAIR_RETURNED_TO_CLIENT
    else:
        movement_type = StockMovement.TYPE_REPAIR_DEACTIVATED

    # "Returned to Client": the units go straight back to the client without
    # passing through Available. A zero-value, flagged delivery records it so the
    # history shows the unit going back out, linked to this repair.
    warranty_delivery = None
    if resolution == ProductUnit.STATUS_SOLD:
        warranty_delivery = DeliveryRecord.objects.create(
            client=return_client,
            customer_name=return_client.name,
            delivery_date=repair.resolved_date,
            notes=f"Warranty return after repair {repair.repair_number}",
            status=DeliveryRecord.STATUS_COMPLETED,
            is_warranty_return=True,
            from_repair=repair,
            created_by=resolved_by,
        )

    for item in items:
        unit = item.product_unit
        from_status = unit.status
        unit.status = resolution
        if resolution == ProductUnit.STATUS_INACTIVE:
            unit.isactive = False
        elif warranty_delivery is not None:
            unit.sold_date = warranty_delivery.delivery_date
            DeliveryItem.objects.create(
                delivery=warranty_delivery,
                product_unit=unit,
                product=unit.product,
                sale_price=0,
            )
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
            delivery_record=warranty_delivery,
            reference=repair.repair_number,
        )

    return repair


@transaction.atomic
def create_removal_record(
    *,
    unit_ids,
    reason,
    removal_date=None,
    notes="",
    removed_by=None,
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

    # Sold units have their own lifecycle via Client Return; already-removed
    # units can't be removed again. Every other status (available, reserved,
    # issued, repair) is eligible -- unlike the other five workflows, this one
    # isn't restricted to "available" only, since a unit can turn out lost,
    # stolen, or damaged beyond repair while reserved, issued, or in repair.
    client_owned = [unit.serial_number for unit in units if unit.owner_client_id]
    if client_owned:
        raise ValidationError(
            "These items belong to a client and cannot be removed from inventory: "
            + ", ".join(sorted(client_owned))
        )
    ineligible_units = [
        unit.serial_number
        for unit in units
        if not unit.isactive
        or unit.status in (ProductUnit.STATUS_SOLD, ProductUnit.STATUS_REMOVED)
    ]
    if ineligible_units:
        raise ValidationError(
            "Sold or already-removed stock units cannot be removed: "
            + ", ".join(sorted(ineligible_units))
        )

    removal = RemovalRecord.objects.create(
        reason=reason,
        removal_date=removal_date or timezone.localdate(),
        notes=notes,
        removed_by=removed_by,
    )

    for unit in units:
        from_status = unit.status
        RemovalItem.objects.create(
            removal=removal,
            product_unit=unit,
            product=unit.product,
        )
        unit.status = ProductUnit.STATUS_REMOVED
        unit.save(update_fields=("status",))
        create_stock_movement(
            product_unit=unit,
            movement_type=StockMovement.TYPE_REMOVED,
            from_status=from_status,
            to_status=ProductUnit.STATUS_REMOVED,
            reason=removal.get_reason_display(),
            notes=notes,
            performed_by=removed_by,
            movement_date=removal.removal_date,
            removal_record=removal,
            reference=removal.removal_number,
        )

    return removal


def _unit_has_delivery(unit):
    return unit.delivery_items.exists()


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
    current_delivery_item = _latest_delivery_item_for_unit(unit)
    if current_delivery_item is None:
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
    po_number=None,
    supplier_invoice_number=None,
    received_date=None,
    notes=None,
    items=None,
    changed_by=None,
):
    if receiving.status == ReceivingRecord.STATUS_CANCELLED:
        raise ValidationError("Cancelled receiving records cannot be edited.")

    before = _snapshot(receiving, RECEIVING_HISTORY_FIELDS)
    if supplier is not None:
        receiving.supplier = supplier
    if po_number is not None:
        receiving.po_number = po_number.strip()
    if supplier_invoice_number is not None:
        receiving.supplier_invoice_number = supplier_invoice_number.strip()
    if received_date is not None:
        receiving.received_date = received_date
    if notes is not None:
        receiving.notes = notes
    receiving.save(
        update_fields=(
            "supplier",
            "po_number",
            "supplier_invoice_number",
            "received_date",
            "notes",
        )
    )
    log_record_changes(
        "receiving",
        receiving,
        receiving.receiving_number,
        before,
        _snapshot(receiving, RECEIVING_HISTORY_FIELDS),
        changed_by,
    )

    for item_data in items or []:
        item_id = item_data.get("id")
        if not item_id:
            continue
        try:
            item = receiving.items.select_related("product_unit").get(pk=item_id)
        except ReceivingItem.DoesNotExist:
            continue

        line = item.product_unit.serial_number if item.product_unit_id else str(item.product)
        line_fields = (("cost", f"Line cost ({line})"), ("notes", f"Line notes ({line})"))
        line_before = _snapshot(item, line_fields)
        update_fields = []
        if "cost" in item_data:
            item.cost = item_data["cost"]
            update_fields.append("cost")
        if "notes" in item_data:
            item.notes = item_data["notes"]
            update_fields.append("notes")
        if update_fields:
            item.save(update_fields=update_fields)
            log_record_changes(
                "receiving",
                receiving,
                receiving.receiving_number,
                line_before,
                _snapshot(item, line_fields),
                changed_by,
            )

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
    invoice_number=None,
    delivery_date=None,
    notes=None,
    items=None,
    changed_by=None,
):
    if delivery.status == DeliveryRecord.STATUS_CANCELLED:
        raise ValidationError("Cancelled delivery records cannot be edited.")

    before = _snapshot(delivery, DELIVERY_HISTORY_FIELDS)

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
    if invoice_number is not None:
        delivery.invoice_number = invoice_number.strip()
    if delivery_date is not None:
        delivery.delivery_date = delivery_date
    if notes is not None:
        delivery.notes = notes
    delivery.save(
        update_fields=(
            "customer_name",
            "invoice_number",
            "delivery_date",
            "notes",
        )
    )
    log_record_changes(
        "delivery",
        delivery,
        delivery.delivery_number,
        before,
        _snapshot(delivery, DELIVERY_HISTORY_FIELDS),
        changed_by,
    )

    for item_data in items or []:
        item_id = item_data.get("id")
        if not item_id:
            continue
        try:
            item = delivery.items.select_related("product_unit").get(pk=item_id)
        except DeliveryItem.DoesNotExist:
            continue
        if "notes" in item_data:
            line = item.product_unit.serial_number if item.product_unit_id else str(item.product)
            line_fields = (("notes", f"Line notes ({line})"),)
            line_before = _snapshot(item, line_fields)
            item.notes = item_data["notes"]
            item.save(update_fields=("notes",))
            log_record_changes(
                "delivery",
                delivery,
                delivery.delivery_number,
                line_before,
                _snapshot(item, line_fields),
                changed_by,
            )

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
    if delivery.is_warranty_return:
        raise ValidationError(
            "Warranty return deliveries cannot be cancelled; the unit was already repaired and returned to the client."
        )

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


def _resolve_upgrade_client(client, client_name_input):
    """An existing client, or one created from a typed name (the picker's inline
    "create" option), the same way a Delivery creates a new client."""
    if client is None and (client_name_input or "").strip():
        client, _created = Client.objects.get_or_create(name=client_name_input.strip())
    if client is None:
        raise ValidationError("Choose the client this upgrade was done for.")
    return client


def _validate_upgrade_state(status, upgrade_date, updater):
    if status not in (
        ClientUpgradeRecord.STATUS_NEEDS_UPGRADE,
        ClientUpgradeRecord.STATUS_UPGRADED,
    ):
        raise ValidationError("Status must be needs upgrade or upgraded.")
    if status == ClientUpgradeRecord.STATUS_UPGRADED:
        if upgrade_date is None:
            raise ValidationError("Choose the date the upgrade was done.")
        if not updater:
            raise ValidationError("Enter the updater number that was used.")


@transaction.atomic
def create_client_upgrade_record(
    *,
    client=None,
    client_name_input="",
    status=ClientUpgradeRecord.STATUS_NEEDS_UPGRADE,
    updater="",
    upgrade_date=None,
    notes="",
    created_by=None,
):
    client = _resolve_upgrade_client(client, client_name_input)
    updater = (updater or "").strip()
    _validate_upgrade_state(status, upgrade_date, updater)

    return ClientUpgradeRecord.objects.create(
        client=client,
        client_name=client.name,
        status=status,
        upgrade_date=upgrade_date,
        updater=updater,
        notes=notes or "",
        created_by=created_by,
    )


@transaction.atomic
def update_client_upgrade_record(
    upgrade,
    *,
    client=None,
    client_name_input="",
    status=None,
    updater=None,
    upgrade_date=None,
    clear_upgrade_date=False,
    notes=None,
    changed_by=None,
):
    if upgrade.status == ClientUpgradeRecord.STATUS_CANCELLED:
        raise ValidationError("Cancelled client upgrade records cannot be edited.")

    before = _snapshot(upgrade, CLIENT_UPGRADE_HISTORY_FIELDS)

    if client is not None or (client_name_input or "").strip():
        client = _resolve_upgrade_client(client, client_name_input)
        upgrade.client = client
        upgrade.client_name = client.name
    if status is not None:
        upgrade.status = status
    if updater is not None:
        upgrade.updater = updater.strip()
    if upgrade_date is not None:
        upgrade.upgrade_date = upgrade_date
    elif clear_upgrade_date:
        upgrade.upgrade_date = None
    if notes is not None:
        upgrade.notes = notes

    _validate_upgrade_state(upgrade.status, upgrade.upgrade_date, upgrade.updater)
    upgrade.save(
        update_fields=(
            "client",
            "client_name",
            "status",
            "upgrade_date",
            "updater",
            "notes",
        )
    )
    log_record_changes(
        "client_upgrade",
        upgrade,
        upgrade.upgrade_number,
        before,
        _snapshot(upgrade, CLIENT_UPGRADE_HISTORY_FIELDS),
        changed_by,
    )
    return upgrade


@transaction.atomic
def cancel_client_upgrade_record(upgrade, *, cancelled_by=None, cancel_reason=""):
    if upgrade.status == ClientUpgradeRecord.STATUS_CANCELLED:
        return upgrade

    upgrade.status = ClientUpgradeRecord.STATUS_CANCELLED
    upgrade.isactive = False
    upgrade.cancel_reason = (cancel_reason or "").strip()
    upgrade.cancelled_at = timezone.now()
    upgrade.cancelled_by = cancelled_by
    upgrade.save(
        update_fields=(
            "status",
            "isactive",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
        )
    )
    return upgrade
