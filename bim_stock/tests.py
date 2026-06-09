from importlib.util import find_spec

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
from unittest.mock import patch


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
                "total_quantity",
                "available_quantity",
                "reserved_quantity",
                "sold_quantity",
                "damaged_quantity",
                "returned_quantity",
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
            serial_number="DAMAGED",
            status=ProductUnit.STATUS_DAMAGED,
            isactive=True,
        )
        ProductUnit.objects.create(
            product=self.product,
            serial_number="RETURNED",
            status=ProductUnit.STATUS_RETURNED,
            isactive=True,
        )

        self.assertEqual(self.product.total_units, 6)
        self.assertEqual(self.product.available_units, 2)
        self.assertEqual(self.product.reserved_units, 1)
        self.assertEqual(self.product.sold_units, 1)
        self.assertEqual(self.product.damaged_units, 1)
        self.assertEqual(self.product.returned_units, 1)
        self.assertEqual(self.product_admin.total_quantity(self.product), 6)
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
        self.assertEqual(inventory_module["href"], "/stock/")

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


class InventoryApiReadinessTests(SimpleTestCase):
    def test_django_rest_framework_is_not_installed_yet(self):
        self.assertIsNone(find_spec("rest_framework"))
