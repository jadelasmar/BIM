from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ProductUnit, ReceivingItem, ReceivingRecord


def _clean_serial_numbers(serial_numbers):
    if not serial_numbers:
        return []

    cleaned = [str(serial).strip() for serial in serial_numbers if str(serial).strip()]
    if len(cleaned) != len(set(cleaned)):
        raise ValidationError("Serial numbers must be unique within a receiving item.")
    return cleaned


def _create_receiving_item(receiving, supplier, received_date, item_data):
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
        )

    return receiving
