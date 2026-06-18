from django.contrib import admin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.db import models
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from pathlib import Path
from unittest.mock import patch

from bim.ui_registry import UI_TOKENS, ui_item


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
    DeliveryRecord,
    Product,
    ProductModel,
    ProductUnit,
    Supplier,
    Type,
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
                "printed",
                "sku",
                "barcode",
                "total_quantity",
                "available_quantity",
                "reserved_quantity",
                "sold_quantity",
                "returned_quantity",
                "minimum_stock_level",
                "reorder_stock_level",
                "stock_alert",
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


class UIRegistryTests(SimpleTestCase):
    def test_core_ui_tokens_define_names_icons_and_tones(self):
        for key in (
            "inventory",
            "operations",
            "total_products",
            "available_stock",
            "out_of_stock",
            "low_stock",
            "receive_stock",
            "create_delivery",
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

        self.assertEqual(create_delivery["icon"], delivery_records["icon"])
        self.assertEqual(create_delivery["tone"], delivery_records["tone"])
        self.assertEqual(create_delivery["icon"], "delivery")
        self.assertEqual(create_delivery["tone"], "indigo")

    def test_frontend_uses_registry_for_workflow_icons(self):
        app_source = Path("frontend/src/App.jsx").read_text(encoding="utf-8")

        self.assertNotIn("<Download", app_source)
        self.assertNotIn("<Truck", app_source)
        self.assertIn("workflowMeta", Path("frontend/src/uiRegistry.js").read_text(encoding="utf-8"))

    def test_frontend_greeting_uses_browser_hour(self):
        app_source = Path("frontend/src/App.jsx").read_text(encoding="utf-8")

        self.assertIn("function greetingPeriodForHour(hour)", app_source)
        self.assertIn("new Date().getHours()", app_source)
        self.assertIn("data.hero.greetingName", app_source)


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
            serial_number="RETURNED",
            status=ProductUnit.STATUS_RETURNED,
            isactive=True,
        )

        self.assertEqual(self.product.total_units, 5)
        self.assertEqual(self.product.available_units, 2)
        self.assertEqual(self.product.reserved_units, 1)
        self.assertEqual(self.product.sold_units, 1)
        self.assertEqual(self.product.returned_units, 1)
        self.assertEqual(self.product_admin.total_quantity(self.product), 5)
        self.assertEqual(self.product_admin.available_quantity(self.product), 2)

    def test_product_stock_alert_uses_product_thresholds(self):
        self.product.reorder_stock_level = 3
        self.product.minimum_stock_level = 0
        self.product.save()
        ProductUnit.objects.create(
            product=self.product,
            serial_number="AVAILABLE-THRESHOLD",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )

        self.assertTrue(self.product.is_low_stock)
        self.assertFalse(self.product.is_critical_stock)
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
                "product__printed",
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
        self.product.reorder_stock_level = 2
        self.product.save()

        response = self.client.get("/stock/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim_stock/dashboard.html")
        self.assertEqual(response.context["total_products"], 1)
        self.assertEqual(response.context["available_units"], 1)
        self.assertEqual(response.context["sold_units"], 1)
        self.assertEqual(response.context["low_stock_products"], 1)

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

    def test_product_detail_hides_unit_details_without_unit_permission(self):
        user = User.objects.create_user(username="product-only", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        self.client.force_login(user)

        response = self.client.get(f"/stock/products/{self.product.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["available_unit_count"], 1)
        self.assertEqual(list(response.context["available_units"]), [])
        self.assertContains(response, "Stock unit details require stock unit permission")
        self.assertNotContains(response, "AVAILABLE-DETAIL")

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
        from bim_accounts.forms import BimUserChangeForm

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
        from bim_accounts.forms import BimUserChangeForm

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
        from bim_accounts.forms import BimUserCreationForm

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
        from bim_accounts.forms import BimUserCreationForm

        form = BimUserCreationForm(data={"email": "Jad.Alasmar@bimpos.com"})

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "jad.alasmar@bimpos.com")
        self.assertTrue(user.username.startswith("pending-jad.alasmar"))
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertTrue(user.groups.filter(name="Viewer").exists())

    def test_user_admin_creation_generates_unique_pending_usernames(self):
        from bim_accounts.forms import BimUserCreationForm

        first_form = BimUserCreationForm(data={"email": "jad.alasmar@bimpos.com"})
        second_form = BimUserCreationForm(data={"email": "jad.alasmar@example.com"})

        self.assertTrue(first_form.is_valid(), first_form.errors)
        first_user = first_form.save()
        self.assertTrue(second_form.is_valid(), second_form.errors)
        second_user = second_form.save()

        self.assertNotEqual(first_user.username, second_user.username)
        self.assertTrue(second_user.username.startswith("pending-jad.alasmar"))

    def test_user_admin_allows_unchanged_email_on_change(self):
        from bim_accounts.forms import BimUserChangeForm

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
        self.assertTemplateUsed(get_response, "registration/password_setup_confirm.html")
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
        self.assertContains(response, 'placeholder="jad.alasmar"')
        self.assertNotContains(response, 'value="jad.alasmar"')

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
        from bim_accounts.utils import send_password_setup_email

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
        from bim_accounts.admin import BimUserAdmin

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
            "bim_accounts.utils.send_mail",
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
            "/inventory/",
            "/inventory/products/new/",
            "/inventory/receiving/new/",
            "/inventory/deliveries/new/",
        )

        for route in protected_routes:
            with self.subTest(route=route):
                response = self.client.get(route)

                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, f"/accounts/login/?next={route}")

    def test_command_center_data_api_returns_refreshable_dashboard_payload(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
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
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="AUTO-REFRESH-UNIT",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/api/command-center/")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["currentPath"], "/")
        self.assertEqual(data["api"]["commandCenter"], "/api/command-center/")
        self.assertEqual(data["pollIntervalMs"], 60000)
        self.assertEqual(data["recentReceiving"][0]["title"], "Canon L100")
        self.assertEqual(
            data["recentReceiving"][0]["reference"],
            f"RCV-{timezone.localdate().year}-{unit.pk:04d}",
        )

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
        self.client.force_login(user)

        response = self.client.get("/")

        overview = response.context["initial_data"]["overview"]
        self.assertNotIn("Sites", {item["label"] for item in overview})
        self.assertNotIn("Sold Units", {item["label"] for item in overview})
        self.assertIn("Delivery Records", {item["label"] for item in overview})
        self.assertTrue(all(item.get("icon") for item in overview))
        overview_by_label = {item["label"]: item for item in overview}
        self.assertEqual(overview_by_label["Delivery Records"]["tone"], "indigo")
        self.assertFalse(overview_by_label["Total Assets"]["enabled"])
        self.assertFalse(overview_by_label["Knowledge Docs"]["enabled"])
        self.assertEqual(overview_by_label["Total Assets"]["detail"], "Coming later")
        self.assertEqual(overview_by_label["New Stock Units"]["tone"], "green")

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
        self.assertEqual(operations_module["count"], 2)
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

    def test_command_center_recent_activity_labels_sold_units_as_delivered(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
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
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="DELIVERED-ACTIVITY",
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/")
        activity = response.context["initial_data"]["recentActivity"][0]

        self.assertEqual(activity["type"], "Delivery")
        self.assertEqual(
            activity["reference"],
            f"DLV-{timezone.localdate().year}-{unit.pk:04d}",
        )
        self.assertEqual(activity["related"], "Canon L100")
        self.assertEqual(activity["status"], "Delivered")
        self.assertEqual(activity["status_class"], "delivered")

    def test_command_center_recent_activity_uses_receiving_reference_fallback(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
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
        unit = ProductUnit.objects.create(
            product=product,
            serial_number="RECEIVING-ACTIVITY",
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        self.client.force_login(user)

        response = self.client.get("/")
        activity = response.context["initial_data"]["recentActivity"][0]

        self.assertEqual(activity["type"], "Receiving")
        self.assertEqual(
            activity["reference"],
            f"RCV-{timezone.localdate().year}-{unit.pk:04d}",
        )
        self.assertEqual(activity["related"], "Canon L100")
        self.assertEqual(activity["status"], "Received")
        self.assertEqual(activity["status_class"], "received")
        receiving_panel = response.context["initial_data"]["recentReceiving"][0]
        self.assertEqual(
            receiving_panel["reference"],
            f"RCV-{timezone.localdate().year}-{unit.pk:04d}",
        )
        self.assertEqual(receiving_panel["title"], "Canon L100")
        self.assertEqual(receiving_panel["detail"], "Laser")
        self.assertEqual(
            receiving_panel["href"],
            f"/inventory/products/{product.pk}/",
        )
        self.assertNotIn(unit.serial_number, str(receiving_panel))
        self.assertEqual(receiving_panel["status"], "Received")
        self.assertEqual(receiving_panel["status_class"], "received")

    def test_command_center_recent_deliveries_panel_uses_delivery_records(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
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
        self.assertEqual(delivery_panel["detail"], "1 Canon L100")
        self.assertIsNone(delivery_panel["href"])
        self.assertEqual(
            delivery_panel["futureHref"],
            f"/inventory/deliveries/{delivery.pk}/",
        )
        self.assertEqual(delivery_panel["status"], "Delivered")
        self.assertEqual(delivery_panel["status_class"], "delivered")

    def test_command_center_quick_actions_are_current_workflows_only(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="add_product"),
            Permission.objects.get(codename="add_productunit"),
            Permission.objects.get(codename="change_productunit"),
            Permission.objects.get(codename="view_product"),
        )
        self.client.force_login(user)

        response = self.client.get("/")
        actions = response.context["initial_data"]["quickActions"]
        actions_by_label = {action["label"]: action for action in actions}

        self.assertEqual(
            set(actions_by_label),
            {"Add Product", "Receive Stock", "Create Delivery", "Add Supplier"},
        )
        self.assertEqual(actions_by_label["Add Product"]["href"], "/inventory/products/new/")
        self.assertEqual(actions_by_label["Receive Stock"]["href"], "/inventory/receiving/new/")
        self.assertEqual(
            actions_by_label["Create Delivery"]["href"],
            "/inventory/deliveries/new/",
        )
        self.assertTrue(actions_by_label["Add Product"]["enabled"])
        self.assertTrue(actions_by_label["Receive Stock"]["enabled"])
        self.assertTrue(actions_by_label["Create Delivery"]["enabled"])
        self.assertEqual(actions_by_label["Create Delivery"]["icon"], "delivery")
        self.assertEqual(actions_by_label["Create Delivery"]["tone"], "indigo")
        self.assertFalse(actions_by_label["Add Supplier"]["enabled"])
        self.assertIsNone(actions_by_label["Add Supplier"]["href"])

    def test_command_center_stock_alert_kpis_use_inventory_counts(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        user.user_permissions.add(Permission.objects.get(codename="view_product"))
        product_type = Type.objects.create(name="Printer")
        category = Category.objects.create(type=product_type, name="Laser")
        brand = Brand.objects.create(brandname="Canon")
        model = ProductModel.objects.create(brand=brand, modelname="L100")
        out_product = Product.objects.create(
            descript="Canon laser printer",
            printed="Canon L100",
            category=category,
            model=model,
            reorder_stock_level=2,
            minimum_stock_level=1,
        )
        low_model = ProductModel.objects.create(brand=brand, modelname="L200")
        low_product = Product.objects.create(
            descript="Canon laser printer L200",
            printed="Canon L200",
            category=category,
            model=low_model,
            reorder_stock_level=3,
            minimum_stock_level=1,
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
        low_stock_alert = response.context["initial_data"]["lowStockAlerts"][0]
        self.assertEqual(low_stock_alert["productName"], "Canon L200")
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
            Permission.objects.get(codename="change_productunit"),
            Permission.objects.get(codename="view_product"),
        )
        self.client.force_login(user)

        response = self.client.get("/")
        actions = response.context["initial_data"]["quickActions"]
        actions_by_label = {action["label"]: action for action in actions}

        self.assertEqual(
            set(actions_by_label),
            {"Add Product", "Receive Stock", "Create Delivery", "Add Supplier"},
        )
        self.assertFalse(actions_by_label["Add Supplier"]["enabled"])
        self.assertIsNone(actions_by_label["Add Supplier"]["href"])
        self.assertEqual(actions_by_label["Add Supplier"]["description"], "Coming later")

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
            "Search products, stock units, deliveries, suppliers, companies...",
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
        product_type = Type.objects.create(name="Printer")
        category = Category.objects.create(type=product_type, name="Laser")
        brand = Brand.objects.create(brandname="Canon")

        for index in range(2):
            model = ProductModel.objects.create(brand=brand, modelname=f"L{index}")
            product = Product.objects.create(
                descript=f"Canon laser printer {index}",
                printed=f"Canon L{index}",
                category=category,
                model=model,
                reorder_stock_level=3,
                minimum_stock_level=1,
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

    def test_receive_stock_react_page_uses_receive_stock_route(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_supplier"),
            Permission.objects.get(codename="add_productunit"),
        )
        self.client.force_login(user)

        response = self.client.get("/inventory/receiving/new/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/inventory/receiving/new/",
        )
        receive_action = next(
            action
            for action in response.context["initial_data"]["quickActions"]
            if action["label"] == "Receive Stock"
        )
        self.assertEqual(receive_action["href"], "/inventory/receiving/new/")

    def test_create_delivery_react_page_uses_delivery_route(self):
        user = User.objects.create_user(username="support", password="test-pass")
        user.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_productunit"),
            Permission.objects.get(codename="change_productunit"),
        )
        self.client.force_login(user)

        response = self.client.get("/inventory/deliveries/new/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bim/react_app.html")
        self.assertEqual(
            response.context["initial_data"]["currentPath"],
            "/inventory/deliveries/new/",
        )
        delivery_action = next(
            action
            for action in response.context["initial_data"]["quickActions"]
            if action["label"] == "Create Delivery"
        )
        self.assertEqual(delivery_action["href"], "/inventory/deliveries/new/")

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
        for group_name in ("Administrator", "Operations Manager", "IT Support", "Viewer"):
            self.assertTrue(Group.objects.filter(name=group_name).exists())

    def test_bimpos_groups_have_expected_permission_levels(self):
        administrator_group = Group.objects.get(name="Administrator")
        operations_manager_group = Group.objects.get(name="Operations Manager")
        it_support_group = Group.objects.get(name="IT Support")
        viewer_group = Group.objects.get(name="Viewer")

        administrator_permissions = set(
            administrator_group.permissions.filter(content_type__app_label="bim_stock")
            .values_list("codename", flat=True)
        )
        operations_manager_permissions = set(
            operations_manager_group.permissions.filter(content_type__app_label="bim_stock")
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
        self.assertTrue(all(not code.startswith("delete_") for code in operations_manager_permissions))
        self.assertTrue(any(code.startswith("add_") for code in operations_manager_permissions))
        self.assertTrue(any(code.startswith("change_") for code in operations_manager_permissions))
        self.assertTrue(any(code.startswith("view_") for code in operations_manager_permissions))
        self.assertTrue(all(not code.startswith("add_") for code in it_support_permissions))
        self.assertTrue(all(not code.startswith("delete_") for code in it_support_permissions))
        self.assertTrue(any(code.startswith("change_") for code in it_support_permissions))
        self.assertTrue(any(code.startswith("view_") for code in it_support_permissions))
        self.assertTrue(viewer_permissions)
        self.assertTrue(all(code.startswith("view_") for code in viewer_permissions))


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


class InventoryApiTests(TestCase):
    def setUp(self):
        self.product_type = Type.objects.create(name="Printer")
        self.category = Category.objects.create(type=self.product_type, name="Laser")
        self.brand = Brand.objects.create(brandname="Canon")
        self.model = ProductModel.objects.create(brand=self.brand, modelname="L100")
        self.supplier = Supplier.objects.create(name="Gulf Networks LLC")
        self.product = Product.objects.create(
            descript="Canon laser printer",
            printed="Canon L100",
            category=self.category,
            model=self.model,
            barcode="BAR-CANON-L100",
            minimum_stock_level=1,
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
        self.assertEqual(product_data["model_name"], "L100")
        self.assertEqual(product_data["total_units"], 2)
        self.assertEqual(product_data["available_units"], 1)
        self.assertEqual(product_data["reserved_units"], 1)
        self.assertEqual(product_data["minimum_stock_level"], 1)
        self.assertEqual(product_data["reorder_stock_level"], 2)
        self.assertTrue(product_data["is_low_stock"])
        self.assertTrue(product_data["is_critical_stock"])
        self.assertEqual(product_data["stock_alert_tone"], "critical")

    def test_product_api_requires_product_permission(self):
        user = User.objects.create_user(username="no-perm", password="test-pass")
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
                "printed": "Canon L200",
                "category": self.category.pk,
                "model": new_model.pk,
                "barcode": "BAR-CANON-L200",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["sku"], "LAS-CAN-L200")

    def test_product_api_creates_product_with_new_model_name(self):
        user = self._user_with_permissions("view_product", "add_product")
        self.client.force_login(user)

        response = self.client.post(
            "/api/stock/products/",
            {
                "descript": "Canon laser printer L300",
                "printed": "Canon L300",
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

    def test_reference_apis_return_lookup_data(self):
        user = self._user_with_permissions(
            "view_product",
            "view_productunit",
            "view_supplier",
        )
        self.client.force_login(user)

        responses = [
            self.client.get("/api/stock/types/"),
            self.client.get("/api/stock/categories/"),
            self.client.get("/api/stock/brands/"),
            self.client.get("/api/stock/models/"),
            self.client.get("/api/stock/suppliers/"),
        ]

        self.assertTrue(all(response.status_code == 200 for response in responses))
        self.assertIn("Printer", {item["name"] for item in responses[0].json()})
        self.assertIn("Gulf Networks LLC", {item["name"] for item in responses[4].json()})

    def test_summary_api_returns_inventory_counts(self):
        user = self._user_with_permissions("view_product")
        self.client.force_login(user)

        response = self.client.get("/api/stock/summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_products"], 1)
        self.assertEqual(response.json()["available_units"], 1)
        self.assertEqual(response.json()["reserved_units"], 1)
        self.assertEqual(response.json()["low_stock_products"], 1)
        self.assertEqual(response.json()["critical_stock_products"], 1)

    def test_delivery_api_creates_record_and_marks_units_sold(self):
        user = self._user_with_permissions(
            "view_product",
            "view_productunit",
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
        self.assertTrue(
            DeliveryRecord.objects.filter(
                delivery_number=response.json()["delivery_number"],
                items__product_unit=unit,
            ).exists()
        )

    def test_delivery_api_rejects_unavailable_units(self):
        user = self._user_with_permissions(
            "view_product",
            "view_productunit",
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
