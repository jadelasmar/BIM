from django.db import models


# Type is the broad product group.
# Create this first.
# Example: Hardware.
class Type(models.Model):  # renamed from ProductType
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Category belongs to a Type and narrows the product group.
# Create this after Type.
# Example: Type = Hardware, Category = Barcode Printer.
class Category(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT, related_name="categories")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(
                fields=["type", "name"],
                name="unique_category_per_type",
            )
        ]

    def __str__(self):
        return f"{self.type} - {self.name}"


# Brand stores the manufacturer or brand name for product models.
# Create this before ProductModel.
# Example: Zebra, Canon, HP.
class Brand(models.Model):
    brandname = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.brandname


# ProductModel stores the model name under a specific Brand.
# Create this after Brand.
# Example: Brand = Zebra, ProductModel = GK888T.
class ProductModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="models")
    modelname = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "modelname"],
                name="unique_model_per_brand",
            )
        ]

    def __str__(self):
        return f"{self.brand} - {self.modelname}"


# Product is the reusable product definition.
# Create this after Type, Category, Brand, and ProductModel exist.
# It is not one physical stock item; physical stock is stored in ProductUnit.
class Product(models.Model):
    descript = models.CharField(max_length=200)
    printed = models.CharField(max_length=200, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    model = models.ForeignKey(ProductModel, on_delete=models.PROTECT)

    sku = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    barcode = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(upload_to="products_images/", blank=True, null=True)

    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "model"],
                name="unique_product_category_model",
            )
        ]

    def save(self, *args, **kwargs):
        # SKU is generated from Category, Brand, and Model.
        # Example: Laser + Canon + L100 becomes LAS-CAN-L100.
        category_code = self.category.name[:3].upper() if self.category else "PRD"
        brand_code = self.model.brand.brandname[:3].upper() if self.model else "GEN"
        model_code = (
            self.model.modelname.replace(" ", "").upper() if self.model else "XXX"
        )

        self.sku = f"{category_code}-{brand_code}-{model_code}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.printed or self.descript


# Supplier stores the company or person that stock units are bought from.
class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


# ProductUnit is one real physical stock item.
# It tracks serial number, purchase info, selling info, and stock status.
class ProductUnit(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_RESERVED = "reserved"
    STATUS_SOLD = "sold"
    STATUS_DAMAGED = "damaged"
    STATUS_RETURNED = "returned"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_SOLD, "Sold"),
        (STATUS_DAMAGED, "Damaged"),
        (STATUS_RETURNED, "Returned"),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="units")

    serial_number = models.CharField(max_length=150, unique=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )

    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, blank=True, null=True
    )

    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    purchase_date = models.DateField(blank=True, null=True)
    sold_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} - {self.serial_number}"
