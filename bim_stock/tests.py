from django.contrib import admin
from django.test import SimpleTestCase

from .admin import ProductAdmin, ProductUnitAdmin
from .models import Product, ProductUnit


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
        self.assertEqual(
            self.product_unit_admin.list_select_related,
            ("product", "supplier"),
        )
