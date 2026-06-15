from django.contrib import admin
from django import forms
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    Brand,
    Category,
    DeliveryItem,
    DeliveryRecord,
    Product,
    ProductModel,
    ProductUnit,
    Supplier,
    Type,
)


# Type is created first in the product setup flow.
admin.site.register(Type)


# Category belongs to Type.
admin.site.register(Category)


# Brand is created before ProductModel.
admin.site.register(Brand)


# ProductModel belongs to Brand.
admin.site.register(ProductModel)


# Product admin manages the reusable product definition, not physical stock units.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
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
    )
    search_fields = ("descript", "printed", "sku", "barcode")
    list_filter = ("category", "model__brand", "isactive")
    list_select_related = ("category__type", "model__brand")
    readonly_fields = ("sku", "crdate")
    ordering = ("descript", "printed", "sku")

    fields = (
        "descript",
        "printed",
        "category",
        "model",
        "sku",
        "barcode",
        "minimum_stock_level",
        "reorder_stock_level",
        "image",
        "crdate",
        "isactive",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            total_unit_count=Count(
                "units",
                filter=Q(units__isactive=True),
            ),
            available_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_AVAILABLE,
                    units__isactive=True,
                ),
            ),
            reserved_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_RESERVED,
                    units__isactive=True,
                ),
            ),
            sold_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_SOLD,
                    units__isactive=True,
                ),
            ),
            returned_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_RETURNED,
                    units__isactive=True,
                ),
            ),
        )

    def stock_quantity(self, obj, annotation_name, property_name):
        if hasattr(obj, annotation_name):
            return getattr(obj, annotation_name)

        return getattr(obj, property_name)

    @admin.display(description="Total Qty", ordering="total_unit_count")
    def total_quantity(self, obj):
        return self.stock_quantity(obj, "total_unit_count", "total_units")

    @admin.display(description="Available Qty", ordering="available_unit_count")
    def available_quantity(self, obj):
        return self.stock_quantity(obj, "available_unit_count", "available_units")

    @admin.display(description="Reserved Qty", ordering="reserved_unit_count")
    def reserved_quantity(self, obj):
        return self.stock_quantity(obj, "reserved_unit_count", "reserved_units")

    @admin.display(description="Sold Qty", ordering="sold_unit_count")
    def sold_quantity(self, obj):
        return self.stock_quantity(obj, "sold_unit_count", "sold_units")

    @admin.display(description="Returned Qty", ordering="returned_unit_count")
    def returned_quantity(self, obj):
        return self.stock_quantity(obj, "returned_unit_count", "returned_units")

    @admin.display(description="Stock Alert")
    def stock_alert(self, obj):
        if obj.is_critical_stock:
            return "Critical"
        if obj.is_low_stock:
            return "Low"
        return "-"

    @admin.display(description="Type", ordering="category__type__name")
    def product_type(self, obj):
        return obj.category.type

    @admin.display(description="Brand", ordering="model__brand__brandname")
    def brand(self, obj):
        return obj.model.brand


# Supplier is used when adding purchased ProductUnit records.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)


# ProductUnitPurchaseForm sets useful defaults when buying stock.
class ProductUnitPurchaseForm(forms.ModelForm):
    class Meta:
        model = ProductUnit
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["status"].initial = ProductUnit.STATUS_AVAILABLE
            self.fields["purchase_date"].initial = timezone.localdate()


# ProductUnit admin manages each physical stock item.
@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    form = ProductUnitPurchaseForm
    actions = ("mark_as_sold",)
    list_display = (
        "product",
        "serial_number",
        "status",
        "supplier",
        "cost",
        "selling_price",
        "purchase_date",
        "sold_date",
        "isactive",
    )
    list_filter = (
        "status",
        "product__category",
        "product__model__brand",
        "supplier",
        "isactive",
        "purchase_date",
        "sold_date",
    )
    search_fields = (
        "serial_number",
        "product__descript",
        "product__printed",
        "product__sku",
        "product__barcode",
    )
    list_select_related = (
        "product",
        "product__category",
        "product__model__brand",
        "supplier",
    )
    readonly_fields = ("crdate",)
    autocomplete_fields = ("product", "supplier")
    fieldsets = (
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
    )

    @admin.action(description="Mark selected units as sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(
            status=ProductUnit.STATUS_SOLD,
            sold_date=timezone.localdate(),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 0
    autocomplete_fields = ("product_unit",)
    readonly_fields = ("product", "crdate")
    fields = ("product_unit", "product", "notes", "isactive", "crdate")


@admin.register(DeliveryRecord)
class DeliveryRecordAdmin(admin.ModelAdmin):
    inlines = (DeliveryItemInline,)
    list_display = (
        "delivery_number",
        "customer_name",
        "receiver_name",
        "delivery_date",
        "status",
        "unit_count",
        "created_by",
        "isactive",
        "crdate",
    )
    search_fields = (
        "delivery_number",
        "customer_name",
        "receiver_name",
        "items__product_unit__serial_number",
        "items__product__descript",
        "items__product__sku",
    )
    list_filter = ("status", "delivery_date", "isactive")
    readonly_fields = ("delivery_number", "crdate")
    autocomplete_fields = ("created_by",)
    ordering = ("-delivery_date", "-delivery_number")

    fieldsets = (
        (
            "Delivery record",
            {
                "fields": (
                    "delivery_number",
                    "customer_name",
                    "receiver_name",
                    "delivery_date",
                    "status",
                    "created_by",
                    "isactive",
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
    )

    @admin.display(description="Units")
    def unit_count(self, obj):
        return obj.total_units
