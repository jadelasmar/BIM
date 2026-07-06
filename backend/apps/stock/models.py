from django.db import models
from django.conf import settings
from django.utils import timezone


# Category groups products into a clear product family.
# Create this before Product.
# Example: Barcode Printer.
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


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
# Create this after Category, Brand, and ProductModel exist.
# It is not one physical stock item; physical stock is stored in ProductUnit.
class Product(models.Model):
    descript = models.CharField(max_length=200)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    model = models.ForeignKey(ProductModel, on_delete=models.PROTECT)

    sku = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    barcode = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(upload_to="products_images/", blank=True, null=True)
    reorder_stock_level = models.PositiveIntegerField(default=0)

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
        return self.descript

    def active_unit_count(self, status=None):
        units = self.units.filter(isactive=True)
        if status:
            units = units.filter(status=status)

        return units.count()

    @property
    def total_units(self):
        return self.active_unit_count()

    @property
    def available_units(self):
        return self.active_unit_count(ProductUnit.STATUS_AVAILABLE)

    @property
    def reserved_units(self):
        return self.active_unit_count(ProductUnit.STATUS_RESERVED)

    @property
    def issued_units(self):
        return self.active_unit_count(ProductUnit.STATUS_ISSUED)

    @property
    def sold_units(self):
        return self.active_unit_count(ProductUnit.STATUS_SOLD)

    @property
    def repair_units(self):
        return self.active_unit_count(ProductUnit.STATUS_REPAIR)

    @property
    def is_low_stock(self):
        return (
            self.reorder_stock_level > 0
            and self.available_units > 0
            and self.available_units <= self.reorder_stock_level
        )

    @property
    def stock_alert_tone(self):
        if self.is_low_stock:
            return "warning"
        return "normal"


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
    STATUS_ISSUED = "issued"
    STATUS_SOLD = "sold"
    STATUS_REPAIR = "repair"
    STATUS_INACTIVE = "inactive"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_ISSUED, "Issued"),
        (STATUS_SOLD, "Sold"),
        (STATUS_REPAIR, "Repair"),
        (STATUS_INACTIVE, "Inactive"),
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

    def sync_status_dates(self):
        if self.status == self.STATUS_SOLD and not self.sold_date:
            self.sold_date = timezone.localdate()
        elif self.status in (
            self.STATUS_AVAILABLE,
            self.STATUS_RESERVED,
            self.STATUS_ISSUED,
            self.STATUS_REPAIR,
            self.STATUS_INACTIVE,
        ):
            self.sold_date = None

    def save(self, *args, **kwargs):
        self.sync_status_dates()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.serial_number}"


class ReceivingRecord(models.Model):
    STATUS_RECORDED = "recorded"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_RECORDED, "Recorded"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    receiving_number = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        editable=False,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    reference_number = models.CharField(max_length=100, blank=True)
    received_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_RECORDED,
    )
    cancel_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cancelled_stock_receiving_records",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_receiving_records",
    )
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("-received_date", "-receiving_number")

    def save(self, *args, **kwargs):
        if not self.receiving_number:
            year = (self.received_date or timezone.localdate()).year
            prefix = f"RCV-{year}-"
            latest = (
                ReceivingRecord.objects.filter(receiving_number__startswith=prefix)
                .order_by("-receiving_number")
                .first()
            )
            next_number = 1
            if latest:
                try:
                    next_number = int(latest.receiving_number.rsplit("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    next_number = latest.pk + 1
            self.receiving_number = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.filter(isactive=True))

    def __str__(self):
        return self.receiving_number or "Receiving"


class ReceivingItem(models.Model):
    receiving = models.ForeignKey(
        ReceivingRecord,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_unit = models.OneToOneField(
        ProductUnit,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="receiving_item",
    )
    quantity = models.PositiveIntegerField(default=1)
    serial_number = models.CharField(max_length=150, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("product__descript", "serial_number", "pk")

    def save(self, *args, **kwargs):
        if self.product_unit_id:
            self.product = self.product_unit.product
            self.serial_number = self.product_unit.serial_number
            self.quantity = 1
        super().save(*args, **kwargs)

    def __str__(self):
        reference = self.serial_number or f"{self.quantity} units"
        return f"{self.receiving} - {self.product} - {reference}"


class DeliveryRecord(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    delivery_number = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        editable=False,
    )
    customer_name = models.CharField(max_length=150)
    receiver_name = models.CharField(max_length=150, blank=True)
    delivery_date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
    )
    cancel_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="cancelled_stock_delivery_records",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_delivery_records",
    )
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("-delivery_date", "-delivery_number")

    def save(self, *args, **kwargs):
        if not self.delivery_number:
            year = (self.delivery_date or timezone.localdate()).year
            prefix = f"DLV-{year}-"
            latest = (
                DeliveryRecord.objects.filter(delivery_number__startswith=prefix)
                .order_by("-delivery_number")
                .first()
            )
            next_number = 1
            if latest:
                try:
                    next_number = int(latest.delivery_number.rsplit("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    next_number = latest.pk + 1
            self.delivery_number = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)

    @property
    def total_units(self):
        return self.items.filter(isactive=True).count()

    def __str__(self):
        return self.delivery_number or "Delivery"


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(
        DeliveryRecord,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product_unit = models.OneToOneField(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="delivery_item",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("product__descript", "product_unit__serial_number")

    def save(self, *args, **kwargs):
        if self.product_unit_id and not self.product_id:
            self.product = self.product_unit.product
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.delivery} - {self.product_unit.serial_number}"


class ReservationRecord(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_RELEASED = "released"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_RELEASED, "Released"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    reservation_number = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        editable=False,
    )
    reserved_for = models.CharField(max_length=150)
    reason = models.CharField(max_length=150, blank=True)
    expected_release_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_reservation_records",
    )
    reserved_at = models.DateTimeField(default=timezone.now)
    release_reason = models.TextField(blank=True)
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="released_stock_reservation_records",
    )
    released_at = models.DateTimeField(blank=True, null=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("-reserved_at", "-reservation_number")

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            year = (self.reserved_at or timezone.now()).year
            prefix = f"RSV-{year}-"
            latest = (
                ReservationRecord.objects.filter(reservation_number__startswith=prefix)
                .order_by("-reservation_number")
                .first()
            )
            next_number = 1
            if latest:
                try:
                    next_number = int(latest.reservation_number.rsplit("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    next_number = latest.pk + 1
            self.reservation_number = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)

    @property
    def total_units(self):
        return self.items.filter(isactive=True).count()

    def __str__(self):
        return self.reservation_number or "Reservation"


class ReservationItem(models.Model):
    reservation = models.ForeignKey(
        ReservationRecord,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product_unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="reservation_items",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("product__descript", "product_unit__serial_number")

    def save(self, *args, **kwargs):
        if self.product_unit_id and not self.product_id:
            self.product = self.product_unit.product
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reservation} - {self.product_unit.serial_number}"


class IssueRecord(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_RETURNED = "returned"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_RETURNED, "Returned"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    issue_number = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        editable=False,
    )
    issued_to = models.CharField(max_length=150)
    department = models.CharField(max_length=150, blank=True)
    branch_or_site = models.CharField(max_length=150, blank=True)
    reason = models.CharField(max_length=150, blank=True)
    issue_date = models.DateField(default=timezone.localdate)
    expected_return_date = models.DateField(blank=True, null=True)
    returned_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_issue_records",
    )
    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="returned_stock_issue_records",
    )
    return_reason = models.TextField(blank=True)
    returned_at = models.DateTimeField(blank=True, null=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("-issue_date", "-issue_number")

    def save(self, *args, **kwargs):
        if not self.issue_number:
            year = (self.issue_date or timezone.localdate()).year
            prefix = f"ISS-{year}-"
            latest = (
                IssueRecord.objects.filter(issue_number__startswith=prefix)
                .order_by("-issue_number")
                .first()
            )
            next_number = 1
            if latest:
                try:
                    next_number = int(latest.issue_number.rsplit("-", 1)[1]) + 1
                except (IndexError, ValueError):
                    next_number = latest.pk + 1
            self.issue_number = f"{prefix}{next_number:04d}"
        super().save(*args, **kwargs)

    @property
    def total_units(self):
        return self.items.filter(isactive=True).count()

    def __str__(self):
        return self.issue_number or "Issue"


class IssueItem(models.Model):
    issue = models.ForeignKey(
        IssueRecord,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product_unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="issue_items",
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("product__descript", "product_unit__serial_number")

    def save(self, *args, **kwargs):
        if self.product_unit_id and not self.product_id:
            self.product = self.product_unit.product
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.issue} - {self.product_unit.serial_number}"


class StockMovement(models.Model):
    TYPE_RECEIVED = "received"
    TYPE_RECEIVING_CANCELLED = "receiving_cancelled"
    TYPE_DELIVERED = "delivered"
    TYPE_DELIVERY_CANCELLED = "delivery_cancelled"
    TYPE_MANUAL_ADD = "manual_add"
    TYPE_MANUAL_UPDATE = "manual_update"
    TYPE_RESERVED = "reserved"
    TYPE_RESERVATION_RELEASED = "reservation_released"
    TYPE_ISSUED = "issued"
    TYPE_ISSUE_RETURNED = "issue_returned"

    MOVEMENT_TYPE_CHOICES = [
        (TYPE_RECEIVED, "Received"),
        (TYPE_RECEIVING_CANCELLED, "Receiving Cancelled"),
        (TYPE_DELIVERED, "Delivered"),
        (TYPE_DELIVERY_CANCELLED, "Delivery Cancelled"),
        (TYPE_MANUAL_ADD, "Manual Add"),
        (TYPE_MANUAL_UPDATE, "Manual Update"),
        (TYPE_RESERVED, "Reserved"),
        (TYPE_RESERVATION_RELEASED, "Reservation Released"),
        (TYPE_ISSUED, "Issued"),
        (TYPE_ISSUE_RETURNED, "Issue Returned"),
    ]

    product_unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.PROTECT,
        related_name="movements",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )
    movement_type = models.CharField(max_length=40, choices=MOVEMENT_TYPE_CHOICES)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    reason = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
    )
    movement_date = models.DateField(default=timezone.localdate)
    receiving_record = models.ForeignKey(
        ReceivingRecord,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
    )
    delivery_record = models.ForeignKey(
        DeliveryRecord,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
    )
    reservation_record = models.ForeignKey(
        ReservationRecord,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
    )
    issue_record = models.ForeignKey(
        IssueRecord,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
    )
    reference = models.CharField(max_length=150, blank=True)
    crdate = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True)

    class Meta:
        ordering = ("-movement_date", "-crdate", "-pk")
        indexes = [
            models.Index(fields=("product", "movement_date")),
            models.Index(fields=("product_unit", "movement_date")),
            models.Index(fields=("movement_type", "movement_date")),
        ]

    def save(self, *args, **kwargs):
        if self.product_unit_id and not self.product_id:
            self.product = self.product_unit.product
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product_unit}"
