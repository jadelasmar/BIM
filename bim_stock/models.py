from django.db import models


class Brand(models.Model):
    brandname = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.brandname


class ProductModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, blank=True, null=True)
    modelname = models.CharField(max_length=100)

    class Meta:
        unique_together = ("brand", "modelname")

    def __str__(self):
        return self.modelname


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Type(models.Model):  # renamed from ProductType
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    descript = models.CharField(max_length=200)
    printed = models.CharField(max_length=200, blank=True, null=True)

    type = models.ForeignKey(Type, on_delete=models.PROTECT, blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True
    )
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, blank=True, null=True)
    model = models.ForeignKey(
        ProductModel, on_delete=models.PROTECT, blank=True, null=True
    )

    sku = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    barcode = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(upload_to="products_images/", blank=True, null=True)

    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        category_code = self.category.name[:3].upper() if self.category else "PRD"
        brand_code = self.brand.brandname[:3].upper() if self.brand else "GEN"
        model_code = (
            self.model.modelname.replace(" ", "").upper() if self.model else "XXX"
        )

        self.sku = f"{category_code}-{brand_code}-{model_code}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.printed or self.descript


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_SOLD = "sold"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_SOLD, "Sold"),
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

    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} - {self.serial_number}"
