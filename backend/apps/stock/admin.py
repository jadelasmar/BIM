from django.contrib import admin
from django import forms
from django.db.models import Count, Q
from django.utils import timezone
from .models import (
    Brand,
    Category,
    DeliveryItem,
    DeliveryRecord,
    IssueItem,
    IssueRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    ReservationItem,
    ReservationRecord,
    StockMovement,
    Supplier,
)


# Category is created before Product.
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
    )
    search_fields = ("descript", "sku", "barcode")
    list_filter = ("category", "model__brand", "isactive")
    list_select_related = ("category", "model__brand")
    readonly_fields = ("sku", "crdate")
    ordering = ("descript", "sku")

    fields = (
        "descript",
        "category",
        "model",
        "sku",
        "barcode",
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
            issued_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_ISSUED,
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
            repair_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_REPAIR,
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

    @admin.display(description="Issued Qty", ordering="issued_unit_count")
    def issued_quantity(self, obj):
        return self.stock_quantity(obj, "issued_unit_count", "issued_units")

    @admin.display(description="Sold Qty", ordering="sold_unit_count")
    def sold_quantity(self, obj):
        return self.stock_quantity(obj, "sold_unit_count", "sold_units")

    @admin.display(description="Repair Qty", ordering="repair_unit_count")
    def repair_quantity(self, obj):
        return self.stock_quantity(obj, "repair_unit_count", "repair_units")

    @admin.display(description="Stock Alert")
    def stock_alert(self, obj):
        if obj.is_low_stock:
            return "Low"
        return "-"

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


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "movement_date",
        "movement_type",
        "product",
        "product_unit",
        "from_status",
        "to_status",
        "reference",
        "performed_by",
        "isactive",
    )
    list_filter = ("movement_type", "from_status", "to_status", "movement_date", "isactive")
    search_fields = (
        "reference",
        "reason",
        "notes",
        "product__descript",
        "product__sku",
        "product_unit__serial_number",
        "receiving_record__receiving_number",
        "delivery_record__delivery_number",
        "reservation_record__reservation_number",
        "issue_record__issue_number",
    )
    list_select_related = (
        "product",
        "product_unit",
        "performed_by",
        "receiving_record",
        "delivery_record",
        "reservation_record",
        "issue_record",
    )
    readonly_fields = (
        "product_unit",
        "product",
        "movement_type",
        "from_status",
        "to_status",
        "reason",
        "notes",
        "performed_by",
        "movement_date",
        "receiving_record",
        "delivery_record",
        "reservation_record",
        "issue_record",
        "reference",
        "crdate",
        "isactive",
    )
    ordering = ("-movement_date", "-crdate")

    def has_add_permission(self, request):
        return False


class ReservationItemInline(admin.TabularInline):
    model = ReservationItem
    extra = 0
    autocomplete_fields = ("product_unit",)
    readonly_fields = ("product", "crdate")
    fields = ("product_unit", "product", "notes", "isactive", "crdate")


@admin.register(ReservationRecord)
class ReservationRecordAdmin(admin.ModelAdmin):
    inlines = (ReservationItemInline,)
    list_display = (
        "reservation_number",
        "reserved_for",
        "status",
        "expected_release_date",
        "unit_count",
        "reserved_by",
        "released_by",
        "isactive",
        "crdate",
    )
    search_fields = (
        "reservation_number",
        "reserved_for",
        "reason",
        "items__product_unit__serial_number",
        "items__product__descript",
        "items__product__sku",
    )
    list_filter = ("status", "expected_release_date", "isactive")
    readonly_fields = (
        "reservation_number",
        "reserved_at",
        "released_at",
        "crdate",
    )
    autocomplete_fields = ("reserved_by", "released_by")
    ordering = ("-reserved_at", "-reservation_number")

    fieldsets = (
        (
            "Reservation record",
            {
                "fields": (
                    "reservation_number",
                    "reserved_for",
                    "reason",
                    "expected_release_date",
                    "status",
                    "reserved_by",
                    "reserved_at",
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
        (
            "Release",
            {
                "fields": (
                    "release_reason",
                    "released_at",
                    "released_by",
                )
            },
        ),
    )

    @admin.display(description="Units")
    def unit_count(self, obj):
        return obj.total_units


class IssueItemInline(admin.TabularInline):
    model = IssueItem
    extra = 0
    autocomplete_fields = ("product_unit",)
    readonly_fields = ("product", "crdate")
    fields = ("product_unit", "product", "notes", "isactive", "crdate")


@admin.register(IssueRecord)
class IssueRecordAdmin(admin.ModelAdmin):
    inlines = (IssueItemInline,)
    list_display = (
        "issue_number",
        "issued_to",
        "status",
        "issue_date",
        "expected_return_date",
        "returned_date",
        "unit_count",
        "issued_by",
        "returned_by",
        "isactive",
        "crdate",
    )
    search_fields = (
        "issue_number",
        "issued_to",
        "department",
        "branch_or_site",
        "reason",
        "items__product_unit__serial_number",
        "items__product__descript",
        "items__product__sku",
    )
    list_filter = ("status", "issue_date", "expected_return_date", "isactive")
    readonly_fields = (
        "issue_number",
        "returned_at",
        "crdate",
    )
    autocomplete_fields = ("issued_by", "returned_by")
    ordering = ("-issue_date", "-issue_number")

    fieldsets = (
        (
            "Issue record",
            {
                "fields": (
                    "issue_number",
                    "issued_to",
                    "department",
                    "branch_or_site",
                    "reason",
                    "issue_date",
                    "expected_return_date",
                    "status",
                    "issued_by",
                    "isactive",
                )
            },
        ),
        (
            "Return",
            {
                "fields": (
                    "returned_date",
                    "return_reason",
                    "returned_by",
                    "returned_at",
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
    readonly_fields = ("delivery_number", "cancelled_at", "crdate")
    autocomplete_fields = ("created_by", "cancelled_by")
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
        (
            "Cancellation",
            {
                "fields": (
                    "cancel_reason",
                    "cancelled_at",
                    "cancelled_by",
                )
            },
        ),
    )

    @admin.display(description="Units")
    def unit_count(self, obj):
        return obj.total_units


class ReceivingItemInline(admin.TabularInline):
    model = ReceivingItem
    extra = 0
    autocomplete_fields = ("product", "product_unit")
    readonly_fields = ("crdate",)
    fields = (
        "product",
        "product_unit",
        "quantity",
        "serial_number",
        "cost",
        "notes",
        "isactive",
        "crdate",
    )


@admin.register(ReceivingRecord)
class ReceivingRecordAdmin(admin.ModelAdmin):
    inlines = (ReceivingItemInline,)
    list_display = (
        "receiving_number",
        "supplier",
        "received_date",
        "reference_number",
        "status",
        "total_quantity",
        "created_by",
        "isactive",
        "crdate",
    )
    search_fields = (
        "receiving_number",
        "reference_number",
        "supplier__name",
        "items__product__descript",
        "items__serial_number",
        "items__product_unit__serial_number",
    )
    list_filter = ("status", "supplier", "received_date", "isactive")
    readonly_fields = ("receiving_number", "cancelled_at", "crdate")
    autocomplete_fields = ("supplier", "created_by", "cancelled_by")
    ordering = ("-received_date", "-receiving_number")

    fieldsets = (
        (
            "Receiving record",
            {
                "fields": (
                    "receiving_number",
                    "supplier",
                    "reference_number",
                    "received_date",
                    "status",
                    "created_by",
                    "isactive",
                )
            },
        ),
        (
            "Cancellation",
            {
                "fields": (
                    "cancel_reason",
                    "cancelled_at",
                    "cancelled_by",
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
