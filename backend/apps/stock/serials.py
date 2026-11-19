"""Auto-made serial numbers for units received without a typed serial.

These serials only exist so the unique ``ProductUnit.serial_number`` column is
filled; the unit is also flagged ``serial_is_generated=True`` by the caller so
the app knows it is a "generic" unit. Two formats, both built from the
product's own SKU (migration 0044 recognises the same two):

    Receive Stock   <SKU>-<6-digit batch>-<line, 2 digits>-<index, 3 digits>
    Add Unit        <SKU>-<6-digit batch>-<index, 3 digits>

Nothing here changes a unit's status or writes a StockMovement.
"""

import time

from .models import ProductUnit


def _batch():
    # Last six digits of the millisecond clock, like the frontend used to do.
    return f"{int(time.time() * 1000) % 1_000_000:06d}"


def _bump(batch):
    return f"{(int(batch) + 1) % 1_000_000:06d}"


def _free(candidates):
    return not ProductUnit.objects.filter(serial_number__in=candidates).exists()


def generate_receiving_serials(product, line_number, start_index, count):
    """``count`` unused serials for one receiving line (``line_number`` is the
    1-based position of the line in the receipt; numbering starts at
    ``start_index``, so it continues after any typed serials on the line)."""
    if count < 1:
        return []
    batch = _batch()
    while True:
        serials = [
            f"{product.sku}-{batch}-{line_number:02d}-{start_index + offset:03d}"
            for offset in range(count)
        ]
        if _free(serials):
            return serials
        batch = _bump(batch)


def generate_unit_serial(product):
    """One unused serial for a manually added unit."""
    batch = _batch()
    while True:
        serial = f"{product.sku}-{batch}-001"
        if _free([serial]):
            return serial
        batch = _bump(batch)
