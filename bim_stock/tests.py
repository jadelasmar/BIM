from django.contrib import admin
from django.contrib.auth.models import Group, Permission, User
from django.db import models
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from .admin import ProductAdmin, ProductUnitAdmin, ProductUnitPurchaseForm
from .models import Brand, Category, Product, ProductModel, ProductUnit, Type


# Tests for Product admin list/search/filter configuration.
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


# Tests the available stock count shown in Product admin.
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
                "product__printed",
                "product__sku",
                "product__barcode",
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


# Tests the /stock/ dashboard page counts.
class StockDashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="stock-user",
            password="test-pass",
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_productunit"),
        )
        product_type = Type.objects.create(name="Printer")
        category = Category.objects.create(type=product_type, name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            printed="Canon L100",
            category=category,
            model=model,
            barcode="BAR-CANON-L100",
        )
        Product.objects.create(
            descript="Inactive printer",
            printed="Inactive L100",
            category=category,
            model=ProductModel.objects.create(brand=brand, modelname="L200"),
            isactive=False,
        )

    def test_stock_dashboard_shows_current_stock_counts(self):
        self.client.force_login(self.user)
        ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-1",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-INACTIVE",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=False,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="SOLD-1",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="DAMAGED-1",
            status=ProductUnit.STATUS_DAMAGED,
            isactive=True,
        )

        response = self.client.get("/stock/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim_stock/dashboard.html")
        self.assertEqual(response.context["total_products"], 1)
        self.assertEqual(response.context["available_units"], 1)
        self.assertEqual(response.context["sold_units"], 1)
        self.assertEqual(response.context["damaged_units"], 1)

    def test_stock_dashboard_requires_login(self):
        response = self.client.get("/stock/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/stock/")


# Tests custom stock pages outside Django admin.
class CustomStockPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="stock-user",
            password="test-pass",
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_productunit"),
        )
        product_type = Type.objects.create(name="Printer")
        category = Category.objects.create(type=product_type, name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        inactive_model = ProductModel.objects.create(brand=brand, modelname="L200")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            printed="Canon L100",
            category=category,
            model=model,
            barcode="BAR-CANON-L100",
        )
        self.inactive_product = Product.objects.create(
            descript="Inactive printer",
            printed="Inactive L200",
            category=category,
            model=inactive_model,
            isactive=False,
        )
        self.available_unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-DETAIL",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        self.sold_unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="SOLD-DETAIL",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        self.inactive_unit = ProductUnit.objects.create(
            product=self.product,
            serial_number="INACTIVE-DETAIL",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=False,
        )

    def test_product_list_shows_active_products_with_available_counts(self):
        self.client.force_login(self.user)
        response = self.client.get("/stock/products/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim_stock/product_list.html")
        products = list(response.context["products"])
        self.assertEqual(products, [self.product])
        self.assertEqual(products[0].available_unit_count, 1)

    def test_product_list_can_search_by_barcode(self):
        self.client.force_login(self.user)
        response = self.client.get("/stock/products/", {"q": "CANON-L100"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["products"]), [self.product])
        self.assertEqual(response.context["query"], "CANON-L100")

    def test_product_detail_shows_available_units_only(self):
        self.client.force_login(self.user)
        response = self.client.get(f"/stock/products/{self.product.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim_stock/product_detail.html")
        self.assertEqual(response.context["product"], self.product)
        self.assertEqual(response.context["available_unit_count"], 1)
        self.assertContains(response, "BAR-CANON-L100")
        self.assertEqual(
            list(response.context["available_units"]),
            [self.available_unit],
        )

    def test_product_detail_does_not_show_inactive_products(self):
        self.client.force_login(self.user)
        response = self.client.get(f"/stock/products/{self.inactive_product.pk}/")

        self.assertEqual(response.status_code, 404)

    def test_stock_list_shows_active_units(self):
        self.client.force_login(self.user)
        response = self.client.get("/stock/units/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim_stock/stock_list.html")
        self.assertEqual(
            list(response.context["units"]),
            [self.available_unit, self.sold_unit],
        )

    def test_stock_list_can_search_by_product_barcode(self):
        self.client.force_login(self.user)
        response = self.client.get("/stock/units/", {"q": "BAR-CANON-L100"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["units"]),
            [self.available_unit, self.sold_unit],
        )
        self.assertEqual(response.context["query"], "BAR-CANON-L100")

    def test_custom_stock_pages_show_staff_navigation_helpers(self):
        self.client.force_login(self.user)
        dashboard_response = self.client.get("/stock/")
        product_response = self.client.get("/stock/products/", {"q": "CANON"})
        stock_response = self.client.get("/stock/units/", {"q": "CANON"})

        self.assertContains(dashboard_response, "Browse Products")
        self.assertContains(dashboard_response, "Browse Stock Units")
        self.assertContains(product_response, "Showing 1 product")
        self.assertContains(product_response, "Clear Search")
        self.assertContains(stock_response, "Showing 2 stock units")
        self.assertContains(stock_response, "Clear Search")

    def test_stock_pages_require_stock_permissions(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        self.client.force_login(user)

        response = self.client.get("/stock/products/")

        self.assertEqual(response.status_code, 403)


# Tests BIM Nexus auth, role preparation, and Command Center behavior.
class BIMPOSAccessTests(TestCase):
    def test_login_page_uses_bim_nexus_template(self):
        response = self.client.get("/accounts/login/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertContains(response, "BIM Nexus Login")

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

    def test_command_center_shows_inventory_module_by_permission(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/module_launcher.html")
        self.assertContains(response, "BIM Nexus Command Center")
        self.assertContains(response, "Inventory")
        self.assertContains(response, 'href="/stock/"')

    def test_command_center_disables_inventory_without_permission(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        self.client.force_login(user)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inventory")
        self.assertNotContains(response, 'href="/stock/"')

    def test_bimpos_groups_are_prepared(self):
        for group_name in ("Admin", "Stock Manager", "IT Support", "Viewer"):
            self.assertTrue(Group.objects.filter(name=group_name).exists())


# Tests ProductUnit model fields that support pricing.
class ProductUnitModelTests(SimpleTestCase):
    def test_product_unit_tracks_client_selling_price(self):
        field = ProductUnit._meta.get_field("selling_price")

        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
        self.assertEqual(field.default, 0)
