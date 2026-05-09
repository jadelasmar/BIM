from django.contrib import admin
from django.db import models
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .admin import ProductAdmin, ProductUnitAdmin, ProductUnitPurchaseForm
from .models import Brand, Category, Product, ProductModel, ProductUnit, Type


class ProductAdminTests(SimpleTestCase):
    def setUp(self):
        self.product_admin = ProductAdmin(Product, admin.site)

    def test_product_admin_has_staff_friendly_listing_tools(self):
        self.assertEqual(
            self.product_admin.list_display,
            (
                "descript",
                "printed",
                "sku",
                "barcode",
                "available_quantity",
                "product_type",
                "category",
                "brand",
                "model",
                "isactive",
                "crdate",
            ),
        )
        self.assertEqual(
            self.product_admin.search_fields,
            ("descript", "printed", "sku", "barcode"),
        )
        self.assertEqual(
            self.product_admin.list_filter,
            ("category", "model__brand", "isactive"),
        )
        self.assertEqual(self.product_admin.readonly_fields, ("sku", "crdate"))
        self.assertEqual(self.product_admin.ordering, ("descript", "printed", "sku"))
        self.assertEqual(
            self.product_admin.list_select_related,
            ("category__type", "model__brand"),
        )


class ProductAdminStockCountTests(TestCase):
    def setUp(self):
        self.product_admin = ProductAdmin(Product, admin.site)
        product_type = Type.objects.create(name="Printer")
        category = Category.objects.create(type=product_type, name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            printed="Canon L100",
            category=category,
            model=model,
        )

    def test_available_quantity_counts_only_active_available_units(self):
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

        self.assertEqual(self.product_admin.available_quantity(self.product), 2)

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
                "product__printed",
                "product__sku",
            ),
        )
        self.assertEqual(
            self.product_unit_admin.list_filter,
            ("status", "supplier", "isactive", "purchase_date", "sold_date"),
        )
        self.assertEqual(self.product_unit_admin.readonly_fields, ("crdate",))
        self.assertEqual(self.product_unit_admin.actions, ("mark_as_sold",))
        self.assertEqual(
            self.product_unit_admin.list_select_related,
            ("product", "supplier"),
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


class ProductUnitPurchaseFormTests(SimpleTestCase):
    def test_new_product_unit_defaults_to_available_purchase_today(self):
        form = ProductUnitPurchaseForm()

        self.assertEqual(
            form.fields["status"].initial,
            ProductUnit.STATUS_AVAILABLE,
        )
        self.assertEqual(form.fields["purchase_date"].initial, timezone.localdate())


class ProductUnitSellingWorkflowTests(TestCase):
    def setUp(self):
        self.product_unit_admin = ProductUnitAdmin(ProductUnit, admin.site)
        product_type = Type.objects.create(name="Printer")
        category = Category.objects.create(type=product_type, name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        product = Product.objects.create(
            descript="Canon laser printer",
            printed="Canon L100",
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


class ProductUnitModelTests(SimpleTestCase):
    def test_product_unit_tracks_client_selling_price(self):
        field = ProductUnit._meta.get_field("selling_price")

        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
        self.assertEqual(field.default, 0)
