"""One-off command to seed realistic demo data for Command Center KPIs.

NOT a permanent feature. All seeded records live under a fixed set of
Category/Brand/Supplier/Client names (SEED_* below) that don't exist in a
normal BIM Nexus install, so they never mix with real data and can always
be found and removed again with:

    python manage.py seed_demo_data --clear

Running the command with no flags clears any previously seeded demo data
first, then reseeds from scratch -- safe to re-run any time.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.stock import services
from apps.stock.models import (
    Brand,
    Category,
    Client,
    ClientReturnRecord,
    DeliveryRecord,
    IssueRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingRecord,
    RemovalRecord,
    RepairRecord,
    ReservationRecord,
    StockMovement,
    Supplier,
)
from apps.stock.selectors import low_stock_counts

User = get_user_model()

SEED_NOTE = "[Seed data] "

SUPPLIERS = {
    "Nova Distribution Co.": dict(contact_person="Elena Marsh", phone="+1 555-201-3344", email="orders@novadist.example.com"),
    "Falcon Wholesale": dict(contact_person="Marcus Byrne", phone="+1 555-208-9021", email="sales@falconwholesale.example.com"),
    "BlueHarbor Trading Co.": dict(contact_person="Priya Nair", phone="+1 555-214-7765", email="accounts@blueharbor.example.com"),
    "Summit Supply Partners": dict(contact_person="Owen Castillo", phone="+1 555-219-4482", email="info@summitsupply.example.com"),
    "Redline Logistics": dict(contact_person="Farah Haddad", phone="+1 555-227-6650", email="dispatch@redlinelogistics.example.com"),
}

CLIENTS = {
    "Coral Bay Resort": dict(contact_person="Diane Foster", phone="+1 555-301-2210", email="procurement@coralbayresort.example.com"),
    "Meridian Law Group": dict(contact_person="Samuel Ortiz", phone="+1 555-306-8834", email="admin@meridianlaw.example.com"),
    "Northfield School District": dict(contact_person="Grace Lin", phone="+1 555-311-5567", email="it@northfieldsd.example.com"),
    "Vantage Realty Partners": dict(contact_person="Theo Bennett", phone="+1 555-318-9012", email="ops@vantagerealty.example.com"),
    "Harborview Medical Center": dict(contact_person="Nadia Rahman", phone="+1 555-322-4471", email="supplychain@harborviewmc.example.com"),
}

# Each product's `buckets` list assigns its freshly-received (all "available")
# units to a storyline that fully determines which services.py workflow
# calls are run against them and where they end up:
#   stay_available               -> untouched, stays available
#   sold                         -> delivered, stays sold
#   sold_then_returned_available -> delivered, then client-returned to available
#   sold_then_returned_repair    -> delivered, then client-returned to repair
#   reserved_active               -> reserved, left active
#   reserved_released             -> reserved, then released back to available
#   issued_active                  -> issued, left active
#   issued_returned                -> issued, then returned back to available
#   repair_active                   -> sent to repair, left active
#   repair_resolved_available       -> sent to repair, then resolved to available
#   removed                          -> removed permanently
# Two products (tplink_ap, epson_projector_qty) are quantity-only receiving
# lines with no serial numbers -- no ProductUnit rows are ever created for
# them, which is the "quantity-tracked" half of the requested product mix.
PRODUCT_PLAN = [
    # -- deliberately out-of-stock / low-stock, exact numbers --
    dict(key="lenovo_t14", category="Laptops", brand="Lenovo", model="ThinkPad T14 Gen 4",
         descript="Lenovo ThinkPad T14 Gen 4 Laptop", reorder=3, cost=780,
         buckets=[("stay_available", 2), ("sold", 2), ("removed", 1)]),
    dict(key="cisco_switch", category="Networking Equipment", brand="Cisco", model="Catalyst 1000 24P",
         descript="Cisco Catalyst 1000 24-Port Switch", reorder=2, cost=650,
         buckets=[("stay_available", 1), ("sold", 1), ("issued_active", 1), ("removed", 1)]),
    dict(key="honeywell_pos", category="POS Terminals", brand="Honeywell", model="Vega 3000",
         descript="Honeywell Vega 3000 POS Terminal", reorder=2, cost=410,
         buckets=[("sold", 3)]),
    dict(key="tplink_ap", category="Networking Equipment", brand="TP-Link", model="EAP670",
         descript="TP-Link EAP670 Wireless Access Point", reorder=5, cost=95,
         quantity_only=15),
    dict(key="epson_projector_qty", category="Projectors", brand="Epson", model="EB-X06",
         descript="Epson EB-X06 Business Projector", reorder=4, cost=380,
         quantity_only=8),
    # -- healthy stock, generous margins above reorder level --
    dict(key="lenovo_e14", category="Laptops", brand="Lenovo", model="ThinkPad E14 Gen 5",
         descript="Lenovo ThinkPad E14 Gen 5 Laptop", reorder=2, cost=650,
         buckets=[("stay_available", 5), ("sold", 2), ("sold_then_returned_available", 1)]),
    dict(key="dell_latitude", category="Laptops", brand="Dell", model="Latitude 5440",
         descript="Dell Latitude 5440 Laptop", reorder=2, cost=720,
         buckets=[("stay_available", 4), ("sold", 1), ("issued_returned", 1), ("repair_active", 1)]),
    dict(key="dell_monitor", category="Monitors", brand="Dell", model="P2422H",
         descript="Dell P2422H 24-inch Monitor", reorder=2, cost=140,
         buckets=[("stay_available", 4), ("sold", 1), ("sold_then_returned_available", 1), ("reserved_released", 1)]),
    dict(key="benq_monitor", category="Monitors", brand="BenQ", model="GW2480",
         descript="BenQ GW2480 24-inch Monitor", reorder=2, cost=125,
         buckets=[("stay_available", 4), ("sold", 2), ("reserved_active", 1), ("sold_then_returned_repair", 1)]),
    dict(key="honeywell_scanner", category="Barcode Scanners", brand="Honeywell", model="Voyager 1250g",
         descript="Honeywell Voyager 1250g Barcode Scanner", reorder=2, cost=95,
         buckets=[("stay_available", 3), ("sold", 1), ("issued_active", 1), ("reserved_released", 1)]),
    dict(key="datalogic_scanner", category="Barcode Scanners", brand="Datalogic", model="QuickScan QD2131",
         descript="Datalogic QuickScan QD2131 Barcode Scanner", reorder=2, cost=110,
         buckets=[("stay_available", 3), ("sold", 2), ("removed", 1)]),
    dict(key="epson_pos", category="POS Terminals", brand="Epson", model="TM-T88VI",
         descript="Epson TM-T88VI POS Printer", reorder=2, cost=310,
         buckets=[("stay_available", 3), ("sold", 2), ("reserved_active", 1)]),
    dict(key="apc_1500", category="Power Backup", brand="APC", model="Back-UPS 1500VA",
         descript="APC Back-UPS 1500VA", reorder=2, cost=155,
         buckets=[("stay_available", 4), ("sold", 1), ("issued_returned", 1)]),
    dict(key="apc_750", category="Power Backup", brand="APC", model="Smart-UPS 750VA",
         descript="APC Smart-UPS 750VA", reorder=2, cost=210,
         buckets=[("stay_available", 3), ("sold", 1), ("repair_active", 1)]),
    dict(key="dell_dock", category="Docking Stations", brand="Dell", model="WD19S",
         descript="Dell WD19S Docking Station", reorder=2, cost=140,
         buckets=[("stay_available", 4), ("sold", 1), ("reserved_released", 1)]),
    dict(key="lenovo_dock", category="Docking Stations", brand="Lenovo", model="ThinkPad USB-C Dock Gen2",
         descript="Lenovo ThinkPad USB-C Dock Gen 2", reorder=2, cost=110,
         buckets=[("stay_available", 3), ("sold", 1), ("issued_active", 1)]),
    dict(key="benq_projector", category="Projectors", brand="BenQ", model="MW632ST",
         descript="BenQ MW632ST Short-Throw Projector", reorder=2, cost=430,
         buckets=[("stay_available", 3), ("sold", 1), ("removed", 1)]),
    dict(key="tplink_router", category="Networking Equipment", brand="TP-Link", model="Archer AX55",
         descript="TP-Link Archer AX55 Wi-Fi 6 Router", reorder=2, cost=85,
         buckets=[("stay_available", 4), ("sold", 1), ("repair_resolved_available", 1), ("reserved_active", 1)]),
]

RECEIVING_BATCHES = [
    dict(supplier="Nova Distribution Co.", po="PO-DEMO-1001", invoice="INV-DEMO-88001", days_ago=52,
         product_keys=["lenovo_t14", "lenovo_e14", "lenovo_dock"]),
    dict(supplier="Falcon Wholesale", po="PO-DEMO-1002", invoice="INV-DEMO-88002", days_ago=46,
         product_keys=["dell_latitude", "dell_monitor", "dell_dock"]),
    dict(supplier="BlueHarbor Trading Co.", po="PO-DEMO-1003", invoice="INV-DEMO-88003", days_ago=39,
         product_keys=["cisco_switch", "tplink_router", "tplink_ap"]),
    dict(supplier="Summit Supply Partners", po="PO-DEMO-1004", invoice="INV-DEMO-88004", days_ago=33,
         product_keys=["benq_monitor", "benq_projector"]),
    dict(supplier="Redline Logistics", po="PO-DEMO-1005", invoice="INV-DEMO-88005", days_ago=27,
         product_keys=["honeywell_scanner", "datalogic_scanner"]),
    dict(supplier="Falcon Wholesale", po="PO-DEMO-1006", invoice="INV-DEMO-88006", days_ago=19,
         product_keys=["epson_pos", "honeywell_pos", "apc_1500", "apc_750"]),
    dict(supplier="Summit Supply Partners", po="PO-DEMO-1007", invoice="INV-DEMO-88007", days_ago=9,
         product_keys=["epson_projector_qty"]),
]

SEED_CATEGORY_NAMES = sorted({plan["category"] for plan in PRODUCT_PLAN})
SEED_BRAND_NAMES = sorted({plan["brand"] for plan in PRODUCT_PLAN})
SEED_SUPPLIER_NAMES = list(SUPPLIERS)
SEED_CLIENT_NAMES = list(CLIENTS)

RECORD_TYPES_BY_ITEM_RELATION = {
    "Client Return": ClientReturnRecord,
    "Delivery": DeliveryRecord,
    "Reservation": ReservationRecord,
    "Temporary Assignment": IssueRecord,
    "Repair": RepairRecord,
    "Removal": RemovalRecord,
    "Receiving": ReceivingRecord,
}


def _chunk(items, sizes):
    chunks = []
    cursor = 0
    for size in sizes:
        chunks.append(items[cursor:cursor + size])
        cursor += size
    return chunks


class Command(BaseCommand):
    help = (
        "One-off: seed realistic demo data (products, stock units, suppliers, "
        "clients, and records across all 7 workflows) so the Command Center "
        "dashboard shows varied, non-trivial KPIs. Not a permanent feature -- "
        "safe to re-run (clears its own previous data first) or remove entirely "
        "with --clear."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove previously seeded demo data and exit (does not reseed).",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            with transaction.atomic():
                self._clear()
            self.stdout.write(self.style.SUCCESS("Seeded demo data removed."))
            return

        with transaction.atomic():
            self._clear()
            self._seed()
        self._print_summary()

    # -- clearing -----------------------------------------------------

    def _clear(self):
        StockMovement.objects.filter(product__category__name__in=SEED_CATEGORY_NAMES).delete()

        for model in RECORD_TYPES_BY_ITEM_RELATION.values():
            model.objects.filter(
                items__product__category__name__in=SEED_CATEGORY_NAMES
            ).distinct().delete()

        ProductUnit.objects.filter(product__category__name__in=SEED_CATEGORY_NAMES).delete()
        Product.objects.filter(category__name__in=SEED_CATEGORY_NAMES).delete()
        ProductModel.objects.filter(brand__brandname__in=SEED_BRAND_NAMES).delete()
        Brand.objects.filter(brandname__in=SEED_BRAND_NAMES).delete()
        Category.objects.filter(name__in=SEED_CATEGORY_NAMES).delete()
        Supplier.objects.filter(name__in=SEED_SUPPLIER_NAMES).delete()
        Client.objects.filter(name__in=SEED_CLIENT_NAMES).delete()

    # -- seeding --------------------------------------------------------

    def _seed(self):
        today = timezone.localdate()
        performed_by = (
            User.objects.filter(is_superuser=True).order_by("pk").first()
            or User.objects.order_by("pk").first()
        )

        suppliers = {
            name: Supplier.objects.get_or_create(name=name, defaults=details)[0]
            for name, details in SUPPLIERS.items()
        }
        clients = {
            name: Client.objects.get_or_create(name=name, defaults=details)[0]
            for name, details in CLIENTS.items()
        }

        categories = {
            name: Category.objects.get_or_create(name=name)[0] for name in SEED_CATEGORY_NAMES
        }
        brands = {
            name: Brand.objects.get_or_create(brandname=name)[0] for name in SEED_BRAND_NAMES
        }

        plan_by_key = {plan["key"]: plan for plan in PRODUCT_PLAN}
        products = {}
        for plan in PRODUCT_PLAN:
            model_obj, _ = ProductModel.objects.get_or_create(
                brand=brands[plan["brand"]], modelname=plan["model"]
            )
            product, _ = Product.objects.get_or_create(
                category=categories[plan["category"]],
                model=model_obj,
                defaults=dict(descript=plan["descript"], reorder_stock_level=plan["reorder"]),
            )
            products[plan["key"]] = product

        # -- receiving: creates every ProductUnit (all start "available") --
        units_by_key = {}
        for batch in RECEIVING_BATCHES:
            supplier = suppliers[batch["supplier"]]
            received_date = today - timedelta(days=batch["days_ago"])
            items = []
            for key in batch["product_keys"]:
                plan = plan_by_key[key]
                product = products[key]
                if "quantity_only" in plan:
                    items.append({
                        "product": product,
                        "quantity": plan["quantity_only"],
                        "cost": plan["cost"],
                        "notes": SEED_NOTE + "Bulk receiving, not individually serialized.",
                    })
                else:
                    total = sum(count for _, count in plan["buckets"])
                    serials = [f"DEMO-{product.sku}-{i:03d}" for i in range(1, total + 1)]
                    items.append({
                        "product": product,
                        "quantity": total,
                        "serial_numbers": serials,
                        "cost": plan["cost"],
                    })
            services.create_receiving_record(
                items=items,
                supplier=supplier,
                po_number=batch["po"],
                supplier_invoice_number=batch["invoice"],
                received_date=received_date,
                notes=SEED_NOTE + "Demo receiving batch.",
                created_by=performed_by,
            )
            for key in batch["product_keys"]:
                if "quantity_only" in plan_by_key[key]:
                    continue
                units_by_key[key] = list(
                    ProductUnit.objects.filter(product=products[key]).order_by("serial_number")
                )

        # -- slice each product's units into storyline pools --
        pools = {
            name: []
            for name in (
                "sold",
                "sold_then_returned_available",
                "sold_then_returned_repair",
                "reserved_active",
                "reserved_released",
                "issued_active",
                "issued_returned",
                "repair_active",
                "repair_resolved_available",
                "removed",
            )
        }
        for key, plan in plan_by_key.items():
            if "quantity_only" in plan:
                continue
            units = units_by_key[key]
            cursor = 0
            for bucket_name, count in plan["buckets"]:
                chunk = units[cursor:cursor + count]
                cursor += count
                if bucket_name != "stay_available":
                    pools[bucket_name].extend(chunk)

        # -- deliveries (everything that was ever sold goes through here first) --
        all_sold_units = (
            pools["sold"] + pools["sold_then_returned_available"] + pools["sold_then_returned_repair"]
        )
        delivery_sizes = [5, 5, 4, 4, 4, 4]
        delivery_days_ago = [24, 19, 15, 11, 6, 2]
        for idx, chunk in enumerate(_chunk(all_sold_units, delivery_sizes)):
            client_name = SEED_CLIENT_NAMES[idx % len(SEED_CLIENT_NAMES)]
            services.create_delivery_record(
                unit_ids=[unit.pk for unit in chunk],
                client=clients[client_name],
                receiver_name="Warehouse Receiving",
                invoice_number=f"INV-DEMO-CUST-{idx + 1:03d}",
                delivery_date=today - timedelta(days=delivery_days_ago[idx]),
                notes=SEED_NOTE + "Demo delivery.",
                created_by=performed_by,
            )

        # -- client returns (only possible after delivery, above) --
        for idx, unit in enumerate(pools["sold_then_returned_available"]):
            services.create_client_return_record(
                unit_ids=[unit.pk],
                resolution=ProductUnit.STATUS_AVAILABLE,
                client=clients[SEED_CLIENT_NAMES[idx % len(SEED_CLIENT_NAMES)]],
                received_from="Client Warehouse Contact",
                return_date=today - timedelta(days=3 + idx),
                reason="Wrong specification ordered",
                notes=SEED_NOTE + "Demo client return.",
                received_by=performed_by,
            )
        for idx, unit in enumerate(pools["sold_then_returned_repair"]):
            services.create_client_return_record(
                unit_ids=[unit.pk],
                resolution=ProductUnit.STATUS_REPAIR,
                client=clients[SEED_CLIENT_NAMES[(idx + 2) % len(SEED_CLIENT_NAMES)]],
                received_from="Client Site Contact",
                return_date=today - timedelta(days=4 + idx),
                reason="Defective on arrival",
                notes=SEED_NOTE + "Demo client return.",
                received_by=performed_by,
            )

        # -- reservations: two stay active, two get released/cancelled --
        reserved_active = pools["reserved_active"]
        reserved_released = pools["reserved_released"]
        if reserved_active:
            services.create_reservation_record(
                unit_ids=[reserved_active[0].pk],
                reserved_for="Field Support Team - J. Ortiz",
                reason="Deployed with field technician",
                notes=SEED_NOTE + "Demo reservation.",
                reserved_by=performed_by,
            )
        if len(reserved_active) > 1:
            services.create_reservation_record(
                unit_ids=[unit.pk for unit in reserved_active[1:]],
                reserved_for="Warehouse Expansion Project",
                reason="Held for new branch rollout",
                notes=SEED_NOTE + "Demo reservation.",
                reserved_by=performed_by,
            )
        if len(reserved_released) > 1:
            released = services.create_reservation_record(
                unit_ids=[unit.pk for unit in reserved_released[:2]],
                reserved_for="Trade Show Demo Booth",
                reason="Reserved for annual trade show",
                notes=SEED_NOTE + "Demo reservation.",
                reserved_by=performed_by,
            )
            services.release_reservation_record(
                released, released_by=performed_by, release_reason="Trade show concluded, returned to stock"
            )
        if len(reserved_released) > 2:
            cancelled = services.create_reservation_record(
                unit_ids=[unit.pk for unit in reserved_released[2:]],
                reserved_for="Branch Rollout Hold",
                reason="Tentative hold pending budget approval",
                notes=SEED_NOTE + "Demo reservation.",
                reserved_by=performed_by,
            )
            services.release_reservation_record(
                cancelled, released_by=performed_by, release_reason="Budget not approved", cancel=True
            )

        # -- temporary assignments: two stay active, one gets returned --
        issued_active = pools["issued_active"]
        issued_returned = pools["issued_returned"]
        if len(issued_active) > 1:
            services.create_issue_record(
                unit_ids=[unit.pk for unit in issued_active[:2]],
                issued_to="Front Desk - Reception",
                reason="Temporary coverage during renovation",
                notes=SEED_NOTE + "Demo temporary assignment.",
                issued_by=performed_by,
            )
        if len(issued_active) > 2:
            services.create_issue_record(
                unit_ids=[issued_active[2].pk],
                issued_to="Field Technician - M. Alvarez",
                reason="On-site client support",
                notes=SEED_NOTE + "Demo temporary assignment.",
                issued_by=performed_by,
            )
        if issued_returned:
            returned_issue = services.create_issue_record(
                unit_ids=[unit.pk for unit in issued_returned],
                issued_to="Marketing Dept - Loaner Pool",
                reason="Conference loaner equipment",
                notes=SEED_NOTE + "Demo temporary assignment.",
                issued_by=performed_by,
            )
            services.return_issue_record(
                returned_issue, returned_by=performed_by, return_reason="Conference concluded, equipment returned"
            )

        # -- repairs: two stay active, one gets resolved --
        repair_active = pools["repair_active"]
        repair_resolved = pools["repair_resolved_available"]
        if repair_active:
            services.create_repair_record(
                unit_ids=[repair_active[0].pk],
                repair_reason="Reported malfunctioning by end user",
                technician="Internal IT - R. Haddad",
                notes=SEED_NOTE + "Demo repair.",
                sent_by=performed_by,
            )
        if len(repair_active) > 1:
            services.create_repair_record(
                unit_ids=[repair_active[1].pk],
                repair_reason="Failed routine diagnostic check",
                technician="Internal IT - R. Haddad",
                notes=SEED_NOTE + "Demo repair.",
                sent_by=performed_by,
            )
        if repair_resolved:
            resolved_repair = services.create_repair_record(
                unit_ids=[unit.pk for unit in repair_resolved],
                repair_reason="Overheating under sustained load",
                technician="Vendor - TechFix Solutions",
                notes=SEED_NOTE + "Demo repair.",
                sent_by=performed_by,
            )
            services.resolve_repair_record(
                resolved_repair,
                resolution=ProductUnit.STATUS_AVAILABLE,
                resolved_by=performed_by,
                resolution_notes="Replaced faulty component and verified stable operation under load; tested OK.",
            )

        # -- removals --
        removed_units = pools["removed"]
        if len(removed_units) > 1:
            services.create_removal_record(
                unit_ids=[unit.pk for unit in removed_units[:2]],
                reason=RemovalRecord.REASON_DAMAGED,
                removal_date=today - timedelta(days=5),
                notes=SEED_NOTE + "Damaged during warehouse handling; confirmed beyond repair.",
                removed_by=performed_by,
            )
        if len(removed_units) > 2:
            services.create_removal_record(
                unit_ids=[removed_units[2].pk],
                reason=RemovalRecord.REASON_LOST,
                removal_date=today - timedelta(days=8),
                notes=SEED_NOTE + "Unit unaccounted for after quarterly stock count.",
                removed_by=performed_by,
            )
        if len(removed_units) > 3:
            services.create_removal_record(
                unit_ids=[removed_units[3].pk],
                reason=RemovalRecord.REASON_STOLEN,
                removal_date=today - timedelta(days=2),
                notes=SEED_NOTE + "Reported missing from storage room; incident logged with security.",
                removed_by=performed_by,
            )

    # -- reporting --------------------------------------------------------

    def _print_summary(self):
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write(
            f"  Products: {Product.objects.filter(category__name__in=SEED_CATEGORY_NAMES).count()}"
        )
        unit_qs = ProductUnit.objects.filter(product__category__name__in=SEED_CATEGORY_NAMES)
        self.stdout.write(f"  Stock units: {unit_qs.count()}")
        for status_value, status_label in ProductUnit.STATUS_CHOICES:
            count = unit_qs.filter(status=status_value).count()
            if count:
                self.stdout.write(f"    {status_label}: {count}")

        low_count, out_count = low_stock_counts()
        self.stdout.write(f"  Low stock products (store-wide): {low_count}")
        self.stdout.write(f"  Out of stock products (store-wide): {out_count}")
        self.stdout.write(f"  Suppliers: {Supplier.objects.filter(name__in=SEED_SUPPLIER_NAMES).count()}")
        self.stdout.write(f"  Clients: {Client.objects.filter(name__in=SEED_CLIENT_NAMES).count()}")

        for label, model in RECORD_TYPES_BY_ITEM_RELATION.items():
            count = model.objects.filter(
                items__product__category__name__in=SEED_CATEGORY_NAMES
            ).distinct().count()
            self.stdout.write(f"  {label} records: {count}")

        self.stdout.write(self.style.WARNING("Run with --clear to remove this seeded data later."))
