from django.contrib import admin
from django.db.models import Count, Q
from .models import Product, Type, Category, Brand, ProductModel, Supplier, ProductUnit


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
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
        "image",
        "crdate",
        "isactive",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            available_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_AVAILABLE,
                    units__isactive=True,
                ),
            )
        )

    @admin.display(description="Available Qty", ordering="available_unit_count")
    def available_quantity(self, obj):
        if hasattr(obj, "available_unit_count"):
            return obj.available_unit_count

        return obj.units.filter(
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        ).count()

    @admin.display(description="Type", ordering="category__type__name")
    def product_type(self, obj):
        return obj.category.type

    @admin.display(description="Brand", ordering="model__brand__brandname")
    def brand(self, obj):
        return obj.model.brand


admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ProductModel)
admin.site.register(Supplier)


@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
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
    list_filter = ("status", "supplier", "isactive", "purchase_date", "sold_date")
    search_fields = (
        "serial_number",
        "product__descript",
        "product__printed",
        "product__sku",
    )
    list_select_related = ("product", "supplier")
    readonly_fields = ("crdate",)
