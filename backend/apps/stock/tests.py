from django.contrib import admin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from io import BytesIO
from pathlib import Path
from PIL import Image
from tempfile import TemporaryDirectory
from unittest.mock import patch

from apps.core.ui_config import UI_TOKENS, ui_item

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
REACT_APP_SOURCE = FRONTEND_SRC / "routes" / "AppRouter.jsx"
REACT_REGISTRY_SOURCE = FRONTEND_SRC / "constants" / "uiRegistry.js"
REACT_STATUS_STYLES_SOURCE = FRONTEND_SRC / "constants" / "statusStyles.js"
REACT_SHELL_TEMPLATE = BACKEND_ROOT / "templates" / "bim" / "react_app.html"


def _admin_user_change_data(user, **overrides):
    data = {
        "username": user.username,
        "password": user.password,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": "on",
        "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
        "groups": [],
        "user_permissions": [],
    }
    data.update(overrides)
    return data

from .admin import ProductAdmin, ProductUnitAdmin, ProductUnitPurchaseForm
from .models import (
    Brand,
    Category,
    ClientReturnItem,
    ClientReturnRecord,
    DeliveryItem,
    DeliveryRecord,
    IssueItem,
    IssueRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    RepairItem,
    RepairRecord,
    ReservationItem,
    ReservationRecord,
    StockMovement,
    Supplier,
)


# Tests for Product admin list/search/filter configuration.
class ProductAdminTests(SimpleTestCase):
    def setUp(self):
        self.product_admin = ProductAdmin(Product, admin.site)

    def test_product_admin_has_staff_friendly_listing_tools(self):
        self.assertEqual(
            self.product_admin.list_display,
            (
                "descript",
                "sku",
                "barcode",
                "total_quantity",
                "available_quantity",
                "reserved_quantity",
                "issued_quantity",
                "sold_quantity",
                "repair_quantity",
                "reorder_stock_level",
                "stock_alert",
                "category",
                "brand",
                "model",
                "isactive",
                "crdate",
            ),
        )
        self.assertEqual(
            self.product_admin.search_fields,
            ("descript", "sku", "barcode"),
        )
        self.assertEqual(
            self.product_admin.list_filter,
            ("category", "model__brand", "isactive"),
        )
        self.assertEqual(self.product_admin.readonly_fields, ("sku", "crdate"))
        self.assertEqual(self.product_admin.ordering, ("descript", "sku"))
        self.assertEqual(
            self.product_admin.list_select_related,
            ("category", "model__brand"),
        )


class UIRegistryTests(SimpleTestCase):
    def test_core_ui_tokens_define_names_icons_and_tones(self):
        for key in (
            "inventory",
            "operations",
            "total_products",
            "available_stock",
            "out_of_stock",
            "low_stock",
            "add_stock_unit",
            "receive_stock",
            "create_delivery",
            "create_reservation",
            "create_repair",
            "create_client_return",
        ):
            token = UI_TOKENS[key]

            self.assertTrue(token.get("icon"))
            self.assertTrue(token.get("tone"))
            self.assertTrue(token.get("name") or token.get("label"))

    def test_ui_item_allows_local_overrides(self):
        item = ui_item("inventory", enabled=True)

        self.assertEqual(item["name"], "BIM Stock")
        self.assertEqual(item["icon"], "database")
        self.assertEqual(item["tone"], "blue")
        self.assertTrue(item["enabled"])

    def test_delivery_ui_tokens_use_same_icon_and_tone(self):
        delivery_records = UI_TOKENS["delivery_records"]
        create_delivery = UI_TOKENS["create_delivery"]
        reservation_records = UI_TOKENS["reservation_records"]
        create_reservation = UI_TOKENS["create_reservation"]
        repair_records = UI_TOKENS["repair_records"]
        create_repair = UI_TOKENS["create_repair"]
        client_return_records = UI_TOKENS["client_return_records"]
        create_client_return = UI_TOKENS["create_client_return"]

        self.assertEqual(create_delivery["icon"], delivery_records["icon"])
        self.assertEqual(create_delivery["tone"], delivery_records["tone"])
        self.assertEqual(create_delivery["icon"], "delivery")
        self.assertEqual(create_delivery["tone"], "indigo")
        self.assertEqual(create_reservation["icon"], reservation_records["icon"])
        self.assertEqual(create_reservation["tone"], reservation_records["tone"])
        self.assertEqual(create_reservation["icon"], "clock-3")
        self.assertEqual(create_reservation["tone"], "warning")
        self.assertEqual(create_repair["icon"], repair_records["icon"])
        self.assertEqual(create_repair["tone"], repair_records["tone"])
        self.assertEqual(create_repair["icon"], "wrench")
        self.assertEqual(create_repair["tone"], "danger")
        self.assertEqual(create_client_return["icon"], client_return_records["icon"])
        self.assertEqual(create_client_return["tone"], client_return_records["tone"])
        self.assertEqual(create_client_return["icon"], "reset")
        self.assertEqual(create_client_return["tone"], "green")

    def test_frontend_uses_registry_for_workflow_icons(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        self.assertNotIn("<Download", app_source)
        self.assertNotIn("<Truck", app_source)
        self.assertIn("workflowMeta", REACT_REGISTRY_SOURCE.read_text(encoding="utf-8"))

    def test_frontend_greeting_uses_browser_hour(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("function greetingPeriodForHour(hour)", app_source)
        self.assertIn("new Date().getHours()", app_source)
        self.assertIn("data.hero.greetingName", app_source)

    def test_command_center_layout_removes_duplicate_panels_and_keeps_refresh(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        command_center_source = app_source[
            app_source.index("function CommandCenter"):
            app_source.index("function SettingsPage")
        ]

        self.assertNotIn("<QuickActions", command_center_source)
        self.assertNotIn("<LowStockPanel", command_center_source)
        self.assertIn("onRefresh", command_center_source)
        self.assertIn("Refresh", app_source)

    def test_topbar_omits_redundant_user_avatar_and_keeps_actions(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        topbar_source = app_source[
            app_source.index("function Topbar"):
            app_source.index("function ThemeToggle")
        ]

        self.assertIn("<ThemeToggle", topbar_source)
        self.assertIn("<QuickAddMenu", topbar_source)
        self.assertIn("<LogoutForm", topbar_source)
        self.assertNotIn("data.user?.initials", topbar_source)
        self.assertNotIn("aria-label={`Signed in as", topbar_source)
        self.assertNotIn("max-w-36 truncate", topbar_source)
        self.assertNotIn("data.user?.displayName || data.user?.username", topbar_source)

    def test_product_details_page_renders_stock_units_and_permission_aware_actions(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        product_details_source = app_source[
            app_source.index("function ProductDetailsPage"):
            app_source.index("function ProductDetailMetric")
        ]

        self.assertIn("function ProductUnitRegister", app_source)
        self.assertIn("<ProductUnitRegister", product_details_source)
        self.assertIn("units={units}", product_details_source)
        self.assertIn("movements={movements}", product_details_source)
        self.assertIn("data.api.productMovements", product_details_source)
        self.assertIn('["Movements", movements.length]', product_details_source)
        self.assertIn("canAccessAdmin={data.user?.canAccessAdmin}", product_details_source)
        self.assertIn("data.quickActions.find", product_details_source)
        self.assertIn("Movement History", product_details_source)
        self.assertNotIn("activityTitle(unit)", product_details_source)
        self.assertNotIn('className="text-sm text-zinc-500"', product_details_source)
        self.assertNotIn("Supplier Code", product_details_source)
        self.assertNotIn('href="/inventory/receiving/new/"', product_details_source)
        self.assertNotIn('href="/inventory/deliveries/new/"', product_details_source)
        self.assertIn("/admin/bim_stock/productunit/${unit.id}/change/", app_source)

    def test_inventory_product_rows_select_inline_detail_without_navigation(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        inventory_table_source = app_source[
            app_source.index("function InventoryTable"):
            app_source.index("function TableMessage")
        ]
        inline_detail_source = app_source[
            app_source.index("function ProductDetail"):
            app_source.index("function ProductDetailsPage")
        ]

        self.assertIn("onSelect(product.id)", inventory_table_source)
        self.assertNotIn("window.location.assign", inventory_table_source)
        self.assertIn('href={`/inventory/products/${product.id}/`}', inline_detail_source)
        self.assertIn("/admin/bim_stock/productunit/?q=${encodeURIComponent(product.sku)}", inline_detail_source)
        self.assertIn("{canAccessAdmin ? (", inline_detail_source)
        self.assertIn("Panel close coming later", inline_detail_source)
        self.assertIn("Full View", inline_detail_source)

    def test_inventory_page_reuses_command_center_kpi_cards(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        inventory_page_source = app_source[
            app_source.index("function InventoryPage"):
            app_source.index("function InventoryHeader")
        ]

        self.assertIn("const inventoryKpis = [", inventory_page_source)
        self.assertIn("<KpiGrid items={inventoryKpis}", inventory_page_source)
        self.assertNotIn("<InventoryMetric", inventory_page_source)
        self.assertNotIn("function InventoryMetric", app_source)

    def test_visible_future_actions_are_disabled_or_marked_coming_later(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        header_source = app_source[
            app_source.index("function Header"):
            app_source.index("function InventoryPage")
        ]
        inventory_header_source = app_source[
            app_source.index("function InventoryHeader"):
            app_source.index("function ProductDetail")
        ]
        stock_entry_source = app_source[
            app_source.index("function StockEntryPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn("Global search coming later", header_source)
        self.assertIn("disabled", header_source)
        self.assertIn("Export coming later", inventory_header_source)
        self.assertIn("disabled", inventory_header_source)
        self.assertIn("Barcode scanning coming later", stock_entry_source)

    def test_add_product_page_can_create_catalogue_lookups_inline(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        add_product_source = app_source[
            app_source.index("function AddProductPage"):
            app_source.index("function StockEntryPage")
        ]

        self.assertIn("function SearchableCreatableSelect", app_source)
        self.assertNotIn("function LookupCreateControl", app_source)
        self.assertIn('createLookupOption("category"', add_product_source)
        self.assertIn('createLookupOption("brand"', add_product_source)
        self.assertNotIn('createLookupOption("supplier"', add_product_source)
        self.assertNotIn("defaultSupplier", add_product_source)
        self.assertNotIn("Client records are not implemented yet.", add_product_source)
        self.assertNotIn('createLookup("type"', add_product_source)
        self.assertNotIn("data.api.types", add_product_source)
        self.assertIn("reorderStockLevel", add_product_source)
        self.assertIn('payload.append("reorder_stock_level", form.reorderStockLevel)', add_product_source)
        self.assertNotIn('payload.append("printed"', add_product_source)
        self.assertNotIn("minimum_stock_level", add_product_source)

    def test_add_product_header_does_not_show_breadcrumb_trail(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        header_source = app_source[
            app_source.index("function AddProductHeader"):
            app_source.index("function FormSection")
        ]

        self.assertIn("Add Product", header_source)
        self.assertNotIn("BIM Nexus", header_source)
        self.assertNotIn("BIM Stock", header_source)
        self.assertNotIn(">05<", header_source)
        self.assertNotIn('className="font-mono text-white">05', header_source)

    def test_add_product_page_supports_click_drop_and_upload_for_product_images(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        add_product_source = app_source[
            app_source.index("function AddProductPage"):
            app_source.index("function StockEntryPage")
        ]
        save_product_start = add_product_source.index("async function saveProduct")
        save_product_source = add_product_source[
            save_product_start:
            add_product_source.index("  return (", save_product_start)
        ]

        self.assertIn("const imageInputRef = useRef(null)", add_product_source)
        self.assertIn("const cameraInputRef = useRef(null)", add_product_source)
        self.assertIn('type="file"', add_product_source)
        self.assertIn('accept="image/png,image/jpeg"', add_product_source)
        self.assertIn('accept="image/*"', add_product_source)
        self.assertIn('capture="environment"', add_product_source)
        self.assertIn("onClick={() => imageInputRef.current?.click()}", add_product_source)
        self.assertIn("onClick={() => cameraInputRef.current?.click()}", add_product_source)
        self.assertIn("Take Photo", add_product_source)
        self.assertIn("onDrop={handleImageDrop}", add_product_source)
        self.assertIn("const payload = new FormData()", save_product_source)
        self.assertIn('payload.append("image", form.imageFile)', save_product_source)
        self.assertNotIn('"Content-Type": "application/json"', save_product_source)

    def test_receive_stock_page_can_search_and_create_suppliers(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        stock_entry_source = app_source[
            app_source.index("function StockEntryPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn("function SearchableCreatableSelect", app_source)
        self.assertIn("async function createSupplierOption", stock_entry_source)
        self.assertIn('fetch(data.api.suppliers', stock_entry_source)
        self.assertIn('body: JSON.stringify({ name: trimmedName })', stock_entry_source)
        self.assertIn('label="Supplier"', stock_entry_source)
        self.assertIn('placeholder="Search or create supplier..."', stock_entry_source)
        self.assertIn("onCreate={createSupplierOption}", stock_entry_source)
        self.assertNotIn("options={suppliers.map((item) => [item.id, item.name])}", stock_entry_source)

    def test_receive_stock_date_defaults_to_today_and_uses_calendar_input(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        stock_entry_source = app_source[
            app_source.index("function StockEntryPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn('new Date().toISOString().slice(0, 10)', stock_entry_source)
        self.assertIn("entryDate: today", stock_entry_source)
        self.assertIn('label={isReceiving ? "Receiving Date" : "Entry Date"}', stock_entry_source)
        self.assertIn('<TextInput type="date" value={form.entryDate}', stock_entry_source)

    def test_receive_stock_received_by_uses_logged_in_user_without_selector(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        stock_entry_source = app_source[
            app_source.index("function StockEntryPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn('const handledByName = data.user?.displayName || data.user?.username || "-"', stock_entry_source)
        self.assertIn('value={handledByName}', stock_entry_source)
        self.assertNotIn("activeUsers", stock_entry_source)
        self.assertNotIn("data.api.activeUsers", stock_entry_source)
        self.assertNotIn("form.handledBy", stock_entry_source)
        self.assertNotIn('<Field label={isReceiving ? "Received By" : "Added By"}>', stock_entry_source)
        self.assertNotIn('placeholder="Select active user"', stock_entry_source)

    def test_receive_stock_submits_one_receiving_record_and_preserves_add_unit_api(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        stock_entry_source = app_source[
            app_source.index("function StockEntryPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn("async function createReceivingRecord()", stock_entry_source)
        self.assertIn("async function createProductUnits()", stock_entry_source)
        self.assertIn("fetch(data.api.receivingRecords", stock_entry_source)
        self.assertIn("fetch(data.api.productUnits", stock_entry_source)
        self.assertIn("item_inputs: itemInputs", stock_entry_source)
        self.assertIn("serial_numbers: buildReceivingSerialNumbers(line, lineIndex)", stock_entry_source)
        self.assertIn("reference_number: form.referenceNumber || form.deliveryNote", stock_entry_source)
        self.assertIn('label="Reference Number"', stock_entry_source)
        self.assertNotIn("`Reference number: ${form.referenceNumber}`", stock_entry_source)
        self.assertIn("if (isReceiving) {", stock_entry_source)
        self.assertIn("await createReceivingRecord();", stock_entry_source)
        self.assertIn("await createProductUnits();", stock_entry_source)
        self.assertIn(
            "window.location.assign(created.id ? `/operations/receiving/${created.id}/` : data.routes.receivingRecords)",
            stock_entry_source,
        )
        self.assertNotIn("Invoice Reference", stock_entry_source)
        self.assertNotIn("invoiceReference", stock_entry_source)

    def test_receiving_records_route_uses_real_api_screen(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        receiving_source = app_source[
            app_source.index("function ReceivingRecordsPage"):
            app_source.index("function ReceivingRecordDetailPage")
        ]

        self.assertIn("data.api.receivingRecords", receiving_source)
        self.assertIn("fetch(endpoint", receiving_source)
        self.assertIn("Receiving Records", receiving_source)
        self.assertIn("record.total_quantity", receiving_source)
        self.assertIn("supplier_name", receiving_source)
        self.assertIn("reference_number", receiving_source)
        self.assertIn("<EmptyState", receiving_source)
        self.assertIn("<ReceivingRecordsPage data={data}", app_source)
        self.assertNotIn('<PlaceholderPage data={data} title="Receiving Records"', app_source)

    def test_receiving_record_detail_route_uses_real_api_screen(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        detail_source = app_source[
            app_source.index("function ReceivingRecordDetailPage"):
            app_source.index("function Header")
        ]

        self.assertIn("data.api.receivingRecordDetail", detail_source)
        self.assertIn("receivingId", detail_source)
        self.assertIn("Back to Receiving Records", detail_source)
        self.assertIn("record.items", detail_source)
        self.assertIn("Reference cost only", detail_source)
        self.assertIn("<ReceivingRecordDetailPage data={data}", app_source)
        self.assertNotIn('<PlaceholderPage data={data} title="Receiving Record"', app_source)

    def test_delivery_records_route_uses_real_api_screen(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        delivery_source = app_source[
            app_source.index("function DeliveryRecordsPage"):
            app_source.index("function DeliveryRecordDetailPage")
        ]

        self.assertIn("data.api.deliveries", delivery_source)
        self.assertIn("fetch(endpoint", delivery_source)
        self.assertIn("Delivery Records", delivery_source)
        self.assertIn("record.total_units", delivery_source)
        self.assertIn("customer_name", delivery_source)
        self.assertIn("receiver_name", delivery_source)
        self.assertIn("<EmptyState", delivery_source)
        self.assertIn("<DeliveryRecordsPage data={data}", app_source)
        self.assertNotIn('<PlaceholderPage data={data} title="Delivery Records"', app_source)

    def test_delivery_record_detail_route_uses_real_api_screen(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        detail_source = app_source[
            app_source.index("function DeliveryRecordDetailPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn("data.api.deliveryDetail", detail_source)
        self.assertIn("deliveryId", detail_source)
        self.assertIn("Back to Delivery Records", detail_source)
        self.assertIn("record.items", detail_source)
        self.assertIn("Delivered Items", detail_source)
        self.assertIn("<DeliveryRecordDetailPage data={data}", app_source)
        self.assertNotIn('<PlaceholderPage data={data} title="Delivery Record"', app_source)

    def test_delivery_record_detail_has_office_safe_correction_actions(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        detail_source = app_source[
            app_source.index("function DeliveryRecordDetailPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertIn("Edit Details", detail_source)
        self.assertIn("Cancel Record", detail_source)
        self.assertIn("customer_name", detail_source)
        self.assertIn("receiver_name", detail_source)
        self.assertIn("delivery_date", detail_source)
        self.assertIn("cancel_reason", detail_source)
        self.assertIn("Wrong unit, product, or serial entries should be cancelled and recreated when safe.", detail_source)

    def test_client_return_action_is_only_on_delivery_detail(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        receiving_detail_source = app_source[
            app_source.index("function ReceivingRecordDetailPage"):
            app_source.index("function ReceivingCorrectionPanel")
        ]
        delivery_detail_source = app_source[
            app_source.index("function DeliveryRecordDetailPage"):
            app_source.index("function CreateDeliveryPage")
        ]

        self.assertNotIn("Create Client Return", receiving_detail_source)
        self.assertNotIn("client-returns/new", receiving_detail_source)
        self.assertIn("Create Client Return", delivery_detail_source)
        self.assertIn("client-returns/new", delivery_detail_source)

    def test_create_delivery_redirects_to_delivery_detail(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        delivery_source = app_source[
            app_source.index("function CreateDeliveryPage"):
            app_source.index("function AddProductHeader")
        ]

        self.assertIn(
            "window.location.assign(created.id ? `/operations/deliveries/${created.id}/` : data.routes.deliveryRecords)",
            delivery_source,
        )
        self.assertNotIn("window.location.assign(data.routes.inventory)", delivery_source)

    def test_operations_record_routes_separate_list_and_detail_matches(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        routes_source = app_source[app_source.index("const appRoutes = ["):]

        self.assertIn('match: (path) => path === "/operations/receiving/"', routes_source)
        self.assertIn('match: (path) => path.startsWith("/operations/receiving/new")', routes_source)
        self.assertIn('match: (path) => /^\\/operations\\/receiving\\/\\d+\\//.test(path)', routes_source)
        self.assertIn('<StockEntryPage data={data} mode="receive" />', routes_source)
        self.assertIn("<ReceivingRecordDetailPage data={data}", routes_source)
        self.assertIn('match: (path) => path === "/operations/deliveries/"', routes_source)
        self.assertIn('match: (path) => path.startsWith("/operations/deliveries/new")', routes_source)
        self.assertIn('match: (path) => /^\\/operations\\/deliveries\\/\\d+\\//.test(path)', routes_source)
        self.assertIn("<CreateDeliveryPage data={data}", routes_source)
        self.assertIn("<DeliveryRecordsPage data={data}", routes_source)
        self.assertIn("<DeliveryRecordDetailPage data={data}", routes_source)
        self.assertIn('match: (path) => path === "/operations/reservations/"', routes_source)
        self.assertIn('match: (path) => path.startsWith("/operations/reservations/new")', routes_source)
        self.assertIn('match: (path) => /^\\/operations\\/reservations\\/\\d+\\//.test(path)', routes_source)
        self.assertIn("<CreateReservationPage data={data}", routes_source)
        self.assertIn("<ReservationRecordsPage data={data}", routes_source)
        self.assertIn("<ReservationRecordDetailPage data={data}", routes_source)
        self.assertIn('match: (path) => path === "/operations/issues/"', routes_source)
        self.assertIn('match: (path) => path.startsWith("/operations/issues/new")', routes_source)
        self.assertIn('match: (path) => /^\\/operations\\/issues\\/\\d+\\//.test(path)', routes_source)
        self.assertIn("<CreateIssuePage data={data}", routes_source)
        self.assertIn("<IssueRecordsPage data={data}", routes_source)
        self.assertIn("<IssueRecordDetailPage data={data}", routes_source)
        self.assertIn('match: (path) => path === "/operations/repairs/"', routes_source)
        self.assertIn('match: (path) => path.startsWith("/operations/repairs/new")', routes_source)
        self.assertIn('match: (path) => /^\\/operations\\/repairs\\/\\d+\\//.test(path)', routes_source)
        self.assertIn("<CreateRepairPage data={data}", routes_source)
        self.assertIn("<RepairRecordsPage data={data}", routes_source)
        self.assertIn("<RepairRecordDetailPage data={data}", routes_source)
        self.assertIn('match: (path) => path === "/operations/client-returns/"', routes_source)
        self.assertIn('match: (path) => path.startsWith("/operations/client-returns/new")', routes_source)
        self.assertIn('match: (path) => /^\\/operations\\/client-returns\\/\\d+\\//.test(path)', routes_source)
        self.assertIn("<CreateClientReturnPage data={data}", routes_source)
        self.assertIn("<ClientReturnRecordsPage data={data}", routes_source)
        self.assertIn("<ClientReturnRecordDetailPage data={data}", routes_source)
        self.assertNotIn('path.startsWith("/inventory/receiving/new")', routes_source)
        self.assertNotIn('path.startsWith("/inventory/deliveries/new")', routes_source)
        self.assertNotIn('path.startsWith("/operations/receiving")', routes_source)
        self.assertNotIn('path.startsWith("/operations/deliveries")', routes_source)

    def test_frontend_has_reservation_list_detail_and_create_screens(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("function ReservationRecordsPage", app_source)
        self.assertIn("function ReservationRecordDetailPage", app_source)
        self.assertIn("function CreateReservationPage", app_source)
        self.assertIn("data.api.reservations", app_source)
        self.assertIn("data.api.reservationDetail", app_source)
        self.assertIn("Release Reservation", app_source)
        self.assertIn("Reserved stock must be released before delivery.", app_source)

    def test_frontend_has_issue_list_detail_and_create_screens(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("function IssueRecordsPage", app_source)
        self.assertIn("function IssueRecordDetailPage", app_source)
        self.assertIn("function CreateIssuePage", app_source)
        self.assertIn("data.api.issues", app_source)
        self.assertIn("data.api.issueDetail", app_source)
        self.assertIn("Return Issue", app_source)
        self.assertIn("Issued units must be returned before delivery.", app_source)

    def test_frontend_has_repair_list_detail_and_create_screens(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("function RepairRecordsPage", app_source)
        self.assertIn("function RepairRecordDetailPage", app_source)
        self.assertIn("function CreateRepairPage", app_source)
        self.assertIn("data.api.repairs", app_source)
        self.assertIn("data.api.repairDetail", app_source)
        self.assertIn("Resolve Repair", app_source)
        self.assertIn("Reserved, issued, and sold units must use their own workflows before repair.", app_source)

    def test_frontend_has_client_return_list_detail_and_create_screens(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("function ClientReturnRecordsPage", app_source)
        self.assertIn("function ClientReturnRecordDetailPage", app_source)
        self.assertIn("function CreateClientReturnPage", app_source)
        self.assertIn("data.api.clientReturns", app_source)
        self.assertIn("data.api.clientReturnDetail", app_source)
        self.assertIn("Return to available", app_source)
        self.assertIn("Send to repair", app_source)
        self.assertIn("not a delivery cancellation", app_source)
        self.assertIn("not a financial refund or credit", app_source)

    def test_frontend_inventory_status_vocabulary_matches_product_unit_statuses(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        status_source = REACT_STATUS_STYLES_SOURCE.read_text(encoding="utf-8")

        for status in ("available", "reserved", "issued", "sold", "repair", "inactive"):
            self.assertIn(f'["{status}",', app_source)
            self.assertIn(f"{status}:", status_source)

        self.assertNotIn('["returned",', app_source)
        self.assertNotIn("returned:", status_source)
        self.assertNotIn("damaged:", status_source)

    def test_legacy_stock_template_routes_are_not_exposed(self):
        app_source = REACT_APP_SOURCE.read_text(encoding="utf-8")
        react_shell_source = REACT_SHELL_TEMPLATE.read_text(encoding="utf-8")

        response = self.client.get("/stock/")

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("/stock/", app_source)
        self.assertNotIn("bim_stock:", react_shell_source)


# Tests the available stock count shown in Product admin.
class ProductAdminStockCountTests(TestCase):
    def setUp(self):
        self.product_admin = ProductAdmin(Product, admin.site)
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )

    def test_product_stock_counts_use_only_active_units(self):
        ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-1",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-2",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="INACTIVE",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=False,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="SOLD",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="RESERVED",
            status=ProductUnit.STATUS_RESERVED,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="ISSUED",
            status=ProductUnit.STATUS_ISSUED,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="REPAIR",
            status=ProductUnit.STATUS_REPAIR,
            isactive=True,
        )

        self.assertEqual(self.product.total_units, 6)
        self.assertEqual(self.product.available_units, 2)
        self.assertEqual(self.product.reserved_units, 1)
        self.assertEqual(self.product.issued_units, 1)
        self.assertEqual(self.product.sold_units, 1)
        self.assertEqual(self.product.repair_units, 1)
        self.assertEqual(self.product_admin.total_quantity(self.product), 6)
        self.assertEqual(self.product_admin.available_quantity(self.product), 2)

    def test_product_stock_alert_uses_product_thresholds(self):
        self.product.reorder_stock_level = 3
        self.product.save()
        ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-THRESHOLD",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )

        self.assertTrue(self.product.is_low_stock)
        self.assertEqual(self.product.stock_alert_tone, "warning")
        self.assertEqual(self.product_admin.stock_alert(self.product), "Low")

    def test_sold_units_do_not_count_as_available_after_admin_action(self):
        product_unit_admin = ProductUnitAdmin(ProductUnit, admin.site)
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="SELL-ME",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )

        product_unit_admin.mark_as_sold(
            request=None,
            queryset=ProductUnit.objects.filter(pk=unit.pk),
        )
        unit.refresh_from_db()

        self.assertEqual(unit.status, ProductUnit.STATUS_SOLD)
        self.assertEqual(unit.sold_date, timezone.localdate())
        self.assertEqual(self.product_admin.available_quantity(self.product), 0)


# Tests for ProductUnit admin list/search/filter/form layout configuration.
class ProductUnitAdminTests(SimpleTestCase):
    def setUp(self):
        self.product_unit_admin = ProductUnitAdmin(ProductUnit, admin.site)

    def test_product_unit_admin_has_staff_friendly_listing_tools(self):
        self.assertEqual(
            self.product_unit_admin.list_display,
            (
                "product",
                "serial_number",
                "status",
                "supplier",
                "cost",
                "selling_price",
                "purchase_date",
                "sold_date",
                "isactive",
            ),
        )
        self.assertEqual(
            self.product_unit_admin.search_fields,
            (
                "serial_number",
                "product__descript",
                "product__sku",
                "product__barcode",
            ),
        )
        self.assertEqual(
            self.product_unit_admin.list_filter,
            (
                "status",
                "product__category",
                "product__model__brand",
                "supplier",
                "isactive",
                "purchase_date",
                "sold_date",
            ),
        )
        self.assertEqual(self.product_unit_admin.readonly_fields, ("crdate",))
        self.assertEqual(self.product_unit_admin.actions, ("mark_as_sold",))
        self.assertEqual(
            self.product_unit_admin.list_select_related,
            ("product", "product__category", "product__model__brand", "supplier"),
        )
        self.assertEqual(
            self.product_unit_admin.autocomplete_fields,
            ("product", "supplier"),
        )
        self.assertEqual(
            self.product_unit_admin.fieldsets,
            (
                (
                    "Stock item",
                    {
                        "fields": (
                            "product",
                            "serial_number",
                            "status",
                            "isactive",
                        )
                    },
                ),
                (
                    "Purchase",
                    {
                        "fields": (
                            "supplier",
                            "cost",
                            "purchase_date",
                        )
                    },
                ),
                (
                    "Sale",
                    {
                        "fields": (
                            "selling_price",
                            "sold_date",
                        )
                    },
                ),
                (
                    "Notes",
                    {
                        "fields": (
                            "notes",
                            "crdate",
                        )
                    },
                ),
            ),
        )


class ReceivingAdminTests(SimpleTestCase):
    def test_receiving_admin_has_staff_friendly_configuration(self):
        from .admin import ReceivingRecordAdmin
        from .models import ReceivingRecord

        receiving_admin = ReceivingRecordAdmin(ReceivingRecord, admin.site)

        self.assertEqual(
            receiving_admin.list_display,
            (
                "receiving_number",
                "supplier",
                "received_date",
                "reference_number",
                "status",
                "total_quantity",
                "created_by",
                "isactive",
                "crdate",
            ),
        )
        self.assertEqual(
            receiving_admin.search_fields,
            (
                "receiving_number",
                "reference_number",
                "supplier__name",
                "items__product__descript",
                "items__serial_number",
                "items__product_unit__serial_number",
            ),
        )
        self.assertEqual(
            receiving_admin.list_filter,
            ("status", "supplier", "received_date", "isactive"),
        )
        self.assertEqual(
            receiving_admin.readonly_fields,
            ("receiving_number", "cancelled_at", "crdate"),
        )


# Tests purchase defaults used when adding new ProductUnit records.
class ProductUnitPurchaseFormTests(SimpleTestCase):
    def test_new_product_unit_defaults_to_available_purchase_today(self):
        form = ProductUnitPurchaseForm()

        self.assertEqual(
            form.fields["status"].initial,
            ProductUnit.STATUS_AVAILABLE,
        )
        self.assertEqual(form.fields["purchase_date"].initial, timezone.localdate())


# Tests selling workflow behavior in ProductUnit admin.
class ProductUnitSellingWorkflowTests(TestCase):
    def setUp(self):
        self.product_unit_admin = ProductUnitAdmin(ProductUnit, admin.site)
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        self.unit = ProductUnit.objects.create(
            product=product,
            serial_number="SOLD-BY-FORM",
            status=ProductUnit.STATUS_AVAILABLE,
        )

    def test_admin_save_sets_sold_date_when_unit_is_sold(self):
        self.unit.status = ProductUnit.STATUS_SOLD
        self.unit.selling_price = 250

        self.product_unit_admin.save_model(
            request=None,
            obj=self.unit,
            form=None,
            change=True,
        )
        self.unit.refresh_from_db()

        self.assertEqual(self.unit.status, ProductUnit.STATUS_SOLD)
        self.assertEqual(self.unit.selling_price, 250)
        self.assertEqual(self.unit.sold_date, timezone.localdate())


# Tests BIM Nexus auth, role preparation, and Command Center behavior.
class BIMPOSAccessTests(TestCase):
    def test_login_page_uses_bim_nexus_template(self):
        response = self.client.get("/accounts/login/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertContains(response, "BIM Nexus Login")
        self.assertContains(response, '"type": "login"')

    def test_login_accepts_internal_email_or_username(self):
        User.objects.create_user(
            username="jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password="test-pass",
        )

        email_response = self.client.post(
            "/accounts/login/",
            {
                "username": "jad.alasmar@bimpos.com",
                "password": "test-pass",
            },
        )
        self.client.logout()
        username_response = self.client.post(
            "/accounts/login/",
            {
                "username": "jad.alasmar",
                "password": "test-pass",
            },
        )

        self.assertEqual(email_response.status_code, 302)
        self.assertEqual(email_response.url, "/")
        self.assertEqual(username_response.status_code, 302)
        self.assertEqual(username_response.url, "/")

    def test_email_login_rejects_duplicate_email(self):
        User.objects.create_user(
            username="first.user",
            email="shared@bimpos.com",
            password="test-pass",
        )
        User.objects.create_user(
            username="second.user",
            email="shared@bimpos.com",
            password="test-pass",
        )

        response = self.client.post(
            "/accounts/login/",
            {
                "username": "shared@bimpos.com",
                "password": "test-pass",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password.")

    def test_user_admin_rejects_duplicate_email_on_change(self):
        from apps.accounts.forms import BimUserChangeForm

        first_user = User.objects.create_user(
            username="first.user",
            email="shared@bimpos.com",
            password="test-pass",
        )
        second_user = User.objects.create_user(
            username="second.user",
            email="second@bimpos.com",
            password="test-pass",
        )

        form = BimUserChangeForm(
            data=_admin_user_change_data(second_user, email="SHARED@bimpos.com"),
            instance=second_user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn(first_user.email, form.errors["email"][0])

    def test_user_admin_rejects_blank_email_on_change(self):
        from apps.accounts.forms import BimUserChangeForm

        user = User.objects.create_user(
            username="jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password="test-pass",
        )

        form = BimUserChangeForm(
            data=_admin_user_change_data(user, email=""),
            instance=user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_user_admin_rejects_duplicate_email_on_add(self):
        from apps.accounts.forms import BimUserCreationForm

        existing_user = User.objects.create_user(
            username="existing.user",
            email="shared@bimpos.com",
            password="test-pass",
        )

        form = BimUserCreationForm(
            data={
                "email": "SHARED@bimpos.com",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn(existing_user.email, form.errors["email"][0])

    def test_user_admin_creation_accepts_email_only(self):
        from apps.accounts.forms import BimUserCreationForm

        form = BimUserCreationForm(data={"email": "Jad.Alasmar@bimpos.com"})

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "jad.alasmar@bimpos.com")
        self.assertTrue(user.username.startswith("pending-jad.alasmar"))
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.groups.filter(name="Viewer").exists())

    def test_new_normal_users_start_in_viewer_group(self):
        user = User.objects.create_user(username="new-user", password="test-pass")

        self.assertTrue(user.groups.filter(name="Viewer").exists())

    def test_user_admin_creation_generates_unique_pending_usernames(self):
        from apps.accounts.forms import BimUserCreationForm

        first_form = BimUserCreationForm(data={"email": "jad.alasmar@bimpos.com"})
        second_form = BimUserCreationForm(data={"email": "jad.alasmar@example.com"})

        self.assertTrue(first_form.is_valid(), first_form.errors)
        first_user = first_form.save()
        self.assertTrue(second_form.is_valid(), second_form.errors)
        second_user = second_form.save()

        self.assertNotEqual(first_user.username, second_user.username)
        self.assertTrue(second_user.username.startswith("pending-jad.alasmar"))

    def test_user_admin_allows_unchanged_email_on_change(self):
        from apps.accounts.forms import BimUserChangeForm

        user = User.objects.create_user(
            username="jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password="test-pass",
        )

        form = BimUserChangeForm(
            data=_admin_user_change_data(user),
            instance=user,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_password_setup_link_sets_username_and_first_password(self):
        user = User.objects.create_user(
            username="pending-jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        setup_url = f"/accounts/setup/{uidb64}/{token}/"

        get_response = self.client.get(setup_url)
        post_response = self.client.post(
            setup_url,
            {
                "username": "jad.alasmar",
                "first_name": "Jad",
                "last_name": "Alasmar",
                "new_password1": "StrongPass123!",
                "new_password2": "StrongPass123!",
            },
        )
        user.refresh_from_db()

        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "bim/react_app.html")
        self.assertContains(get_response, "Create your BIM Nexus account")
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, "/accounts/login/")
        self.assertEqual(user.username, "jad.alasmar")
        self.assertEqual(user.first_name, "Jad")
        self.assertEqual(user.last_name, "Alasmar")
        self.assertTrue(user.has_usable_password())
        self.assertTrue(
            self.client.login(
                username="jad.alasmar@bimpos.com",
                password="StrongPass123!",
            )
        )

    def test_password_setup_username_suggestion_is_placeholder_only(self):
        user = User.objects.create_user(
            username="pending-jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(f"/accounts/setup/{uidb64}/{token}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"usernamePlaceholder": "jad.alasmar"')
        self.assertNotContains(response, '"value": "jad.alasmar"')

    def test_password_setup_blank_username_uses_email_default(self):
        user = User.objects.create_user(
            username="pending-jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.post(
            f"/accounts/setup/{uidb64}/{token}/",
            {
                "username": "",
                "first_name": "Jad",
                "last_name": "Alasmar",
                "new_password1": "StrongPass123!",
                "new_password2": "StrongPass123!",
            },
        )
        user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/")
        self.assertEqual(user.username, "jad.alasmar")
        self.assertTrue(user.has_usable_password())

    def test_password_setup_requires_first_and_last_name(self):
        user = User.objects.create_user(
            username="pending-jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.post(
            f"/accounts/setup/{uidb64}/{token}/",
            {
                "username": "jad.alasmar",
                "first_name": "",
                "last_name": "",
                "new_password1": "StrongPass123!",
                "new_password2": "StrongPass123!",
            },
        )
        user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertEqual(user.username, "pending-jad.alasmar")
        self.assertFalse(user.has_usable_password())

    def test_password_setup_rejects_duplicate_username(self):
        User.objects.create_user(username="jad.alasmar", email="existing@bimpos.com")
        user = User.objects.create_user(
            username="pending-jad.alasmar",
            email="new.user@bimpos.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.post(
            f"/accounts/setup/{uidb64}/{token}/",
            {
                "username": "JAD.ALASMAR",
                "first_name": "New",
                "last_name": "User",
                "new_password1": "StrongPass123!",
                "new_password2": "StrongPass123!",
            },
        )
        user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username is already used")
        self.assertEqual(user.username, "pending-jad.alasmar")
        self.assertFalse(user.has_usable_password())

    def test_password_setup_rejects_invalid_token(self):
        user = User.objects.create_user(
            username="jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password=None,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(f"/accounts/setup/{uidb64}/invalid-token/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password setup link is invalid")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_setup_email_contains_secure_link(self):
        from apps.accounts.utils import send_password_setup_email

        user = User.objects.create_user(
            username="jad.alasmar",
            email="jad.alasmar@bimpos.com",
            password=None,
        )
        request = RequestFactory().get("/")

        sent = send_password_setup_email(user, request)

        self.assertTrue(sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["jad.alasmar@bimpos.com"])
        self.assertIn("/accounts/setup/", mail.outbox[0].body)

    def test_user_admin_generates_manual_setup_link_without_sending_email(self):
        from apps.accounts.admin import BimUserAdmin

        user = User.objects.create_user(
            username="pending-manual.user",
            email="manual.user@bimpos.com",
            password="OldPass123!",
        )
        request = RequestFactory().get("/admin/auth/user/")
        request.session = {}
        request._messages = FallbackStorage(request)
        user_admin = BimUserAdmin(User, admin.site)

        with patch(
            "apps.accounts.utils.send_mail",
            side_effect=AssertionError("email should not be sent"),
        ):
            user_admin.send_password_setup_links(
                request,
                User.objects.filter(pk=user.pk),
            )

        user.refresh_from_db()
        admin_messages = [str(message) for message in list(request._messages)]

        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(
            any("/accounts/setup/" in message for message in admin_messages)
        )
        self.assertTrue(
            any("Manual setup link" in message for message in admin_messages)
        )

    def test_logout_requires_post(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        self.client.force_login(user)

        get_response = self.client.get("/accounts/logout/")
        post_response = self.client.post("/accounts/logout/")

        self.assertEqual(get_response.status_code, 405)
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response.url, "/accounts/login/")

    def test_module_launcher_requires_login(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/")

    def test_app_routes_require_login(self):
        protected_routes = (
            "/",
            "/api/command-center/",
            "/operations/",
            "/operations/receiving/",
            "/operations/receiving/new/",
            "/operations/receiving/1/",
            "/operations/deliveries/",
            "/operations/deliveries/new/",
            "/operations/deliveries/1/",
            "/operations/reservations/",
            "/operations/reservations/new/",
            "/operations/reservations/1/",
            "/inventory/",
            "/inventory/products/new/",
            "/inventory/stock-units/new/",
            "/suppliers/",
            "/clients/",
            "/assets/",
            "/knowledge-base/",
        )

        for route in protected_routes:
            with self.subTest(route=route):
                response = self.client.get(route)

                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, f"/accounts/login/?next={route}")

    def test_command_center_data_api_returns_refreshable_dashboard_payload(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        supplier = Supplier.objects.create(name="Gulf Networks LLC")
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="AUTO-REFRESH-UNIT",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=supplier,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/api/command-center/")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["currentPath"], "/")
        self.assertEqual(data["api"]["commandCenter"], "/api/command-center/")
        self.assertEqual(data["pollIntervalMs"], 60000)
        self.assertEqual(data["recentReceiving"], [])
        self.assertNotIn(unit.serial_number, str(data["recentActivity"]))

    def test_command_center_shows_inventory_module_by_permission(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertContains(response, 'id="bim-nexus-root"')
        self.assertContains(response, "bim-nexus-initial-data")
        self.assertEqual(response.context["initial_data"]["user"]["username"], "viewer")
        inventory_module = next(
            module
            for module in response.context["initial_data"]["modules"]
            if module["name"] == "BIM Stock"
        )
        self.assertTrue(inventory_module["enabled"])
        self.assertEqual(inventory_module["href"], "/inventory/")

    def test_command_center_system_overview_excludes_sites_and_has_icons(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        User.objects.create_user(username="inactive", password="test-pass", is_active=False)
        self.client.force_login(user)

        response = self.client.get("/")

        overview = response.context["initial_data"]["overview"]
        overview_labels = [item["label"] for item in overview]

        self.assertEqual(
            overview_labels,
            [
                "Suppliers",
                "Receiving Records",
                "Delivery Records",
                "Clients",
                "Total Assets",
                "Knowledge Docs",
            ],
        )
        self.assertTrue(all(item.get("icon") for item in overview))
        overview_by_label = {item["label"]: item for item in overview}
        self.assertEqual(overview_by_label["Suppliers"]["href"], "/suppliers/")
        self.assertEqual(overview_by_label["Receiving Records"]["tone"], "green")
        self.assertEqual(overview_by_label["Receiving Records"]["href"], "/operations/receiving/")
        self.assertEqual(overview_by_label["Delivery Records"]["tone"], "indigo")
        self.assertEqual(overview_by_label["Delivery Records"]["href"], "/operations/deliveries/")
        self.assertEqual(overview_by_label["Clients"]["href"], "/clients/")
        self.assertTrue(overview_by_label["Clients"]["enabled"])
        self.assertFalse(overview_by_label["Total Assets"]["enabled"])
        self.assertFalse(overview_by_label["Knowledge Docs"]["enabled"])
        self.assertNotIn("Sites", overview_labels)
        self.assertNotIn("Sold Units", overview_labels)
        self.assertNotIn("Product Categories", overview_labels)

    def test_command_center_kpis_are_clickable_navigation_shortcuts(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/")
        kpis_by_label = {
            item["label"]: item
            for item in response.context["initial_data"]["kpis"]
        }

        self.assertEqual(kpis_by_label["Total Products"]["href"], "/inventory/")
        self.assertEqual(kpis_by_label["Available Stock"]["href"], "/inventory/?status=available")
        self.assertEqual(kpis_by_label["Reserved Stock"]["href"], "/inventory/?status=reserved")
        self.assertEqual(kpis_by_label["Out of Stock Products"]["href"], "/inventory/?stock=out")
        self.assertEqual(kpis_by_label["Low Stock Alerts"]["href"], "/inventory/?stock=low")

    def test_command_center_pending_modules_and_actions_are_disabled(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/")

        pending_modules = [
            module
            for module in response.context["initial_data"]["modules"]
            if module["name"] in {"Assets", "Knowledge Base", "Reports"}
        ]

        self.assertTrue(pending_modules)
        self.assertTrue(all(module["enabled"] is False for module in pending_modules))
        self.assertTrue(all(module["href"] is None for module in pending_modules))
        self.assertTrue(all(module["count"] is None for module in pending_modules))

    def test_operations_module_and_page_are_available_for_stock_workflows(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="add_productunit"),
            Permission.objects.get(codename="change_productunit"),
        )
        self.client.force_login(user)

        command_response = self.client.get("/")
        operations_module = next(
            module
            for module in command_response.context["initial_data"]["modules"]
            if module["name"] == "Operations"
        )
        operations_nav = next(
            item
            for item in command_response.context["initial_data"]["navigation"]["primary"]
            if item["name"] == "Operations"
        )
        operations_response = self.client.get("/operations/")

        self.assertTrue(operations_module["enabled"])
        self.assertEqual(operations_module["href"], "/operations/")
        self.assertEqual(operations_module["count"], 6)
        self.assertTrue(operations_nav["enabled"])
        self.assertEqual(operations_nav["href"], "/operations/")
        self.assertEqual(operations_response.status_code, 200)
        self.assertTemplateUsed(operations_response, "bim/react_app.html")
        self.assertEqual(
            operations_response.context["initial_data"]["currentPath"],
            "/operations/",
        )

    def test_command_center_initial_data_does_not_include_demo_values(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/")

        initial_data = str(response.context["initial_data"])
        for demo_value in (
            "+34 this week",
            "-12 since yesterday",
            "+4 since yesterday",
            "PO-2024",
            "DLV-2024",
            "Ahmad Al-Rashidi",
            "Sara Hassan",
            "Office A",
            "Gulf Networks",
        ):
            self.assertNotIn(demo_value, initial_data)

    def test_command_center_ignores_sold_units_without_delivery_records(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="DELIVERED-ACTIVITY",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/")
        initial_data = response.context["initial_data"]

        self.assertEqual(initial_data["recentActivity"], [])
        self.assertNotIn(unit.serial_number, str(initial_data["recentActivity"]))
        self.assertNotIn("DLV-", str(initial_data["recentActivity"]))

    def test_command_center_ignores_product_unit_only_receiving_history(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        supplier = Supplier.objects.create(name="Gulf Networks LLC")
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="RECEIVING-ACTIVITY",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=supplier,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/")
        initial_data = response.context["initial_data"]
        overview_by_label = {
            item["label"]: item for item in initial_data["overview"]
        }

        self.assertEqual(overview_by_label["Receiving Records"]["value"], "0")
        self.assertEqual(initial_data["recentReceiving"], [])
        self.assertNotIn(unit.serial_number, str(initial_data["recentActivity"]))
        self.assertNotIn("LEGACY-", str(initial_data["recentActivity"]))
        self.assertNotIn("RCV-", str(initial_data["recentActivity"]))

    def test_command_center_recent_activity_uses_receiving_records(self):
        from .services import create_receiving_record

        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        supplier = Supplier.objects.create(name="Gulf Networks LLC")
        receiving = create_receiving_record(
            supplier=supplier,
            reference_number="SUP-REF-77",
            items=[
                {
                    "product": product,
                    "quantity": 2,
                    "serial_numbers": ["REC-ACT-1", "REC-ACT-2"],
                }
            ],
        )
        self.client.force_login(user)

        response = self.client.get("/")
        activity = response.context["initial_data"]["recentActivity"][0]
        receiving_panel = response.context["initial_data"]["recentReceiving"][0]
        overview_by_label = {
            item["label"]: item for item in response.context["initial_data"]["overview"]
        }

        self.assertEqual(activity["type"], "Receiving")
        self.assertEqual(activity["reference"], receiving.receiving_number)
        self.assertEqual(activity["related"], "2 stock units")
        self.assertEqual(activity["href"], f"/operations/receiving/{receiving.pk}/")
        self.assertEqual(receiving_panel["reference"], receiving.receiving_number)
        self.assertEqual(receiving_panel["title"], "Gulf Networks LLC")
        self.assertEqual(receiving_panel["detail"], "2 stock units")
        self.assertEqual(
            receiving_panel["href"],
            f"/operations/receiving/{receiving.pk}/",
        )
        self.assertEqual(overview_by_label["Receiving Records"]["value"], "1")

    def test_manual_add_unit_is_not_counted_as_receiving_record(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        manual_unit = ProductUnit.objects.create(
            product=product,
            serial_number="MANUAL-UNIT",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=None,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/")
        initial_data = response.context["initial_data"]
        overview_by_label = {
            item["label"]: item for item in initial_data["overview"]
        }

        self.assertEqual(overview_by_label["Receiving Records"]["value"], "0")
        self.assertEqual(initial_data["recentReceiving"], [])
        self.assertNotIn(manual_unit.serial_number, str(initial_data["recentActivity"]))
        self.assertNotIn("RCV-", str(initial_data["recentActivity"]))

    def test_command_center_recent_deliveries_panel_uses_delivery_records(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="DELIVERY-PANEL",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        delivery = DeliveryRecord.objects.create(customer_name="IT Department")
        delivery.items.create(product=product, product_unit=unit)
        self.client.force_login(user)

        response = self.client.get("/")
        delivery_panel = response.context["initial_data"]["recentDeliveries"][0]

        self.assertEqual(delivery_panel["reference"], delivery.delivery_number)
        self.assertEqual(delivery_panel["title"], "IT Department")
        self.assertEqual(delivery_panel["detail"], "1 Canon laser printer")
        self.assertEqual(
            delivery_panel["href"],
            f"/operations/deliveries/{delivery.pk}/",
        )
        self.assertEqual(delivery_panel["status"], "Delivered")
        self.assertEqual(delivery_panel["status_class"], "delivered")

    def test_command_center_quick_actions_are_current_workflows_only(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="add_product"),
            Permission.objects.get(codename="add_productunit"),
            Permission.objects.get(codename="add_receivingrecord"),
            Permission.objects.get(codename="add_deliveryrecord"),
            Permission.objects.get(codename="add_reservationrecord"),
            Permission.objects.get(codename="add_issuerecord"),
            Permission.objects.get(codename="add_repairrecord"),
            Permission.objects.get(codename="add_clientreturnrecord"),
            Permission.objects.get(codename="change_productunit"),
            Permission.objects.get(codename="view_product"),
        )
        self.client.force_login(user)

        response = self.client.get("/")
        actions = response.context["initial_data"]["quickActions"]
        actions_by_label = {action["label"]: action for action in actions}

        self.assertEqual(
            set(actions_by_label),
            {
                "Add Product",
                "Create Delivery",
                "Create Reservation",
                "Create Issue",
                "Create Repair",
                "Create Client Return",
                "Receive Stock",
                "Add Unit",
                "Add Supplier",
                "Add Client",
            },
        )
        self.assertEqual(actions_by_label["Add Product"]["href"], "/inventory/products/new/")
        self.assertEqual(actions_by_label["Create Delivery"]["href"], "/operations/deliveries/new/")
        self.assertEqual(actions_by_label["Create Reservation"]["href"], "/operations/reservations/new/")
        self.assertEqual(actions_by_label["Create Issue"]["href"], "/operations/issues/new/")
        self.assertEqual(actions_by_label["Create Repair"]["href"], "/operations/repairs/new/")
        self.assertEqual(actions_by_label["Create Client Return"]["href"], "/operations/client-returns/new/")
        self.assertEqual(actions_by_label["Receive Stock"]["href"], "/operations/receiving/new/")
        self.assertEqual(actions_by_label["Add Unit"]["href"], "/inventory/stock-units/new/")
        self.assertTrue(actions_by_label["Add Product"]["enabled"])
        self.assertTrue(actions_by_label["Create Delivery"]["enabled"])
        self.assertTrue(actions_by_label["Create Reservation"]["enabled"])
        self.assertTrue(actions_by_label["Create Issue"]["enabled"])
        self.assertTrue(actions_by_label["Create Repair"]["enabled"])
        self.assertTrue(actions_by_label["Create Client Return"]["enabled"])
        self.assertTrue(actions_by_label["Receive Stock"]["enabled"])
        self.assertTrue(actions_by_label["Add Unit"]["enabled"])
        self.assertEqual(actions_by_label["Create Delivery"]["icon"], "delivery")
        self.assertEqual(actions_by_label["Create Delivery"]["tone"], "indigo")
        self.assertEqual(actions_by_label["Create Issue"]["icon"], "user-check")
        self.assertEqual(actions_by_label["Create Issue"]["tone"], "indigo")
        self.assertEqual(actions_by_label["Create Repair"]["icon"], "wrench")
        self.assertEqual(actions_by_label["Create Repair"]["tone"], "danger")
        self.assertEqual(actions_by_label["Create Client Return"]["icon"], "reset")
        self.assertEqual(actions_by_label["Create Client Return"]["tone"], "green")
        self.assertFalse(actions_by_label["Add Supplier"]["enabled"])
        self.assertIsNone(actions_by_label["Add Supplier"]["href"])
        self.assertFalse(actions_by_label["Add Client"]["enabled"])
        self.assertIsNone(actions_by_label["Add Client"]["href"])

    def test_command_center_create_delivery_requires_add_delivery_permission(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="change_productunit"))
        user.groups.clear()
        self.client.force_login(user)

        response = self.client.get("/")
        actions_by_label = {
            action["label"]: action
            for action in response.context["initial_data"]["quickActions"]
        }

        self.assertFalse(actions_by_label["Create Delivery"]["enabled"])
        self.assertIsNone(actions_by_label["Create Delivery"]["href"])

    def test_command_center_stock_alert_kpis_use_inventory_counts(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        out_product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
            reorder_stock_level=2,
        )
        low_model = ProductModel.objects.create(brand=brand, modelname="L200")
        low_product = Product.objects.create(
            descript="Canon laser printer L200",
            category=category,
            model=low_model,
            reorder_stock_level=3,
        )
        ProductUnit.objects.create(
            product=low_product,
            serial_number="LOW-STOCK-1",
            status=ProductUnit.STATUS_AVAILABLE,
        )
        ProductUnit.objects.create(
            product=low_product,
            serial_number="LOW-STOCK-2",
            status=ProductUnit.STATUS_AVAILABLE,
        )
        self.client.force_login(user)

        response = self.client.get("/")
        out_of_stock_kpi = next(
            item
            for item in response.context["initial_data"]["kpis"]
            if item["label"] == "Out of Stock Products"
        )
        low_stock_kpi = next(
            item
            for item in response.context["initial_data"]["kpis"]
            if item["label"] == "Low Stock Alerts"
        )

        self.assertEqual(out_of_stock_kpi["value"], "1")
        self.assertEqual(out_of_stock_kpi["tone"], "danger")
        self.assertEqual(out_of_stock_kpi["detail"], "1 product out of stock")
        self.assertEqual(low_stock_kpi["value"], "1")
        self.assertEqual(low_stock_kpi["tone"], "warning")
        self.assertEqual(low_stock_kpi["detail"], "1 product with low stock")
        self.assertLess(
            response.context["initial_data"]["kpis"].index(low_stock_kpi),
            response.context["initial_data"]["kpis"].index(out_of_stock_kpi),
        )
        low_stock_alert = response.context["initial_data"]["lowStockAlerts"][0]
        self.assertEqual(low_stock_alert["productName"], "Canon laser printer L200")
        self.assertEqual(low_stock_alert["category"], "Laser")
        self.assertEqual(low_stock_alert["availableQuantity"], 2)
        self.assertEqual(low_stock_alert["reorderThreshold"], 3)
        self.assertEqual(
            low_stock_alert["href"],
            f"/inventory/products/{low_product.pk}/",
        )
        self.assertEqual(low_stock_alert["status"], "Low Stock")
        self.assertEqual(low_stock_alert["status_class"], "low_stock")

    def test_command_center_quick_add_includes_disabled_supplier_action(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="add_product"),
            Permission.objects.get(codename="add_productunit"),
            Permission.objects.get(codename="add_receivingrecord"),
            Permission.objects.get(codename="add_deliveryrecord"),
            Permission.objects.get(codename="add_reservationrecord"),
            Permission.objects.get(codename="add_issuerecord"),
            Permission.objects.get(codename="add_repairrecord"),
            Permission.objects.get(codename="add_clientreturnrecord"),
            Permission.objects.get(codename="change_productunit"),
            Permission.objects.get(codename="view_product"),
        )
        self.client.force_login(user)

        response = self.client.get("/")
        actions = response.context["initial_data"]["quickActions"]
        actions_by_label = {action["label"]: action for action in actions}

        self.assertEqual(
            set(actions_by_label),
            {
                "Add Product",
                "Create Delivery",
                "Create Reservation",
                "Create Issue",
                "Create Repair",
                "Create Client Return",
                "Receive Stock",
                "Add Unit",
                "Add Supplier",
                "Add Client",
            },
        )
        self.assertFalse(actions_by_label["Add Supplier"]["enabled"])
        self.assertIsNone(actions_by_label["Add Supplier"]["href"])
        self.assertEqual(actions_by_label["Add Supplier"]["description"], "Create supplier master data")
        self.assertFalse(actions_by_label["Add Client"]["enabled"])
        self.assertIsNone(actions_by_label["Add Client"]["href"])
        self.assertEqual(actions_by_label["Add Client"]["description"], "Create client master data")

    def test_command_center_uses_final_sidebar_and_search_labels(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/")
        secondary_nav = response.context["initial_data"]["navigation"]["secondary"]

        self.assertEqual(secondary_nav, [])
        self.assertFalse(response.context["initial_data"]["user"]["canAccessAdmin"])
        self.assertEqual(
            response.context["initial_data"]["hero"]["searchPlaceholder"],
            "Search products, stock units, deliveries, suppliers, clients...",
        )
        self.assertEqual(
            response.context["initial_data"]["hero"]["greetingName"],
            "viewer",
        )
        self.assertEqual(
            response.context["initial_data"]["theme"]["storageKey"],
            "bim-nexus-theme",
        )
        self.assertEqual(response.context["initial_data"]["theme"]["default"], "dark")

    def test_command_center_shows_administration_for_admin_users(self):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@bimpos.com",
            password="test-pass",
        )
        self.client.force_login(user)

        response = self.client.get("/")
        secondary_nav = response.context["initial_data"]["navigation"]["secondary"]

        self.assertTrue(response.context["initial_data"]["user"]["canAccessAdmin"])
        self.assertEqual(len(secondary_nav), 1)
        self.assertEqual(secondary_nav[0]["name"], "Administration")
        self.assertTrue(secondary_nav[0]["enabled"])
        self.assertEqual(secondary_nav[0]["href"], "/admin/")
        self.assertEqual(secondary_nav[0]["detail"], "Django admin")

    def test_command_center_low_stock_kpi_pluralizes_product_detail(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")

        for index in range(2):
            model = ProductModel.objects.create(brand=brand, modelname=f"L{index}")
            product = Product.objects.create(
                descript=f"Canon laser printer {index}",
                category=category,
                model=model,
                reorder_stock_level=3,
            )
            ProductUnit.objects.create(
                product=product,
                serial_number=f"LOW-STOCK-PLURAL-{index}",
                status=ProductUnit.STATUS_AVAILABLE,
            )
            ProductUnit.objects.create(
                product=product,
                serial_number=f"LOW-STOCK-PLURAL-B-{index}",
                status=ProductUnit.STATUS_AVAILABLE,
            )

        self.client.force_login(user)

        response = self.client.get("/")
        low_stock_kpi = next(
            item
            for item in response.context["initial_data"]["kpis"]
            if item["label"] == "Low Stock Alerts"
        )

        self.assertEqual(low_stock_kpi["value"], "2")
        self.assertEqual(low_stock_kpi["detail"], "2 products with low stock")

    def test_inventory_react_page_uses_inventory_navigation(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/inventory/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(response.context["initial_data"]["currentPath"], "/inventory/")
        inventory_nav = next(
            item
            for item in response.context["initial_data"]["navigation"]["primary"]
            if item["name"] == "BIM Stock"
        )
        self.assertTrue(inventory_nav["active"])
        self.assertEqual(
            response.context["initial_data"]["api"]["products"],
            "/api/stock/products/",
        )

    def test_add_product_react_page_uses_add_product_route(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="add_product"),
        )
        self.client.force_login(user)

        response = self.client.get("/inventory/products/new/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/inventory/products/new/",
        )
        add_action = next(
            action
            for action in response.context["initial_data"]["quickActions"]
            if action["label"] == "Add Product"
        )
        self.assertEqual(add_action["href"], "/inventory/products/new/")

    def test_product_detail_react_page_uses_product_detail_route(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )
        self.client.force_login(user)

        response = self.client.get(f"/inventory/products/{product.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            f"/inventory/products/{product.pk}/",
        )
        self.assertEqual(
            response.context["initial_data"]["api"]["productDetail"].format(
                id=product.pk,
            ),
            f"/api/stock/products/{product.pk}/",
        )

    def test_add_stock_unit_react_page_uses_stock_unit_route(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_supplier"),
            Permission.objects.get(codename="add_receivingrecord"),
            Permission.objects.get(codename="add_productunit"),
        )
        self.client.force_login(user)

        response = self.client.get("/inventory/stock-units/new/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/inventory/stock-units/new/",
        )
        add_stock_unit_action = next(
            action
            for action in response.context["initial_data"]["quickActions"]
            if action["label"] == "Add Unit"
        )
        self.assertEqual(add_stock_unit_action["href"], "/inventory/stock-units/new/")

    def test_receive_stock_react_page_uses_receiving_route(self):
        user = User.objects.create_user(username="receiver", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_supplier"),
            Permission.objects.get(codename="add_receivingrecord"),
            Permission.objects.get(codename="add_productunit"),
        )
        self.client.force_login(user)

        response = self.client.get("/operations/receiving/new/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/operations/receiving/new/",
        )
        receive_stock_action = next(
            action
            for action in response.context["initial_data"]["quickActions"]
            if action["label"] == "Receive Stock"
        )
        self.assertEqual(receive_stock_action["href"], "/operations/receiving/new/")

        old_response = self.client.get("/inventory/receiving/new/")
        self.assertEqual(old_response.status_code, 404)

    def test_receiving_records_react_page_exposes_receiving_api(self):
        user = User.objects.create_user(username="receiver", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_receivingrecord"))
        self.client.force_login(user)

        response = self.client.get("/operations/receiving/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/operations/receiving/",
        )
        self.assertEqual(
            response.context["initial_data"]["api"]["receivingRecords"],
            "/api/stock/receiving-records/",
        )
        self.assertEqual(
            response.context["initial_data"]["api"]["receivingRecordDetail"].format(id=42),
            "/api/stock/receiving-records/42/",
        )

    def test_create_delivery_react_page_uses_delivery_route(self):
        user = User.objects.create_user(username="support", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_productunit"),
            Permission.objects.get(codename="add_deliveryrecord"),
            Permission.objects.get(codename="change_productunit"),
        )
        self.client.force_login(user)

        response = self.client.get("/operations/deliveries/new/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/operations/deliveries/new/",
        )
        delivery_action = next(
            action
            for action in response.context["initial_data"]["quickActions"]
            if action["label"] == "Create Delivery"
        )
        self.assertEqual(delivery_action["href"], "/operations/deliveries/new/")

        old_response = self.client.get("/inventory/deliveries/new/")
        self.assertEqual(old_response.status_code, 404)

    def test_delivery_records_shell_exposes_delivery_detail_api(self):
        user = User.objects.create_user(username="dispatcher", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_deliveryrecord"))
        self.client.force_login(user)

        response = self.client.get("/operations/deliveries/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["initial_data"]["api"]["deliveries"],
            "/api/stock/deliveries/",
        )
        self.assertEqual(
            response.context["initial_data"]["api"]["deliveryDetail"].format(id=42),
            "/api/stock/deliveries/42/",
        )

    def test_settings_react_page_provides_theme_settings(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        self.client.force_login(user)

        response = self.client.get("/settings/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(response.context["initial_data"]["currentPath"], "/settings/")
        self.assertEqual(response.context["initial_data"]["navigation"]["secondary"], [])
        self.assertEqual(response.context["initial_data"]["theme"]["storageKey"], "bim-nexus-theme")
        self.assertEqual(response.context["initial_data"]["theme"]["default"], "dark")

    def test_command_center_disables_inventory_without_permission(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.groups.clear()
        self.client.force_login(user)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        inventory_module = next(
            module
            for module in response.context["initial_data"]["modules"]
            if module["name"] == "BIM Stock"
        )
        self.assertFalse(inventory_module["enabled"])
        self.assertIsNone(inventory_module["href"])

    def test_bimpos_groups_are_prepared(self):
        for group_name in ("Administrator", "IT Support", "Viewer"):
            self.assertTrue(Group.objects.filter(name=group_name).exists())
        self.assertFalse(Group.objects.filter(name="Operations Manager").exists())

    def test_bimpos_groups_have_expected_permission_levels(self):
        administrator_group = Group.objects.get(name="Administrator")
        it_support_group = Group.objects.get(name="IT Support")
        viewer_group = Group.objects.get(name="Viewer")

        administrator_permissions = set(
            administrator_group.permissions.filter(content_type__app_label="bim_stock")
            .values_list("codename", flat=True)
        )
        it_support_permissions = set(
            it_support_group.permissions.filter(content_type__app_label="bim_stock")
            .values_list("codename", flat=True)
        )
        viewer_permissions = set(
            viewer_group.permissions.filter(content_type__app_label="bim_stock")
            .values_list("codename", flat=True)
        )

        self.assertTrue(administrator_permissions)
        self.assertIn("add_product", it_support_permissions)
        self.assertIn("change_product", it_support_permissions)
        self.assertIn("add_productunit", it_support_permissions)
        self.assertIn("change_productunit", it_support_permissions)
        self.assertIn("add_receivingrecord", it_support_permissions)
        self.assertIn("add_deliveryrecord", it_support_permissions)
        self.assertIn("add_reservationrecord", it_support_permissions)
        self.assertIn("add_issuerecord", it_support_permissions)
        self.assertIn("add_repairrecord", it_support_permissions)
        self.assertIn("add_clientreturnrecord", it_support_permissions)
        self.assertIn("add_supplier", it_support_permissions)
        self.assertIn("add_client", it_support_permissions)
        self.assertTrue(all(not code.startswith("delete_") for code in it_support_permissions))
        self.assertTrue(any(code.startswith("add_") for code in it_support_permissions))
        self.assertTrue(any(code.startswith("change_") for code in it_support_permissions))
        self.assertTrue(any(code.startswith("view_") for code in it_support_permissions))
        self.assertTrue(viewer_permissions)
        self.assertTrue(all(code.startswith("view_") for code in viewer_permissions))

    def test_initial_data_exposes_stock_action_permissions(self):
        user = User.objects.create_user(username="support", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="change_receivingrecord"),
            Permission.objects.get(codename="change_deliveryrecord"),
            Permission.objects.get(codename="change_productunit"),
        )
        self.client.force_login(user)

        response = self.client.get("/")

        permissions = response.context["initial_data"]["permissions"]
        self.assertTrue(permissions["canEditReceiving"])
        self.assertTrue(permissions["canCancelReceiving"])
        self.assertTrue(permissions["canEditDelivery"])
        self.assertTrue(permissions["canCancelDelivery"])
        self.assertFalse(permissions["canCreateProduct"])


# Tests ProductUnit model fields that support pricing.
class ProductUnitModelTests(SimpleTestCase):
    def test_product_unit_tracks_client_selling_price(self):
        field = ProductUnit._meta.get_field("selling_price")

        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
        self.assertEqual(field.default, 0)


# Tests status/date consistency on direct ProductUnit saves.
class ProductUnitStatusBehaviorTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            category=category,
            model=model,
        )

    def test_product_unit_status_choices_match_office_ready_set(self):
        self.assertEqual(
            [choice[0] for choice in ProductUnit.STATUS_CHOICES],
            [
                ProductUnit.STATUS_AVAILABLE,
                ProductUnit.STATUS_RESERVED,
                ProductUnit.STATUS_ISSUED,
                ProductUnit.STATUS_SOLD,
                ProductUnit.STATUS_REPAIR,
                ProductUnit.STATUS_INACTIVE,
            ],
        )

    def test_sold_status_sets_sold_date_on_save(self):
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="MODEL-SOLD",
            status=ProductUnit.STATUS_SOLD,
        )

        self.assertEqual(unit.sold_date, timezone.localdate())

    def test_available_status_clears_sold_date_on_save(self):
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="MODEL-AVAILABLE",
            status=ProductUnit.STATUS_SOLD,
            sold_date=timezone.localdate(),
        )

        unit.status = ProductUnit.STATUS_AVAILABLE
        unit.save()
        unit.refresh_from_db()

        self.assertIsNone(unit.sold_date)

    def test_inactive_status_is_available_for_api_ready_stock_state(self):
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="MODEL-INACTIVE",
            status=ProductUnit.STATUS_INACTIVE,
            sold_date=timezone.localdate(),
        )

        self.assertEqual(unit.status, ProductUnit.STATUS_INACTIVE)
        self.assertIsNone(unit.sold_date)

    def test_issued_and_repair_statuses_clear_sold_date_on_save(self):
        for status in (ProductUnit.STATUS_ISSUED, ProductUnit.STATUS_REPAIR):
            with self.subTest(status=status):
                unit = ProductUnit.objects.create(
                    product=self.product,
                    serial_number=f"MODEL-{status.upper()}",
                    status=status,
                    sold_date=timezone.localdate(),
                )

                self.assertEqual(unit.status, status)
                self.assertIsNone(unit.sold_date)


class ReceivingRecordModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Laser")
        self.brand = Brand.objects.create(brandname="Canon")
        self.model = ProductModel.objects.create(brand=self.brand, modelname="L100")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            category=self.category,
            model=self.model,
        )

    def test_receiving_record_generates_year_sequence(self):
        from .models import ReceivingRecord

        first = ReceivingRecord.objects.create()
        second = ReceivingRecord.objects.create()

        self.assertEqual(
            first.receiving_number,
            f"RCV-{timezone.localdate().year}-0001",
        )
        self.assertEqual(
            second.receiving_number,
            f"RCV-{timezone.localdate().year}-0002",
        )

    def test_receiving_item_supports_quantity_without_product_unit(self):
        from .models import ReceivingItem, ReceivingRecord

        receiving = ReceivingRecord.objects.create()
        item = ReceivingItem.objects.create(
            receiving=receiving,
            product=self.product,
            quantity=5,
            cost="12.50",
        )

        self.assertEqual(item.quantity, 5)
        self.assertIsNone(item.product_unit)
        self.assertEqual(receiving.total_quantity, 5)


class ReceivingServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Laser")
        self.brand = Brand.objects.create(brandname="Canon")
        self.model = ProductModel.objects.create(brand=self.brand, modelname="L100")
        self.supplier = Supplier.objects.create(name="Gulf Networks LLC")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            category=self.category,
            model=self.model,
        )
        self.user = User.objects.create_user(username="receiver", password="test-pass")

    def test_service_creates_manual_receiving_without_supplier_invoice(self):
        from .models import ReceivingRecord
        from .services import create_receiving_record

        receiving = create_receiving_record(
            created_by=self.user,
            received_date=timezone.localdate(),
            items=[
                {
                    "product": self.product,
                    "quantity": 3,
                    "cost": "7.25",
                    "notes": "Opening count",
                }
            ],
        )

        self.assertIsNone(receiving.supplier)
        self.assertEqual(receiving.reference_number, "")
        self.assertEqual(receiving.total_quantity, 3)
        self.assertEqual(receiving.items.get().product, self.product)
        self.assertEqual(ProductUnit.objects.filter(serial_number="").count(), 0)
        self.assertTrue(ReceivingRecord.objects.filter(pk=receiving.pk).exists())

    def test_service_creates_stock_units_for_serialized_supplier_receiving(self):
        from .services import create_receiving_record

        receiving = create_receiving_record(
            supplier=self.supplier,
            reference_number="SUP-DOC-100",
            created_by=self.user,
            received_date=timezone.localdate(),
            items=[
                {
                    "product": self.product,
                    "quantity": 2,
                    "serial_numbers": ["RCV-SN-1", "RCV-SN-2"],
                    "cost": "88.40",
                    "notes": "Supplier delivery",
                }
            ],
        )

        self.assertEqual(receiving.supplier, self.supplier)
        self.assertEqual(receiving.reference_number, "SUP-DOC-100")
        self.assertEqual(receiving.total_quantity, 2)
        self.assertEqual(receiving.items.count(), 2)
        units = ProductUnit.objects.filter(serial_number__in=["RCV-SN-1", "RCV-SN-2"])
        self.assertEqual(units.count(), 2)
        self.assertTrue(all(unit.supplier == self.supplier for unit in units))
        self.assertTrue(
            all(unit.status == ProductUnit.STATUS_AVAILABLE for unit in units)
        )
        self.assertTrue(
            all(item.product_unit_id for item in receiving.items.order_by("serial_number"))
        )
        movements = StockMovement.objects.filter(receiving_record=receiving).order_by(
            "product_unit__serial_number"
        )
        self.assertEqual(movements.count(), 2)
        self.assertEqual(
            [movement.movement_type for movement in movements],
            [StockMovement.TYPE_RECEIVED, StockMovement.TYPE_RECEIVED],
        )
        self.assertTrue(
            all(movement.to_status == ProductUnit.STATUS_AVAILABLE for movement in movements)
        )
        self.assertTrue(all(movement.performed_by == self.user for movement in movements))

    def test_service_rejects_serial_count_that_does_not_match_quantity(self):
        from django.core.exceptions import ValidationError
        from .services import create_receiving_record

        with self.assertRaises(ValidationError):
            create_receiving_record(
                items=[
                    {
                        "product": self.product,
                        "quantity": 2,
                        "serial_numbers": ["ONLY-ONE"],
                    }
                ],
            )

    def test_service_rejects_existing_serial_numbers(self):
        from django.core.exceptions import ValidationError
        from .services import create_receiving_record

        ProductUnit.objects.create(
            product=self.product,
            serial_number="EXISTING-RCV-SN",
            status=ProductUnit.STATUS_AVAILABLE,
        )

        with self.assertRaises(ValidationError):
            create_receiving_record(
                items=[
                    {
                        "product": self.product,
                        "quantity": 1,
                        "serial_numbers": ["EXISTING-RCV-SN"],
                    }
                ],
            )


class InventoryApiTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Laser")
        self.brand = Brand.objects.create(brandname="Canon")
        self.model = ProductModel.objects.create(brand=self.brand, modelname="L100")
        self.supplier = Supplier.objects.create(name="Gulf Networks LLC")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            category=self.category,
            model=self.model,
            barcode="BAR-CANON-L100",
            reorder_stock_level=2,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="API-AVAILABLE",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=self.supplier,
            cost=50,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="API-RESERVED",
            status=ProductUnit.STATUS_RESERVED,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="API-INACTIVE",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=False,
        )

    def _user_with_permissions(self, *codenames):
        user = User.objects.create_user(username="api-user", password="test-pass")
        for codename in codenames:
            user.user_permissions.add(Permission.objects.get(codename=codename))
        return user

    def _sold_unit_with_delivery(self, serial_number="API-AVAILABLE", customer_name="Retail Client"):
        unit = ProductUnit.objects.get(serial_number=serial_number)
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = timezone.localdate()
        unit.save(update_fields=("status", "sold_date"))
        delivery = DeliveryRecord.objects.create(
            customer_name=customer_name,
            receiver_name="Client Receiver",
            delivery_date=timezone.localdate(),
        )
        delivery_item = DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            product_unit=unit,
            notes="Original delivered unit",
        )
        return unit, delivery, delivery_item

    def test_inventory_api_requires_login(self):
        response = self.client.get("/api/stock/products/")

        self.assertIn(response.status_code, (401, 403))

    def test_product_api_lists_active_products_with_counts_and_filters(self):
        user = self._user_with_permissions("view_product")
        self.client.force_login(user)

        response = self.client.get(
            "/api/stock/products/",
            {"q": "CANON-L100", "category": self.category.pk, "status": "available"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        product_data = response.json()[0]
        self.assertEqual(product_data["descript"], "Canon laser printer")
        self.assertEqual(product_data["sku"], "LAS-CAN-L100")
        self.assertEqual(product_data["barcode"], "BAR-CANON-L100")
        self.assertEqual(product_data["category_name"], "Laser")
        self.assertEqual(product_data["brand_name"], "Canon")
        self.assertNotIn("default_supplier", product_data)
        self.assertNotIn("default_supplier_name", product_data)
        self.assertEqual(product_data["model_name"], "L100")
        self.assertEqual(product_data["total_units"], 2)
        self.assertEqual(product_data["available_units"], 1)
        self.assertEqual(product_data["reserved_units"], 1)
        self.assertIn("issued_units", product_data)
        self.assertIn("repair_units", product_data)
        self.assertNotIn("returned_units", product_data)
        self.assertEqual(product_data["reorder_stock_level"], 2)
        self.assertTrue(product_data["is_low_stock"])
        self.assertNotIn("is_critical_stock", product_data)
        self.assertEqual(product_data["stock_alert_tone"], "warning")

    def test_product_api_requires_product_permission(self):
        user = User.objects.create_user(username="no-perm", password="test-pass")
        user.groups.clear()
        self.client.force_login(user)

        response = self.client.get("/api/stock/products/")

        self.assertEqual(response.status_code, 403)

    def test_product_api_creates_product_with_auto_sku(self):
        user = self._user_with_permissions("view_product", "add_product")
        self.client.force_login(user)
        new_model = ProductModel.objects.create(brand=self.brand, modelname="L200")

        response = self.client.post(
            "/api/stock/products/",
            {
                "descript": "Canon laser printer L200",
                "category": self.category.pk,
                "model": new_model.pk,
                "barcode": "BAR-CANON-L200",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()["sku"], "LAS-CAN-L200")
        self.assertNotIn("default_supplier", response.json())

    def test_product_api_creates_product_with_new_model_name(self):
        user = self._user_with_permissions("view_product", "add_product")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/products/",
            {
                "descript": "Canon laser printer L300",
                "category": self.category.pk,
                "brand": self.brand.pk,
                "model_name_input": "L300",
                "barcode": "BAR-CANON-L300",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["model_name"], "L300")
        self.assertEqual(response.json()["sku"], "LAS-CAN-L300")
        self.assertTrue(
            ProductModel.objects.filter(brand=self.brand, modelname="L300").exists()
        )

    def test_product_api_creates_product_with_image_upload(self):
        user = self._user_with_permissions("view_product", "add_product")
        self.client.force_login(user)
        image_file = BytesIO()
        Image.new("RGB", (1, 1), color="white").save(image_file, format="PNG")
        image = SimpleUploadedFile(
            "printer.png",
            image_file.getvalue(),
            content_type="image/png",
        )

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                "/api/stock/products/",
                {
                    "descript": "Canon laser printer L400",
                    "category": self.category.pk,
                    "brand": self.brand.pk,
                    "model_name_input": "L400",
                    "barcode": "BAR-CANON-L400",
                    "image": image,
                },
            )

        self.assertEqual(response.status_code, 201, response.content)
        product = Product.objects.get(pk=response.json()["id"])
        self.assertTrue(product.image.name.startswith("products_images/printer"))

    def test_product_units_api_searches_serial_and_creates_unit(self):
        user = self._user_with_permissions("view_productunit", "add_productunit")
        self.client.force_login(user)

        search_response = self.client.get(
            "/api/stock/product-units/",
            {"q": "API-AVAILABLE", "status": ProductUnit.STATUS_AVAILABLE},
        )
        create_response = self.client.post(
            "/api/stock/product-units/",
            {
                "product": self.product.pk,
                "serial_number": "API-NEW",
                "status": ProductUnit.STATUS_AVAILABLE,
                "supplier": self.supplier.pk,
                "cost": "75.50",
            },
            content_type="application/json",
        )

        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(len(search_response.json()), 1)
        self.assertEqual(search_response.json()[0]["serial_number"], "API-AVAILABLE")
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.json()["product_sku"], "LAS-CAN-L100")
        movement = StockMovement.objects.get(
            product_unit__serial_number="API-NEW",
            movement_type=StockMovement.TYPE_MANUAL_ADD,
        )
        self.assertEqual(movement.to_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.performed_by, user)

    def test_product_units_api_creates_manual_unit_without_supplier(self):
        user = self._user_with_permissions("view_productunit", "add_productunit")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/product-units/",
            {
                "product": self.product.pk,
                "serial_number": "MANUAL-COUNT-1",
                "status": ProductUnit.STATUS_AVAILABLE,
                "supplier": None,
                "cost": "0.00",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertIsNone(response.json()["supplier"])
        self.assertEqual(response.json()["supplier_name"], None)

    def test_product_units_api_records_manual_update_movement_when_status_changes(self):
        user = self._user_with_permissions("view_productunit", "change_productunit")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.patch(
            f"/api/stock/product-units/{unit.pk}/",
            {"status": ProductUnit.STATUS_RESERVED},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_MANUAL_UPDATE,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_RESERVED)
        self.assertEqual(movement.performed_by, user)

    def test_product_units_api_does_not_record_manual_update_for_non_status_edit(self):
        user = self._user_with_permissions("view_productunit", "change_productunit")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.patch(
            f"/api/stock/product-units/{unit.pk}/",
            {"notes": "Updated maintenance note"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_MANUAL_UPDATE,
            ).exists()
        )

    def test_product_movements_api_returns_product_history(self):
        user = self._user_with_permissions("view_stockmovement")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        StockMovement.objects.create(
            product=unit.product,
            product_unit=unit,
            movement_type=StockMovement.TYPE_MANUAL_ADD,
            from_status="",
            to_status=ProductUnit.STATUS_AVAILABLE,
            reason="Opening unit",
            notes="Initial count",
            performed_by=user,
            reference="Manual Add Unit",
        )
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/products/{self.product.pk}/movements/")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(response.json()), 1)
        movement_data = response.json()[0]
        self.assertEqual(movement_data["movement_type"], StockMovement.TYPE_MANUAL_ADD)
        self.assertEqual(movement_data["movement_type_label"], "Manual Add")
        self.assertEqual(movement_data["product_unit"], unit.pk)
        self.assertEqual(movement_data["serial_number"], "API-AVAILABLE")
        self.assertEqual(movement_data["from_status"], "")
        self.assertEqual(movement_data["to_status"], ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement_data["performed_by_name"], user.username)
        self.assertEqual(movement_data["reference"], "Manual Add Unit")

    def test_product_movements_api_requires_view_movement_permission(self):
        user = self._user_with_permissions("view_product")
        user.groups.clear()
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/products/{self.product.pk}/movements/")

        self.assertEqual(response.status_code, 403)

    def test_reservation_api_creates_record_and_marks_units_reserved(self):
        user = self._user_with_permissions(
            "view_reservationrecord",
            "add_reservationrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/reservations/",
            {
                "reserved_for": "Front Office POS refresh",
                "reason": "Hold for installation",
                "expected_release_date": str(timezone.localdate()),
                "notes": "Install window pending",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        unit.refresh_from_db()
        reservation = ReservationRecord.objects.get(pk=response.json()["id"])
        self.assertEqual(response.json()["reservation_number"][:9], f"RSV-{timezone.localdate().year}-")
        self.assertEqual(reservation.status, ReservationRecord.STATUS_ACTIVE)
        self.assertEqual(reservation.reserved_for, "Front Office POS refresh")
        self.assertEqual(reservation.reserved_by, user)
        self.assertIsNotNone(reservation.reserved_at)
        self.assertEqual(unit.status, ProductUnit.STATUS_RESERVED)
        item = ReservationItem.objects.get(reservation=reservation, product_unit=unit)
        self.assertTrue(item.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_RESERVED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_RESERVED)
        self.assertEqual(movement.reference, reservation.reservation_number)
        self.assertEqual(movement.performed_by, user)

    def test_reservation_api_rejects_sold_reserved_and_inactive_units(self):
        user = self._user_with_permissions(
            "view_reservationrecord",
            "add_reservationrecord",
            "change_productunit",
        )
        sold_unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="RES-SOLD",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        reserved_unit = ProductUnit.objects.get(serial_number="API-RESERVED")
        inactive_unit = ProductUnit.objects.get(serial_number="API-INACTIVE")
        self.client.force_login(user)

        for unit in (sold_unit, reserved_unit, inactive_unit):
            response = self.client.post(
                "/api/stock/reservations/",
                {
                    "reserved_for": "Blocked hold",
                    "reason": "Not available",
                    "unit_ids": [unit.pk],
                },
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(ReservationRecord.objects.count(), 0)
        self.assertFalse(StockMovement.objects.filter(movement_type=StockMovement.TYPE_RESERVED).exists())

    def test_reservation_api_returns_list_and_detail(self):
        user = self._user_with_permissions("view_reservationrecord")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        reservation = ReservationRecord.objects.create(
            reserved_for="Service desk",
            reason="Spare unit hold",
            reserved_by=user,
        )
        ReservationItem.objects.create(
            reservation=reservation,
            product=self.product,
            product_unit=unit,
            notes="Keep charger attached",
        )
        self.client.force_login(user)

        list_response = self.client.get("/api/stock/reservations/", {"q": "Service"})
        detail_response = self.client.get(f"/api/stock/reservations/{reservation.pk}/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["reservation_number"], reservation.reservation_number)
        self.assertEqual(detail_response.json()["reserved_for"], "Service desk")
        self.assertEqual(detail_response.json()["reserved_by_name"], user.username)
        self.assertEqual(detail_response.json()["total_units"], 1)
        self.assertEqual(detail_response.json()["items"][0]["product_unit"], unit.pk)
        self.assertEqual(detail_response.json()["items"][0]["serial_number"], "API-AVAILABLE")
        self.assertEqual(detail_response.json()["items"][0]["notes"], "Keep charger attached")

    def test_reservation_api_releases_active_reserved_units(self):
        user = self._user_with_permissions(
            "view_reservationrecord",
            "change_reservationrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_RESERVED
        unit.save(update_fields=("status", "sold_date"))
        reservation = ReservationRecord.objects.create(
            reserved_for="Service desk",
            reason="Spare unit hold",
            reserved_by=user,
        )
        item = ReservationItem.objects.create(
            reservation=reservation,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/reservations/{reservation.pk}/release/",
            {"release_reason": "No longer needed"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        reservation.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(reservation.status, ReservationRecord.STATUS_RELEASED)
        self.assertEqual(reservation.release_reason, "No longer needed")
        self.assertEqual(reservation.released_by, user)
        self.assertIsNotNone(reservation.released_at)
        self.assertFalse(item.isactive)
        self.assertEqual(unit.status, ProductUnit.STATUS_AVAILABLE)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_RESERVATION_RELEASED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_RESERVED)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.reference, reservation.reservation_number)
        self.assertEqual(movement.reason, "No longer needed")

    def test_reservation_api_blocks_release_when_unit_was_changed(self):
        user = self._user_with_permissions(
            "view_reservationrecord",
            "change_reservationrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_SOLD
        unit.save(update_fields=("status", "sold_date"))
        reservation = ReservationRecord.objects.create(
            reserved_for="Service desk",
            reason="Spare unit hold",
            reserved_by=user,
        )
        ReservationItem.objects.create(
            reservation=reservation,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/reservations/{reservation.pk}/release/",
            {"release_reason": "Try release"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        reservation.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(reservation.status, ReservationRecord.STATUS_ACTIVE)
        self.assertEqual(unit.status, ProductUnit.STATUS_SOLD)
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_RESERVATION_RELEASED,
            ).exists()
        )

    def test_reservation_api_can_cancel_active_reservation_to_release_units(self):
        user = self._user_with_permissions(
            "view_reservationrecord",
            "change_reservationrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_RESERVED
        unit.save(update_fields=("status", "sold_date"))
        reservation = ReservationRecord.objects.create(
            reserved_for="Service desk",
            reason="Spare unit hold",
            reserved_by=user,
        )
        ReservationItem.objects.create(
            reservation=reservation,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/reservations/{reservation.pk}/cancel/",
            {"release_reason": "Wrong unit held"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        reservation.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(reservation.status, ReservationRecord.STATUS_CANCELLED)
        self.assertEqual(unit.status, ProductUnit.STATUS_AVAILABLE)
        self.assertTrue(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_RESERVATION_RELEASED,
                reason="Wrong unit held",
            ).exists()
        )

    def test_reservation_api_permissions_are_explicit(self):
        no_view_user = User.objects.create_user(username="reservation-no-view", password="test-pass")
        no_view_user.user_permissions.add(Permission.objects.get(codename="view_productunit"))
        no_view_user.groups.clear()
        self.client.force_login(no_view_user)
        self.assertEqual(self.client.get("/api/stock/reservations/").status_code, 403)

        create_user = User.objects.create_user(username="reservation-create", password="test-pass")
        create_user.user_permissions.add(Permission.objects.get(codename="view_reservationrecord"))
        create_user.user_permissions.add(Permission.objects.get(codename="add_reservationrecord"))
        create_user.groups.clear()
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(create_user)
        create_response = self.client.post(
            "/api/stock/reservations/",
            {
                "reserved_for": "Missing product-unit permission",
                "reason": "Blocked",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 403)

        release_user = User.objects.create_user(username="reservation-release", password="test-pass")
        release_user.user_permissions.add(Permission.objects.get(codename="view_reservationrecord"))
        release_user.user_permissions.add(Permission.objects.get(codename="change_reservationrecord"))
        release_user.groups.clear()
        reservation = ReservationRecord.objects.create(reserved_for="Service desk")
        self.client.force_login(release_user)
        release_response = self.client.post(
            f"/api/stock/reservations/{reservation.pk}/release/",
            {"release_reason": "Missing product-unit permission"},
            content_type="application/json",
        )
        self.assertEqual(release_response.status_code, 403)

    def test_product_movements_api_includes_reservation_movements(self):
        user = self._user_with_permissions("view_stockmovement")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        reservation = ReservationRecord.objects.create(reserved_for="Front desk")
        StockMovement.objects.create(
            product=unit.product,
            product_unit=unit,
            movement_type=StockMovement.TYPE_RESERVED,
            from_status=ProductUnit.STATUS_AVAILABLE,
            to_status=ProductUnit.STATUS_RESERVED,
            performed_by=user,
            reservation_record=reservation,
            reference=reservation.reservation_number,
        )
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/products/{self.product.pk}/movements/")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()[0]["movement_type"], StockMovement.TYPE_RESERVED)
        self.assertEqual(response.json()[0]["reservation"], reservation.pk)
        self.assertEqual(response.json()[0]["reservation_number"], reservation.reservation_number)

    def test_issue_api_creates_record_and_marks_units_issued(self):
        user = self._user_with_permissions(
            "view_issuerecord",
            "add_issuerecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/issues/",
            {
                "issued_to": "Technician Team",
                "department": "IT",
                "branch_or_site": "Main Branch",
                "reason": "Temporary setup",
                "issue_date": str(timezone.localdate()),
                "expected_return_date": str(timezone.localdate()),
                "notes": "Return after event",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        unit.refresh_from_db()
        issue = IssueRecord.objects.get(pk=response.json()["id"])
        self.assertEqual(response.json()["issue_number"][:9], f"ISS-{timezone.localdate().year}-")
        self.assertEqual(issue.status, IssueRecord.STATUS_ACTIVE)
        self.assertEqual(issue.issued_to, "Technician Team")
        self.assertEqual(issue.issued_by, user)
        self.assertEqual(unit.status, ProductUnit.STATUS_ISSUED)
        item = IssueItem.objects.get(issue=issue, product_unit=unit)
        self.assertTrue(item.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_ISSUED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_ISSUED)
        self.assertEqual(movement.reference, issue.issue_number)
        self.assertEqual(movement.issue_record, issue)
        self.assertEqual(movement.performed_by, user)

    def test_issue_api_rejects_unavailable_units(self):
        user = self._user_with_permissions(
            "view_issuerecord",
            "add_issuerecord",
            "change_productunit",
        )
        unavailable_units = [
            ProductUnit.objects.get(serial_number="API-RESERVED"),
            ProductUnit.objects.create(
                product=self.product,
                serial_number="ISS-SOLD",
                status=ProductUnit.STATUS_SOLD,
                isactive=True,
            ),
            ProductUnit.objects.create(
                product=self.product,
                serial_number="ISS-REPAIR",
                status=ProductUnit.STATUS_REPAIR,
                isactive=True,
            ),
            ProductUnit.objects.create(
                product=self.product,
                serial_number="ISS-ISSUED",
                status=ProductUnit.STATUS_ISSUED,
                isactive=True,
            ),
            ProductUnit.objects.get(serial_number="API-INACTIVE"),
        ]
        self.client.force_login(user)

        for unit in unavailable_units:
            response = self.client.post(
                "/api/stock/issues/",
                {
                    "issued_to": "Blocked issue",
                    "reason": "Not available",
                    "unit_ids": [unit.pk],
                },
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(IssueRecord.objects.count(), 0)
        self.assertFalse(StockMovement.objects.filter(movement_type=StockMovement.TYPE_ISSUED).exists())

    def test_issue_api_returns_list_and_detail(self):
        user = self._user_with_permissions("view_issuerecord")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        issue = IssueRecord.objects.create(
            issued_to="Technician Team",
            department="IT",
            branch_or_site="Main Branch",
            reason="Temporary setup",
            issued_by=user,
        )
        IssueItem.objects.create(
            issue=issue,
            product=self.product,
            product_unit=unit,
            notes="Cable attached",
        )
        self.client.force_login(user)

        list_response = self.client.get("/api/stock/issues/", {"q": "Technician"})
        detail_response = self.client.get(f"/api/stock/issues/{issue.pk}/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["issue_number"], issue.issue_number)
        self.assertEqual(detail_response.json()["issued_to"], "Technician Team")
        self.assertEqual(detail_response.json()["issued_by_name"], user.username)
        self.assertEqual(detail_response.json()["total_units"], 1)
        self.assertEqual(detail_response.json()["items"][0]["product_unit"], unit.pk)
        self.assertEqual(detail_response.json()["items"][0]["serial_number"], "API-AVAILABLE")

    def test_issue_api_returns_active_issued_units(self):
        user = self._user_with_permissions(
            "view_issuerecord",
            "change_issuerecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_ISSUED
        unit.save(update_fields=("status", "sold_date"))
        issue = IssueRecord.objects.create(
            issued_to="Technician Team",
            reason="Temporary setup",
            issued_by=user,
        )
        item = IssueItem.objects.create(
            issue=issue,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/issues/{issue.pk}/return/",
            {
                "return_reason": "Task complete",
                "returned_date": str(timezone.localdate()),
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        issue.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(issue.status, IssueRecord.STATUS_RETURNED)
        self.assertEqual(issue.return_reason, "Task complete")
        self.assertEqual(issue.returned_by, user)
        self.assertIsNotNone(issue.returned_at)
        self.assertFalse(item.isactive)
        self.assertEqual(unit.status, ProductUnit.STATUS_AVAILABLE)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_ISSUE_RETURNED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_ISSUED)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.reference, issue.issue_number)
        self.assertEqual(movement.issue_record, issue)

    def test_issue_api_blocks_return_when_unit_was_changed(self):
        user = self._user_with_permissions(
            "view_issuerecord",
            "change_issuerecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_REPAIR
        unit.save(update_fields=("status", "sold_date"))
        issue = IssueRecord.objects.create(issued_to="Technician Team")
        IssueItem.objects.create(issue=issue, product=self.product, product_unit=unit)
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/issues/{issue.pk}/return/",
            {"return_reason": "Try return"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        issue.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(issue.status, IssueRecord.STATUS_ACTIVE)
        self.assertEqual(unit.status, ProductUnit.STATUS_REPAIR)
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_ISSUE_RETURNED,
            ).exists()
        )

    def test_issue_api_blocks_return_when_issue_is_not_active(self):
        user = self._user_with_permissions(
            "view_issuerecord",
            "change_issuerecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_ISSUED
        unit.save(update_fields=("status", "sold_date"))
        issue = IssueRecord.objects.create(
            issued_to="Technician Team",
            status=IssueRecord.STATUS_RETURNED,
        )
        IssueItem.objects.create(issue=issue, product=self.product, product_unit=unit)
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/issues/{issue.pk}/return/",
            {"return_reason": "Duplicate return"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        unit.refresh_from_db()
        self.assertEqual(unit.status, ProductUnit.STATUS_ISSUED)

    def test_issue_api_permissions_are_explicit(self):
        no_view_user = User.objects.create_user(username="issue-no-view", password="test-pass")
        no_view_user.user_permissions.add(Permission.objects.get(codename="view_productunit"))
        no_view_user.groups.clear()
        self.client.force_login(no_view_user)
        self.assertEqual(self.client.get("/api/stock/issues/").status_code, 403)

        create_user = User.objects.create_user(username="issue-create", password="test-pass")
        create_user.user_permissions.add(Permission.objects.get(codename="view_issuerecord"))
        create_user.user_permissions.add(Permission.objects.get(codename="add_issuerecord"))
        create_user.groups.clear()
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(create_user)
        create_response = self.client.post(
            "/api/stock/issues/",
            {
                "issued_to": "Missing product-unit permission",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 403)

        return_user = User.objects.create_user(username="issue-return", password="test-pass")
        return_user.user_permissions.add(Permission.objects.get(codename="view_issuerecord"))
        return_user.user_permissions.add(Permission.objects.get(codename="change_issuerecord"))
        return_user.groups.clear()
        issue = IssueRecord.objects.create(issued_to="Technician Team")
        self.client.force_login(return_user)
        return_response = self.client.post(
            f"/api/stock/issues/{issue.pk}/return/",
            {"return_reason": "Missing product-unit permission"},
            content_type="application/json",
        )
        self.assertEqual(return_response.status_code, 403)

    def test_product_movements_api_includes_issue_movements(self):
        user = self._user_with_permissions("view_stockmovement")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        issue = IssueRecord.objects.create(issued_to="Technician Team")
        StockMovement.objects.create(
            product=unit.product,
            product_unit=unit,
            movement_type=StockMovement.TYPE_ISSUED,
            from_status=ProductUnit.STATUS_AVAILABLE,
            to_status=ProductUnit.STATUS_ISSUED,
            performed_by=user,
            issue_record=issue,
            reference=issue.issue_number,
        )
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/products/{self.product.pk}/movements/")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()[0]["movement_type"], StockMovement.TYPE_ISSUED)
        self.assertEqual(response.json()[0]["issue"], issue.pk)
        self.assertEqual(response.json()[0]["issue_number"], issue.issue_number)

    def test_repair_api_creates_record_and_marks_units_repair(self):
        user = self._user_with_permissions(
            "view_repairrecord",
            "add_repairrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/repairs/",
            {
                "repair_reason": "Printer head failure",
                "reported_by_name": "Front Office",
                "repair_location": "Workshop",
                "technician": "Internal IT",
                "repair_date": str(timezone.localdate()),
                "expected_resolution_date": str(timezone.localdate()),
                "notes": "Diagnose before reuse",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        unit.refresh_from_db()
        repair = RepairRecord.objects.get(pk=response.json()["id"])
        self.assertEqual(
            response.json()["repair_number"][:9],
            f"RPR-{timezone.localdate().year}-",
        )
        self.assertEqual(repair.status, RepairRecord.STATUS_ACTIVE)
        self.assertEqual(repair.repair_reason, "Printer head failure")
        self.assertEqual(repair.sent_by, user)
        self.assertEqual(unit.status, ProductUnit.STATUS_REPAIR)
        item = RepairItem.objects.get(repair=repair, product_unit=unit)
        self.assertTrue(item.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_SENT_TO_REPAIR,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_REPAIR)
        self.assertEqual(movement.reference, repair.repair_number)
        self.assertEqual(movement.repair_record, repair)
        self.assertEqual(movement.performed_by, user)

    def test_repair_api_rejects_unavailable_units(self):
        user = self._user_with_permissions(
            "view_repairrecord",
            "add_repairrecord",
            "change_productunit",
        )
        unavailable_units = [
            ProductUnit.objects.get(serial_number="API-RESERVED"),
            ProductUnit.objects.create(
                product=self.product,
                serial_number="RPR-SOLD",
                status=ProductUnit.STATUS_SOLD,
                isactive=True,
            ),
            ProductUnit.objects.create(
                product=self.product,
                serial_number="RPR-ISSUED",
                status=ProductUnit.STATUS_ISSUED,
                isactive=True,
            ),
            ProductUnit.objects.create(
                product=self.product,
                serial_number="RPR-REPAIR",
                status=ProductUnit.STATUS_REPAIR,
                isactive=True,
            ),
            ProductUnit.objects.get(serial_number="API-INACTIVE"),
        ]
        self.client.force_login(user)

        for unit in unavailable_units:
            response = self.client.post(
                "/api/stock/repairs/",
                {
                    "repair_reason": "Blocked repair",
                    "unit_ids": [unit.pk],
                },
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(RepairRecord.objects.count(), 0)
        self.assertFalse(
            StockMovement.objects.filter(
                movement_type=StockMovement.TYPE_SENT_TO_REPAIR,
            ).exists()
        )

    def test_repair_api_returns_list_and_detail(self):
        user = self._user_with_permissions("view_repairrecord")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        repair = RepairRecord.objects.create(
            repair_reason="Printer head failure",
            reported_by_name="Front Office",
            repair_location="Workshop",
            technician="Internal IT",
            sent_by=user,
        )
        RepairItem.objects.create(
            repair=repair,
            product=self.product,
            product_unit=unit,
            notes="Cable attached",
        )
        self.client.force_login(user)

        list_response = self.client.get("/api/stock/repairs/", {"q": "Printer"})
        detail_response = self.client.get(f"/api/stock/repairs/{repair.pk}/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["repair_number"], repair.repair_number)
        self.assertEqual(detail_response.json()["repair_reason"], "Printer head failure")
        self.assertEqual(detail_response.json()["sent_by_name"], user.username)
        self.assertEqual(detail_response.json()["total_units"], 1)
        self.assertEqual(detail_response.json()["items"][0]["product_unit"], unit.pk)
        self.assertEqual(detail_response.json()["items"][0]["serial_number"], "API-AVAILABLE")

    def test_repair_api_resolves_to_available(self):
        user = self._user_with_permissions(
            "view_repairrecord",
            "change_repairrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_REPAIR
        unit.save(update_fields=("status", "sold_date"))
        repair = RepairRecord.objects.create(
            repair_reason="Printer head failure",
            sent_by=user,
        )
        item = RepairItem.objects.create(
            repair=repair,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/repairs/{repair.pk}/resolve/",
            {
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "resolved_date": str(timezone.localdate()),
                "resolution_notes": "Tested OK",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        repair.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(repair.status, RepairRecord.STATUS_RESOLVED)
        self.assertEqual(repair.resolution, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(repair.resolution_notes, "Tested OK")
        self.assertEqual(repair.resolved_by, user)
        self.assertIsNotNone(repair.resolved_at)
        self.assertFalse(item.isactive)
        self.assertEqual(unit.status, ProductUnit.STATUS_AVAILABLE)
        self.assertTrue(unit.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_REPAIR_RESOLVED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_REPAIR)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.repair_record, repair)

    def test_repair_api_resolves_to_inactive(self):
        user = self._user_with_permissions(
            "view_repairrecord",
            "change_repairrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_REPAIR
        unit.save(update_fields=("status", "sold_date"))
        repair = RepairRecord.objects.create(repair_reason="Not repairable")
        RepairItem.objects.create(repair=repair, product=self.product, product_unit=unit)
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/repairs/{repair.pk}/resolve/",
            {
                "resolution": ProductUnit.STATUS_INACTIVE,
                "resolution_notes": "Scrap after testing",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        unit.refresh_from_db()
        self.assertEqual(unit.status, ProductUnit.STATUS_INACTIVE)
        self.assertFalse(unit.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_REPAIR_DEACTIVATED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_REPAIR)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_INACTIVE)

    def test_repair_api_blocks_resolve_when_unit_was_changed(self):
        user = self._user_with_permissions(
            "view_repairrecord",
            "change_repairrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_RESERVED
        unit.save(update_fields=("status", "sold_date"))
        repair = RepairRecord.objects.create(repair_reason="Printer head failure")
        RepairItem.objects.create(repair=repair, product=self.product, product_unit=unit)
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/repairs/{repair.pk}/resolve/",
            {
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "resolution_notes": "Try resolve",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        repair.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(repair.status, RepairRecord.STATUS_ACTIVE)
        self.assertEqual(unit.status, ProductUnit.STATUS_RESERVED)
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_REPAIR_RESOLVED,
            ).exists()
        )

    def test_repair_api_permissions_are_explicit(self):
        no_view_user = User.objects.create_user(username="repair-no-view", password="test-pass")
        no_view_user.user_permissions.add(Permission.objects.get(codename="view_productunit"))
        no_view_user.groups.clear()
        self.client.force_login(no_view_user)
        self.assertEqual(self.client.get("/api/stock/repairs/").status_code, 403)

        create_user = User.objects.create_user(username="repair-create", password="test-pass")
        create_user.user_permissions.add(Permission.objects.get(codename="view_repairrecord"))
        create_user.user_permissions.add(Permission.objects.get(codename="add_repairrecord"))
        create_user.groups.clear()
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(create_user)
        create_response = self.client.post(
            "/api/stock/repairs/",
            {
                "repair_reason": "Missing product-unit permission",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 403)

        resolve_user = User.objects.create_user(username="repair-resolve", password="test-pass")
        resolve_user.user_permissions.add(Permission.objects.get(codename="view_repairrecord"))
        resolve_user.user_permissions.add(Permission.objects.get(codename="change_repairrecord"))
        resolve_user.groups.clear()
        repair = RepairRecord.objects.create(repair_reason="Printer head failure")
        self.client.force_login(resolve_user)
        resolve_response = self.client.post(
            f"/api/stock/repairs/{repair.pk}/resolve/",
            {
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "resolution_notes": "Missing product-unit permission",
            },
            content_type="application/json",
        )
        self.assertEqual(resolve_response.status_code, 403)

    def test_product_movements_api_includes_repair_movements(self):
        user = self._user_with_permissions("view_stockmovement")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        repair = RepairRecord.objects.create(repair_reason="Printer head failure")
        StockMovement.objects.create(
            product=unit.product,
            product_unit=unit,
            movement_type=StockMovement.TYPE_SENT_TO_REPAIR,
            from_status=ProductUnit.STATUS_AVAILABLE,
            to_status=ProductUnit.STATUS_REPAIR,
            performed_by=user,
            repair_record=repair,
            reference=repair.repair_number,
        )
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/products/{self.product.pk}/movements/")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()[0]["movement_type"], StockMovement.TYPE_SENT_TO_REPAIR)
        self.assertEqual(response.json()[0]["repair"], repair.pk)
        self.assertEqual(response.json()[0]["repair_number"], repair.repair_number)

    def test_delivery_api_rejects_repair_units_directly(self):
        user = self._user_with_permissions(
            "add_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_REPAIR
        unit.save(update_fields=("status", "sold_date"))
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/deliveries/",
            {
                "customer_name": "Internal Department",
                "receiver_name": "Receiver Name",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        unit.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(unit.status, ProductUnit.STATUS_REPAIR)

    def test_reference_apis_return_lookup_data(self):
        user = self._user_with_permissions(
            "view_product",
            "view_productunit",
            "view_supplier",
        )
        self.client.force_login(user)

        responses = [
            self.client.get("/api/stock/categories/"),
            self.client.get("/api/stock/brands/"),
            self.client.get("/api/stock/models/"),
            self.client.get("/api/stock/suppliers/"),
        ]

        self.assertTrue(all(response.status_code == 200 for response in responses))
        self.assertIn("Laser", {item["name"] for item in responses[0].json()})
        self.assertIn("Gulf Networks LLC", {item["name"] for item in responses[3].json()})

    def test_reference_apis_create_catalogue_lookups(self):
        user = self._user_with_permissions(
            "view_product",
            "view_supplier",
            "add_category",
            "add_brand",
            "add_supplier",
        )
        self.client.force_login(user)

        category_response = self.client.post(
            "/api/stock/categories/",
            {"name": "Barcode"},
            content_type="application/json",
        )
        brand_response = self.client.post(
            "/api/stock/brands/",
            {"brandname": "Zebra"},
            content_type="application/json",
        )
        supplier_response = self.client.post(
            "/api/stock/suppliers/",
            {"name": "North Star Distribution"},
            content_type="application/json",
        )

        self.assertEqual(category_response.status_code, 201)
        self.assertEqual(category_response.json()["name"], "Barcode")
        self.assertEqual(brand_response.status_code, 201)
        self.assertEqual(brand_response.json()["brandname"], "Zebra")
        self.assertEqual(supplier_response.status_code, 201)
        self.assertEqual(supplier_response.json()["name"], "North Star Distribution")

    def test_reference_apis_search_and_prevent_duplicate_lookup_names(self):
        user = self._user_with_permissions(
            "view_product",
            "view_supplier",
            "add_category",
            "add_brand",
            "add_supplier",
        )
        self.client.force_login(user)

        search_response = self.client.get("/api/stock/suppliers/", {"q": "gulf"})
        duplicate_category = self.client.post(
            "/api/stock/categories/",
            {"name": " laser "},
            content_type="application/json",
        )
        duplicate_brand = self.client.post(
            "/api/stock/brands/",
            {"brandname": "canon"},
            content_type="application/json",
        )
        duplicate_supplier = self.client.post(
            "/api/stock/suppliers/",
            {"name": "gulf networks llc"},
            content_type="application/json",
        )

        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(
            [supplier["name"] for supplier in search_response.json()],
            ["Gulf Networks LLC"],
        )
        self.assertEqual(duplicate_category.status_code, 400)
        self.assertEqual(duplicate_brand.status_code, 400)
        self.assertEqual(duplicate_supplier.status_code, 400)

    def test_reference_api_create_requires_lookup_permission(self):
        user = self._user_with_permissions("view_product")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/brands/",
            {"brandname": "Zebra"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Brand.objects.filter(brandname="Zebra").exists())

    def test_summary_api_returns_inventory_counts(self):
        user = self._user_with_permissions("view_product")
        ProductUnit.objects.create(
            product=self.product,
            serial_number="API-ISSUED",
            status=ProductUnit.STATUS_ISSUED,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="API-REPAIR",
            status=ProductUnit.STATUS_REPAIR,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/api/stock/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_products"], 1)
        self.assertEqual(response.json()["available_units"], 1)
        self.assertEqual(response.json()["reserved_units"], 1)
        self.assertEqual(response.json()["issued_units"], 1)
        self.assertEqual(response.json()["repair_units"], 1)
        self.assertNotIn("returned_units", response.json())
        self.assertEqual(response.json()["out_of_stock_products"], 0)
        self.assertEqual(response.json()["low_stock_products"], 1)
        self.assertNotIn("critical_stock_products", response.json())

    def test_summary_api_counts_out_of_stock_separately_from_low_stock(self):
        user = self._user_with_permissions("view_product")
        self.client.force_login(user)
        model = ProductModel.objects.create(brand=self.brand, modelname="L200")
        Product.objects.create(
            descript="Canon empty printer",
            category=self.category,
            model=model,
            reorder_stock_level=3,
        )

        response = self.client.get("/api/stock/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["out_of_stock_products"], 1)
        self.assertEqual(response.json()["low_stock_products"], 1)

    def test_delivery_api_creates_record_and_marks_units_sold(self):
        user = self._user_with_permissions(
            "add_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/deliveries/",
            {
                "customer_name": "Internal Department",
                "receiver_name": "Receiver Name",
                "delivery_date": str(timezone.localdate()),
                "notes": "For staff handover",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        unit.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["delivery_number"][:9], f"DLV-{timezone.localdate().year}-")
        self.assertEqual(response.json()["customer_name"], "Internal Department")
        self.assertEqual(response.json()["total_units"], 1)
        self.assertEqual(unit.status, ProductUnit.STATUS_SOLD)
        self.assertEqual(unit.sold_date, timezone.localdate())
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_DELIVERED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_SOLD)
        self.assertEqual(movement.delivery_record.delivery_number, response.json()["delivery_number"])
        self.assertEqual(movement.performed_by, user)
        self.assertTrue(
            DeliveryRecord.objects.filter(
                delivery_number=response.json()["delivery_number"],
                items__product_unit=unit,
            ).exists()
        )

    def test_delivery_api_requires_add_delivery_permission_to_create(self):
        user = self._user_with_permissions(
            "view_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/deliveries/",
            {
                "customer_name": "Internal Department",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_delivery_api_requires_view_delivery_permission_to_list(self):
        user = self._user_with_permissions("view_productunit")
        user.groups.clear()
        self.client.force_login(user)

        response = self.client.get("/api/stock/deliveries/")

        self.assertEqual(response.status_code, 403)

    def test_delivery_api_returns_single_record_detail(self):
        user = self._user_with_permissions("view_deliveryrecord")
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = timezone.localdate()
        unit.save(update_fields=("status", "sold_date"))
        delivery = DeliveryRecord.objects.create(
            customer_name="Internal Department",
            receiver_name="Receiver Name",
            notes="For staff handover",
            created_by=user,
        )
        DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            product_unit=unit,
            notes="Delivered with charger",
        )
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/deliveries/{delivery.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], delivery.pk)
        self.assertEqual(response.json()["delivery_number"], delivery.delivery_number)
        self.assertEqual(response.json()["customer_name"], "Internal Department")
        self.assertEqual(response.json()["receiver_name"], "Receiver Name")
        self.assertEqual(response.json()["created_by_name"], user.username)
        self.assertEqual(response.json()["total_units"], 1)
        self.assertEqual(response.json()["items"][0]["product"], self.product.pk)
        self.assertEqual(response.json()["items"][0]["product_name"], "Canon laser printer")
        self.assertEqual(response.json()["items"][0]["product_sku"], "LAS-CAN-L100")
        self.assertEqual(response.json()["items"][0]["product_unit"], unit.pk)
        self.assertEqual(response.json()["items"][0]["serial_number"], "API-AVAILABLE")
        self.assertEqual(response.json()["items"][0]["product_unit_status"], ProductUnit.STATUS_SOLD)
        self.assertEqual(response.json()["items"][0]["product_unit_status_label"], "Sold")
        self.assertEqual(response.json()["items"][0]["notes"], "Delivered with charger")

    def test_delivery_api_updates_safe_header_fields_and_item_notes(self):
        user = self._user_with_permissions(
            "view_deliveryrecord",
            "change_deliveryrecord",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = timezone.localdate()
        unit.save(update_fields=("status", "sold_date"))
        delivery = DeliveryRecord.objects.create(
            customer_name="Old Customer",
            receiver_name="Old Receiver",
            notes="Old notes",
            created_by=user,
        )
        item = DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            product_unit=unit,
            notes="Old item note",
        )
        self.client.force_login(user)

        response = self.client.patch(
            f"/api/stock/deliveries/{delivery.pk}/",
            {
                "customer_name": "New Customer",
                "receiver_name": "New Receiver",
                "delivery_date": "2026-07-05",
                "notes": "Updated notes",
                "delivery_number": "DLV-1999-9999",
                "created_by": None,
                "items": [
                    {
                        "id": item.pk,
                        "product": self.product.pk + 1000,
                        "product_unit": unit.pk + 1000,
                        "notes": "Updated item note",
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        delivery.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(delivery.customer_name, "New Customer")
        self.assertEqual(delivery.receiver_name, "New Receiver")
        self.assertEqual(str(delivery.delivery_date), "2026-07-05")
        self.assertEqual(delivery.notes, "Updated notes")
        self.assertNotEqual(delivery.delivery_number, "DLV-1999-9999")
        self.assertEqual(delivery.created_by, user)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.product_unit, unit)
        self.assertEqual(item.notes, "Updated item note")
        self.assertEqual(unit.status, ProductUnit.STATUS_SOLD)
        self.assertEqual(str(unit.sold_date), "2026-07-05")

    def test_delivery_api_cancels_when_linked_units_are_untouched_sold_units(self):
        user = self._user_with_permissions(
            "view_deliveryrecord",
            "change_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = timezone.localdate()
        unit.save(update_fields=("status", "sold_date"))
        delivery = DeliveryRecord.objects.create(
            customer_name="Cancel Customer",
            created_by=user,
        )
        item = DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/deliveries/{delivery.pk}/cancel/",
            {"cancel_reason": "Wrong unit selected"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        delivery.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(delivery.status, DeliveryRecord.STATUS_CANCELLED)
        self.assertEqual(delivery.cancel_reason, "Wrong unit selected")
        self.assertEqual(delivery.cancelled_by, user)
        self.assertIsNotNone(delivery.cancelled_at)
        self.assertFalse(item.isactive)
        self.assertEqual(unit.status, ProductUnit.STATUS_AVAILABLE)
        self.assertIsNone(unit.sold_date)
        self.assertTrue(unit.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_DELIVERY_CANCELLED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_SOLD)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.reason, "Wrong unit selected")
        self.assertEqual(movement.performed_by, user)

    def test_delivery_api_blocks_cancel_when_linked_unit_is_no_longer_sold(self):
        user = self._user_with_permissions(
            "view_deliveryrecord",
            "change_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_REPAIR
        unit.save(update_fields=("status", "sold_date"))
        delivery = DeliveryRecord.objects.create(customer_name="Cancel Customer")
        DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/deliveries/{delivery.pk}/cancel/",
            {"cancel_reason": "Wrong unit selected"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        delivery.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(delivery.status, DeliveryRecord.STATUS_COMPLETED)
        self.assertEqual(unit.status, ProductUnit.STATUS_REPAIR)
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_DELIVERY_CANCELLED,
            ).exists()
        )

    def test_delivery_api_cancel_requires_product_unit_change_permission(self):
        user = self._user_with_permissions(
            "view_deliveryrecord",
            "change_deliveryrecord",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_SOLD
        unit.save(update_fields=("status", "sold_date"))
        delivery = DeliveryRecord.objects.create(customer_name="Cancel Customer")
        DeliveryItem.objects.create(
            delivery=delivery,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/deliveries/{delivery.pk}/cancel/",
            {"cancel_reason": "No product unit permission"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_delivery_api_detail_requires_view_delivery_permission(self):
        user = self._user_with_permissions("view_productunit")
        user.groups.clear()
        delivery = DeliveryRecord.objects.create(customer_name="Internal Department")
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/deliveries/{delivery.pk}/")

        self.assertEqual(response.status_code, 403)

    def test_delivery_api_rejects_unavailable_units(self):
        user = self._user_with_permissions(
            "add_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-RESERVED")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/deliveries/",
            {
                "customer_name": "Internal Department",
                "receiver_name": "Receiver Name",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        unit.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(unit.status, ProductUnit.STATUS_RESERVED)

    def test_delivery_api_rejects_issued_units_directly(self):
        user = self._user_with_permissions(
            "add_deliveryrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_ISSUED
        unit.save(update_fields=("status", "sold_date"))
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/deliveries/",
            {
                "customer_name": "Internal Department",
                "receiver_name": "Receiver Name",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        unit.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(unit.status, ProductUnit.STATUS_ISSUED)

    def test_delivery_service_rejects_units_that_are_not_available(self):
        from django.core.exceptions import ValidationError

        from .services import create_delivery_record

        unit = ProductUnit.objects.get(serial_number="API-RESERVED")

        with self.assertRaises(ValidationError):
            create_delivery_record(
                unit_ids=[unit.pk],
                customer_name="Internal Department",
            )

        unit.refresh_from_db()
        self.assertEqual(unit.status, ProductUnit.STATUS_RESERVED)
        self.assertFalse(DeliveryRecord.objects.exists())
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_DELIVERED,
            ).exists()
        )

    def test_client_return_api_moves_sold_delivery_unit_to_available(self):
        user = self._user_with_permissions(
            "view_clientreturnrecord",
            "add_clientreturnrecord",
            "change_productunit",
        )
        unit, delivery, delivery_item = self._sold_unit_with_delivery()
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/client-returns/",
            {
                "delivery": delivery.pk,
                "customer_name": "Retail Client",
                "received_from": "Client Receiver",
                "return_date": str(timezone.localdate()),
                "reason": "Returned after replacement",
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "notes": "Checked at counter",
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        unit.refresh_from_db()
        delivery.refresh_from_db()
        delivery_item.refresh_from_db()
        client_return = ClientReturnRecord.objects.get(pk=response.json()["id"])
        item = ClientReturnItem.objects.get(client_return=client_return, product_unit=unit)
        self.assertEqual(response.json()["return_number"][:9], f"RET-{timezone.localdate().year}-")
        self.assertEqual(client_return.delivery, delivery)
        self.assertEqual(client_return.customer_name, "Retail Client")
        self.assertEqual(client_return.received_by, user)
        self.assertEqual(client_return.total_units, 1)
        self.assertEqual(item.delivery_item, delivery_item)
        self.assertEqual(item.product, self.product)
        self.assertEqual(unit.status, ProductUnit.STATUS_AVAILABLE)
        self.assertIsNone(unit.sold_date)
        self.assertEqual(delivery.status, DeliveryRecord.STATUS_COMPLETED)
        self.assertTrue(delivery_item.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_CLIENT_RETURNED_AVAILABLE,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_SOLD)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.delivery_record, delivery)
        self.assertEqual(movement.client_return_record, client_return)
        self.assertEqual(movement.performed_by, user)

    def test_client_return_api_moves_sold_delivery_unit_to_repair(self):
        user = self._user_with_permissions(
            "view_clientreturnrecord",
            "add_clientreturnrecord",
            "change_productunit",
        )
        unit, delivery, _delivery_item = self._sold_unit_with_delivery()
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/client-returns/",
            {
                "delivery": delivery.pk,
                "customer_name": "Retail Client",
                "received_from": "Client Receiver",
                "return_date": str(timezone.localdate()),
                "reason": "Needs testing",
                "resolution": ProductUnit.STATUS_REPAIR,
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        unit.refresh_from_db()
        self.assertEqual(unit.status, ProductUnit.STATUS_REPAIR)
        self.assertIsNone(unit.sold_date)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_CLIENT_RETURNED_REPAIR,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_SOLD)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_REPAIR)

    def test_client_return_api_rejects_units_without_active_completed_delivery_item(self):
        user = self._user_with_permissions(
            "view_clientreturnrecord",
            "add_clientreturnrecord",
            "change_productunit",
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        unit.status = ProductUnit.STATUS_SOLD
        unit.sold_date = timezone.localdate()
        unit.save(update_fields=("status", "sold_date"))
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/client-returns/",
            {
                "customer_name": "Retail Client",
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        unit.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(unit.status, ProductUnit.STATUS_SOLD)
        self.assertFalse(ClientReturnRecord.objects.exists())
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_CLIENT_RETURNED_AVAILABLE,
            ).exists()
        )

    def test_client_return_api_blocks_duplicate_or_changed_units(self):
        user = self._user_with_permissions(
            "view_clientreturnrecord",
            "add_clientreturnrecord",
            "change_productunit",
        )
        unit, delivery, delivery_item = self._sold_unit_with_delivery()
        existing_return = ClientReturnRecord.objects.create(
            delivery=delivery,
            customer_name="Retail Client",
            resolution=ProductUnit.STATUS_AVAILABLE,
        )
        ClientReturnItem.objects.create(
            client_return=existing_return,
            delivery_item=delivery_item,
            product=self.product,
            product_unit=unit,
        )
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/client-returns/",
            {
                "delivery": delivery.pk,
                "customer_name": "Retail Client",
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ClientReturnRecord.objects.count(), 1)
        self.assertFalse(
            StockMovement.objects.filter(
                product_unit=unit,
                movement_type=StockMovement.TYPE_CLIENT_RETURNED_AVAILABLE,
            ).exists()
        )

    def test_client_return_api_permissions_are_explicit(self):
        no_view_user = self._user_with_permissions("view_productunit")
        no_view_user.groups.clear()
        self.client.force_login(no_view_user)

        list_response = self.client.get("/api/stock/client-returns/")

        self.assertEqual(list_response.status_code, 403)

        create_user = User.objects.create_user(username="client-return-create", password="test-pass")
        create_user.user_permissions.add(
            Permission.objects.get(codename="view_clientreturnrecord"),
            Permission.objects.get(codename="add_clientreturnrecord"),
        )
        create_user.groups.clear()
        unit, delivery, _delivery_item = self._sold_unit_with_delivery()
        self.client.force_login(create_user)

        create_response = self.client.post(
            "/api/stock/client-returns/",
            {
                "delivery": delivery.pk,
                "customer_name": "Retail Client",
                "resolution": ProductUnit.STATUS_AVAILABLE,
                "unit_ids": [unit.pk],
            },
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, 403)

    def test_client_return_api_returns_list_detail_and_movement_history(self):
        user = self._user_with_permissions(
            "view_clientreturnrecord",
            "view_stockmovement",
        )
        unit, delivery, delivery_item = self._sold_unit_with_delivery()
        client_return = ClientReturnRecord.objects.create(
            delivery=delivery,
            customer_name="Retail Client",
            received_from="Client Receiver",
            reason="Returned after replacement",
            resolution=ProductUnit.STATUS_AVAILABLE,
            received_by=user,
        )
        ClientReturnItem.objects.create(
            client_return=client_return,
            delivery_item=delivery_item,
            product=self.product,
            product_unit=unit,
        )
        StockMovement.objects.create(
            product=self.product,
            product_unit=unit,
            movement_type=StockMovement.TYPE_CLIENT_RETURNED_AVAILABLE,
            from_status=ProductUnit.STATUS_SOLD,
            to_status=ProductUnit.STATUS_AVAILABLE,
            performed_by=user,
            delivery_record=delivery,
            client_return_record=client_return,
            reference=client_return.return_number,
        )
        self.client.force_login(user)

        list_response = self.client.get("/api/stock/client-returns/", {"q": "Retail"})
        detail_response = self.client.get(f"/api/stock/client-returns/{client_return.pk}/")
        movements_response = self.client.get(f"/api/stock/products/{self.product.pk}/movements/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()[0]["return_number"], client_return.return_number)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["delivery"], delivery.pk)
        self.assertEqual(detail_response.json()["delivery_number"], delivery.delivery_number)
        self.assertEqual(detail_response.json()["items"][0]["delivery_item"], delivery_item.pk)
        self.assertEqual(detail_response.json()["items"][0]["serial_number"], "API-AVAILABLE")
        self.assertEqual(movements_response.status_code, 200)
        self.assertEqual(
            movements_response.json()[0]["movement_type"],
            StockMovement.TYPE_CLIENT_RETURNED_AVAILABLE,
        )
        self.assertEqual(movements_response.json()[0]["client_return"], client_return.pk)
        self.assertEqual(
            movements_response.json()[0]["client_return_number"],
            client_return.return_number,
        )

    def test_receiving_api_creates_supplier_record_and_stock_units(self):
        user = self._user_with_permissions(
            "view_productunit",
            "add_productunit",
            "view_receivingrecord",
            "add_receivingrecord",
        )
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/receiving-records/",
            {
                "supplier": self.supplier.pk,
                "reference_number": "SUP-REF-1",
                "received_date": str(timezone.localdate()),
                "notes": "Supplier stock entry",
                "item_inputs": [
                    {
                        "product": self.product.pk,
                        "quantity": 2,
                        "serial_numbers": ["API-RCV-1", "API-RCV-2"],
                        "cost": "55.00",
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(
            response.json()["receiving_number"][:9],
            f"RCV-{timezone.localdate().year}-",
        )
        self.assertEqual(response.json()["supplier"], self.supplier.pk)
        self.assertEqual(response.json()["total_quantity"], 2)
        self.assertEqual(len(response.json()["items"]), 2)
        self.assertEqual(
            ProductUnit.objects.filter(
                serial_number__in=["API-RCV-1", "API-RCV-2"],
            ).count(),
            2,
        )

    def test_receiving_api_creates_manual_quantity_without_supplier_or_units(self):
        user = self._user_with_permissions(
            "view_productunit",
            "add_productunit",
            "view_receivingrecord",
            "add_receivingrecord",
        )
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/receiving-records/",
            {
                "received_date": str(timezone.localdate()),
                "item_inputs": [
                    {
                        "product": self.product.pk,
                        "quantity": 4,
                        "cost": "0.00",
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertIsNone(response.json()["supplier"])
        self.assertEqual(response.json()["total_quantity"], 4)
        self.assertEqual(response.json()["items"][0]["product"], self.product.pk)
        self.assertIsNone(response.json()["items"][0]["product_unit"])

    def test_receiving_api_returns_single_record_detail(self):
        user = self._user_with_permissions("view_receivingrecord")

        receiving = ReceivingRecord.objects.create(
            supplier=self.supplier,
            reference_number="SUP-DETAIL-1",
            notes="Detail note",
            created_by=user,
        )
        unit = ProductUnit.objects.get(serial_number="API-AVAILABLE")
        ReceivingItem.objects.create(
            receiving=receiving,
            product=self.product,
            product_unit=unit,
            quantity=1,
            serial_number="API-AVAILABLE",
            cost="50.00",
            notes="Line note",
        )
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/receiving-records/{receiving.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], receiving.pk)
        self.assertEqual(response.json()["receiving_number"], receiving.receiving_number)
        self.assertEqual(response.json()["supplier_name"], self.supplier.name)
        self.assertEqual(response.json()["reference_number"], "SUP-DETAIL-1")
        self.assertEqual(response.json()["notes"], "Detail note")
        self.assertEqual(response.json()["created_by_name"], user.username)
        self.assertEqual(response.json()["total_quantity"], 1)
        self.assertEqual(response.json()["items"][0]["product_name"], str(self.product))
        self.assertEqual(response.json()["items"][0]["product_unit_serial_number"], "API-AVAILABLE")
        self.assertEqual(response.json()["items"][0]["cost"], "50.00")

    def test_receiving_api_updates_safe_header_and_line_metadata_only(self):
        other_supplier = Supplier.objects.create(name="Metro Hardware")
        user = self._user_with_permissions(
            "view_receivingrecord",
            "change_receivingrecord",
        )
        receiving = ReceivingRecord.objects.create(
            supplier=self.supplier,
            reference_number="OLD-REF",
            notes="Old notes",
            created_by=user,
        )
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="EDIT-SAFE-1",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=self.supplier,
            cost="10.00",
            purchase_date=timezone.localdate(),
        )
        item = ReceivingItem.objects.create(
            receiving=receiving,
            product=self.product,
            product_unit=unit,
            quantity=1,
            serial_number="EDIT-SAFE-1",
            cost="10.00",
            notes="Old line note",
        )
        self.client.force_login(user)

        response = self.client.patch(
            f"/api/stock/receiving-records/{receiving.pk}/",
            {
                "supplier": other_supplier.pk,
                "reference_number": "NEW-REF",
                "received_date": "2026-07-05",
                "notes": "Updated header",
                "receiving_number": "RCV-1999-9999",
                "created_by": None,
                "items": [
                    {
                        "id": item.pk,
                        "product": self.product.pk + 1000,
                        "quantity": 99,
                        "serial_number": "DO-NOT-EDIT",
                        "cost": "25.50",
                        "notes": "Updated line note",
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        receiving.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(receiving.supplier, other_supplier)
        self.assertEqual(receiving.reference_number, "NEW-REF")
        self.assertEqual(str(receiving.received_date), "2026-07-05")
        self.assertEqual(receiving.notes, "Updated header")
        self.assertNotEqual(receiving.receiving_number, "RCV-1999-9999")
        self.assertEqual(receiving.created_by, user)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.serial_number, "EDIT-SAFE-1")
        self.assertEqual(item.cost, 25.50)
        self.assertEqual(item.notes, "Updated line note")
        self.assertEqual(unit.supplier, other_supplier)
        self.assertEqual(str(unit.purchase_date), "2026-07-05")
        self.assertEqual(unit.cost, 25.50)

    def test_receiving_api_cancels_when_linked_units_are_available(self):
        user = self._user_with_permissions(
            "view_receivingrecord",
            "change_receivingrecord",
            "change_productunit",
        )
        receiving = ReceivingRecord.objects.create(
            supplier=self.supplier,
            reference_number="CANCEL-ME",
            created_by=user,
        )
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="CANCEL-RCV-1",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=self.supplier,
            isactive=True,
        )
        item = ReceivingItem.objects.create(
            receiving=receiving,
            product=self.product,
            product_unit=unit,
            quantity=1,
            serial_number=unit.serial_number,
            cost="11.00",
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/receiving-records/{receiving.pk}/cancel/",
            {"cancel_reason": "Wrong serial entered"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        receiving.refresh_from_db()
        item.refresh_from_db()
        unit.refresh_from_db()
        self.assertEqual(receiving.status, ReceivingRecord.STATUS_CANCELLED)
        self.assertFalse(receiving.isactive)
        self.assertEqual(receiving.cancel_reason, "Wrong serial entered")
        self.assertEqual(receiving.cancelled_by, user)
        self.assertIsNotNone(receiving.cancelled_at)
        self.assertFalse(item.isactive)
        self.assertEqual(unit.status, ProductUnit.STATUS_INACTIVE)
        self.assertFalse(unit.isactive)
        movement = StockMovement.objects.get(
            product_unit=unit,
            movement_type=StockMovement.TYPE_RECEIVING_CANCELLED,
        )
        self.assertEqual(movement.from_status, ProductUnit.STATUS_AVAILABLE)
        self.assertEqual(movement.to_status, ProductUnit.STATUS_INACTIVE)
        self.assertEqual(movement.reason, "Wrong serial entered")
        self.assertEqual(movement.performed_by, user)

    def test_receiving_api_blocks_cancel_when_linked_unit_is_used(self):
        user = self._user_with_permissions(
            "view_receivingrecord",
            "change_receivingrecord",
            "change_productunit",
        )
        receiving = ReceivingRecord.objects.create(supplier=self.supplier)
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="USED-RCV-1",
            status=ProductUnit.STATUS_RESERVED,
            supplier=self.supplier,
            isactive=True,
        )
        ReceivingItem.objects.create(
            receiving=receiving,
            product=self.product,
            product_unit=unit,
            quantity=1,
            serial_number=unit.serial_number,
            cost="11.00",
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/receiving-records/{receiving.pk}/cancel/",
            {"cancel_reason": "Wrong serial entered"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        receiving.refresh_from_db()
        unit.refresh_from_db()
        self.assertTrue(receiving.isactive)
        self.assertEqual(unit.status, ProductUnit.STATUS_RESERVED)
        self.assertTrue(unit.isactive)

    def test_receiving_api_change_requires_change_receiving_permission(self):
        user = self._user_with_permissions("view_receivingrecord")
        receiving = ReceivingRecord.objects.create(supplier=self.supplier)
        self.client.force_login(user)

        response = self.client.patch(
            f"/api/stock/receiving-records/{receiving.pk}/",
            {"notes": "No permission"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_receiving_api_cancel_requires_product_unit_change_permission(self):
        user = self._user_with_permissions(
            "view_receivingrecord",
            "change_receivingrecord",
        )
        receiving = ReceivingRecord.objects.create(supplier=self.supplier)
        unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="PERM-CANCEL-1",
            status=ProductUnit.STATUS_AVAILABLE,
            supplier=self.supplier,
            isactive=True,
        )
        ReceivingItem.objects.create(
            receiving=receiving,
            product=self.product,
            product_unit=unit,
            quantity=1,
            serial_number=unit.serial_number,
        )
        self.client.force_login(user)

        response = self.client.post(
            f"/api/stock/receiving-records/{receiving.pk}/cancel/",
            {"cancel_reason": "No unit permission"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_receiving_api_detail_requires_view_permission(self):
        user = self._user_with_permissions()
        user.groups.clear()
        from .models import ReceivingRecord

        receiving = ReceivingRecord.objects.create()
        self.client.force_login(user)

        response = self.client.get(f"/api/stock/receiving-records/{receiving.pk}/")

        self.assertEqual(response.status_code, 403)

    def test_receiving_api_requires_add_permission_to_create(self):
        user = self._user_with_permissions("view_receivingrecord")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/receiving-records/",
            {
                "item_inputs": [{"product": self.product.pk, "quantity": 1}],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_receiving_api_rejects_existing_serial_number(self):
        user = self._user_with_permissions(
            "view_productunit",
            "add_productunit",
            "view_receivingrecord",
            "add_receivingrecord",
        )
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/receiving-records/",
            {
                "supplier": self.supplier.pk,
                "item_inputs": [
                    {
                        "product": self.product.pk,
                        "quantity": 1,
                        "serial_numbers": ["API-AVAILABLE"],
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
