from django.contrib import admin
from .models import Product, Type, Category, Brand, ProductModel, Supplier, ProductUnit


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "descript",
        "printed",
        "sku",
        "product_type",
        "category",
        "brand",
        "model",
        "isactive",
    )
    readonly_fields = ("sku", "crdate")

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
        "purchase_date",
        "sold_date",
        "isactive",
    )
    list_filter = ("status", "supplier", "isactive", "purchase_date", "sold_date")
    search_fields = ("serial_number", "product__descript", "product__sku")
    readonly_fields = ("crdate",)
