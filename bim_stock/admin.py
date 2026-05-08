from django.contrib import admin
from .models import Product, Type, Category, Brand, ProductModel, Supplier, ProductUnit


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("descript", "printed", "sku", "category", "brand", "model", "isactive")
    readonly_fields = ("sku", "crdate")

    fields = (
        "descript",
        "printed",
        "type",
        "category",
        "brand",
        "model",
        "sku",
        "barcode",
        "image",
        "crdate",
        "isactive",
    )


admin.site.register(Type)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ProductModel)
admin.site.register(Supplier)
admin.site.register(ProductUnit)