import re

from django.db import migrations, models

# The two serial formats the frontend used to build when no serial was typed:
#   Receive Stock:  <SKU>-<6-digit batch>-<line>-<index>   e.g. ABC-123456-01-003
#   Add Unit:       <SKU>-<6-digit batch>-<index>          e.g. ABC-123456-003
# (line is zero-padded to 2 digits, index to 3; wider only past 99 / 999.)
# Matching is done in Python on purpose (no database-specific regex), and this
# logic is deliberately copied here: a migration must not depend on app code
# that can change later.
_RECEIVING_SUFFIX = re.compile(r"^\d{6}-\d{2,}-\d{3,}$")
_ADD_UNIT_SUFFIX = re.compile(r"^\d{6}-\d{3,}$")
_LOOKS_GENERATED = re.compile(r"-\d{6}-(\d{2,}-)?\d{3,}$")


def is_generated_serial(sku, serial):
    """True only when the serial is the product's own SKU plus exactly one of
    the two generated suffix formats."""
    if not sku or not serial or not serial.startswith(sku + "-"):
        return False
    suffix = serial[len(sku) + 1:]
    return bool(_RECEIVING_SUFFIX.match(suffix) or _ADD_UNIT_SUFFIX.match(suffix))


def find_generated_units(units):
    """Split units into (matched ids, near-miss rows). A near miss is not
    matched but looks generated: it ends in a generated-looking suffix or
    starts with its own SKU. They are reported, never guessed."""
    matched = []
    near_misses = []
    for unit in units:
        sku = unit.product.sku
        serial = unit.serial_number
        if is_generated_serial(sku, serial):
            matched.append(unit.pk)
        elif _LOOKS_GENERATED.search(serial or "") or (sku and (serial or "").startswith(sku + "-")):
            near_misses.append((unit.pk, sku, serial))
    return matched, near_misses


def mark_generated_serials(apps, schema_editor):
    ProductUnit = apps.get_model("bim_stock", "ProductUnit")
    units = ProductUnit.objects.select_related("product").only(
        "id", "serial_number", "product__sku"
    )
    matched, near_misses = find_generated_units(units)
    for start in range(0, len(matched), 500):
        ProductUnit.objects.filter(pk__in=matched[start:start + 500]).update(
            serial_is_generated=True
        )
    print(f"\n  serial_is_generated: marked {len(matched)} unit(s) as generated.")
    if near_misses:
        print(f"  {len(near_misses)} near-miss(es) left as real serials (id, sku, serial):")
        for row in near_misses:
            print(f"    {row}")
    else:
        print("  No near-misses.")


class Migration(migrations.Migration):

    dependencies = [
        ('bim_stock', '0043_product_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='serial_is_generated',
            field=models.BooleanField(default=False),
        ),
        # Reverse is a no-op: reversing the migration drops the column above.
        migrations.RunPython(mark_generated_serials, migrations.RunPython.noop),
    ]
