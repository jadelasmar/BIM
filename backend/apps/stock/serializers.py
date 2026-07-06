from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from .models import (
    Brand,
    Category,
    DeliveryItem,
    DeliveryRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    Supplier,
)
from .services import (
    cancel_receiving_record,
    create_receiving_record,
    update_receiving_record_header,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Category name is required.")
        queryset = Category.objects.filter(name__iexact=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Category already exists.")
        return name


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "brandname")

    def validate_brandname(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Brand name is required.")
        queryset = Brand.objects.filter(brandname__iexact=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Brand already exists.")
        return name


class ProductModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.brandname", read_only=True)

    class Meta:
        model = ProductModel
        fields = ("id", "brand", "brand_name", "modelname")


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Supplier name is required.")
        queryset = Supplier.objects.filter(name__iexact=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Supplier already exists.")
        return name


class ProductSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        required=False,
        write_only=True,
    )
    model = serializers.PrimaryKeyRelatedField(
        queryset=ProductModel.objects.all(),
        required=False,
    )
    model_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_id = serializers.IntegerField(source="model.brand_id", read_only=True)
    brand_name = serializers.CharField(source="model.brand.brandname", read_only=True)
    model_name = serializers.CharField(source="model.modelname", read_only=True)
    total_units = serializers.SerializerMethodField()
    available_units = serializers.SerializerMethodField()
    reserved_units = serializers.SerializerMethodField()
    sold_units = serializers.SerializerMethodField()
    returned_units = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    stock_alert_tone = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "descript",
            "display_name",
            "category",
            "category_name",
            "model",
            "model_name",
            "brand_id",
            "brand_name",
            "brand",
            "model_name_input",
            "sku",
            "barcode",
            "image",
            "reorder_stock_level",
            "crdate",
            "isactive",
            "total_units",
            "available_units",
            "reserved_units",
            "sold_units",
            "returned_units",
            "is_low_stock",
            "stock_alert_tone",
        )
        read_only_fields = (
            "sku",
            "crdate",
            "total_units",
            "available_units",
            "reserved_units",
            "sold_units",
            "returned_units",
            "is_low_stock",
            "stock_alert_tone",
        )
        validators = []

    def get_display_name(self, obj):
        return str(obj)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        model = attrs.get("model") or getattr(self.instance, "model", None)
        brand = attrs.get("brand")
        model_name = attrs.get("model_name_input", "").strip()

        if not model and not (brand and model_name):
            raise serializers.ValidationError(
                {
                    "model_name_input": (
                        "Select an existing model or enter a brand and model name."
                    )
                }
            )

        return attrs

    def _save_with_model_name(self, attrs, save_func):
        brand = attrs.pop("brand", None)
        model_name = attrs.pop("model_name_input", "").strip()
        if not attrs.get("model") and brand and model_name:
            attrs["model"], _created = ProductModel.objects.get_or_create(
                brand=brand,
                modelname=model_name,
            )
        return save_func(attrs)

    def create(self, validated_data):
        return self._save_with_model_name(
            validated_data,
            lambda attrs: super(ProductSerializer, self).create(attrs),
        )

    def update(self, instance, validated_data):
        return self._save_with_model_name(
            validated_data,
            lambda attrs: super(ProductSerializer, self).update(instance, attrs),
        )

    def _count(self, obj, annotated_name, fallback_name):
        return getattr(obj, annotated_name, getattr(obj, fallback_name))

    def get_total_units(self, obj):
        return self._count(obj, "api_total_units", "total_units")

    def get_available_units(self, obj):
        return self._count(obj, "api_available_units", "available_units")

    def get_reserved_units(self, obj):
        return self._count(obj, "api_reserved_units", "reserved_units")

    def get_sold_units(self, obj):
        return self._count(obj, "api_sold_units", "sold_units")

    def get_returned_units(self, obj):
        return self._count(obj, "api_returned_units", "returned_units")

    def get_is_low_stock(self, obj):
        available_units = self.get_available_units(obj)
        return (
            obj.reorder_stock_level > 0
            and available_units > 0
            and available_units <= obj.reorder_stock_level
        )

    def get_stock_alert_tone(self, obj):
        if self.get_is_low_stock(obj):
            return "warning"
        return "normal"


class ProductUnitSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_barcode = serializers.CharField(source="product.barcode", read_only=True)
    category_id = serializers.IntegerField(source="product.category_id", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)
    brand_id = serializers.IntegerField(source="product.model.brand_id", read_only=True)
    brand_name = serializers.CharField(
        source="product.model.brand.brandname",
        read_only=True,
    )
    model_name = serializers.CharField(source="product.model.modelname", read_only=True)
    supplier_name = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = ProductUnit
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_barcode",
            "category_id",
            "category_name",
            "brand_id",
            "brand_name",
            "model_name",
            "serial_number",
            "status",
            "status_label",
            "supplier",
            "supplier_name",
            "cost",
            "selling_price",
            "purchase_date",
            "sold_date",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = ("crdate", "sold_date")

    def get_product_name(self, obj):
        return str(obj.product)

    def get_status_label(self, obj):
        return obj.get_status_display()

    def get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else None


class DeliveryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )

    class Meta:
        model = DeliveryItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "serial_number",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class DeliveryRecordSerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True, read_only=True)
    total_units = serializers.SerializerMethodField()
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        allow_empty=False,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_username",
        read_only=True,
    )

    class Meta:
        model = DeliveryRecord
        fields = (
            "id",
            "delivery_number",
            "customer_name",
            "receiver_name",
            "delivery_date",
            "notes",
            "status",
            "created_by",
            "created_by_name",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "delivery_number",
            "created_by",
            "created_by_name",
            "total_units",
            "items",
            "crdate",
        )

    def get_total_units(self, obj):
        return obj.total_units

    def validate_unit_ids(self, value):
        unique_ids = list(dict.fromkeys(value))
        units = ProductUnit.objects.filter(pk__in=unique_ids, isactive=True)
        units_by_id = {unit.pk: unit for unit in units}
        missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]
        unavailable_units = [
            unit.serial_number
            for unit in units_by_id.values()
            if unit.status != ProductUnit.STATUS_AVAILABLE
        ]

        if missing_ids:
            raise serializers.ValidationError("One or more stock units were not found.")
        if unavailable_units:
            raise serializers.ValidationError(
                "Only available stock units can be delivered."
            )

        return unique_ids

    def create(self, validated_data):
        unit_ids = validated_data.pop("unit_ids")
        request = self.context.get("request")

        with transaction.atomic():
            delivery = DeliveryRecord.objects.create(
                **validated_data,
                created_by=request.user if request else None,
            )
            units = (
                ProductUnit.objects.select_related("product")
                .filter(pk__in=unit_ids)
                .order_by("product__descript", "serial_number")
            )
            for unit in units:
                DeliveryItem.objects.create(
                    delivery=delivery,
                    product_unit=unit,
                    product=unit.product,
                )
                unit.status = ProductUnit.STATUS_SOLD
                unit.sold_date = delivery.delivery_date
                unit.save(update_fields=("status", "sold_date"))

        return delivery


class ReceivingItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_unit_serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )

    class Meta:
        model = ReceivingItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "product_unit_serial_number",
            "quantity",
            "serial_number",
            "cost",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class ReceivingItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_unit = serializers.PrimaryKeyRelatedField(
        queryset=ProductUnit.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    serial_numbers = serializers.ListField(
        child=serializers.CharField(allow_blank=False, trim_whitespace=True),
        required=False,
        allow_empty=False,
    )
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        serial_numbers = attrs.get("serial_numbers") or []
        product_unit = attrs.get("product_unit")
        quantity = attrs.get("quantity", 1)

        if product_unit and serial_numbers:
            raise serializers.ValidationError(
                "Use either product_unit or serial_numbers, not both."
            )
        if product_unit:
            attrs["product"] = product_unit.product
            attrs["quantity"] = 1
        if serial_numbers and len(serial_numbers) != quantity:
            raise serializers.ValidationError(
                "Serial number count must match quantity."
            )
        if len(serial_numbers) != len(set(serial_numbers)):
            raise serializers.ValidationError("Serial numbers must be unique.")

        return attrs


class ReceivingRecordSerializer(serializers.ModelSerializer):
    items = ReceivingItemSerializer(many=True, read_only=True)
    item_inputs = ReceivingItemInputSerializer(
        many=True,
        write_only=True,
        required=True,
        allow_empty=False,
    )
    total_quantity = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_username",
        read_only=True,
    )

    class Meta:
        model = ReceivingRecord
        fields = (
            "id",
            "receiving_number",
            "supplier",
            "supplier_name",
            "reference_number",
            "received_date",
            "notes",
            "status",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
            "created_by",
            "created_by_name",
            "total_quantity",
            "item_inputs",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "receiving_number",
            "status",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
            "created_by",
            "created_by_name",
            "total_quantity",
            "items",
            "crdate",
        )

    def get_total_quantity(self, obj):
        return obj.total_quantity

    def create(self, validated_data):
        item_inputs = validated_data.pop("item_inputs")
        request = self.context.get("request")
        try:
            return create_receiving_record(
                items=item_inputs,
                created_by=request.user if request else None,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class ReceivingItemCorrectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class ReceivingRecordCorrectionSerializer(serializers.ModelSerializer):
    items = ReceivingItemCorrectionSerializer(many=True, required=False)

    class Meta:
        model = ReceivingRecord
        fields = (
            "supplier",
            "reference_number",
            "received_date",
            "notes",
            "items",
        )
        extra_kwargs = {
            "supplier": {"required": False, "allow_null": True},
            "reference_number": {"required": False, "allow_blank": True},
            "received_date": {"required": False},
            "notes": {"required": False, "allow_blank": True},
        }

    def update(self, instance, validated_data):
        item_updates = validated_data.pop("items", [])
        try:
            return update_receiving_record_header(
                instance,
                supplier=validated_data.get("supplier")
                if "supplier" in validated_data
                else instance.supplier,
                reference_number=validated_data.get("reference_number")
                if "reference_number" in validated_data
                else instance.reference_number,
                received_date=validated_data.get("received_date")
                if "received_date" in validated_data
                else instance.received_date,
                notes=validated_data.get("notes")
                if "notes" in validated_data
                else instance.notes,
                items=item_updates,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def to_representation(self, instance):
        return ReceivingRecordSerializer(instance, context=self.context).data


class ReceivingRecordCancelSerializer(serializers.Serializer):
    cancel_reason = serializers.CharField(required=True, allow_blank=False)

    def save(self, **kwargs):
        receiving = self.context["receiving"]
        request = self.context.get("request")
        try:
            return cancel_receiving_record(
                receiving,
                cancelled_by=request.user if request else None,
                cancel_reason=self.validated_data["cancel_reason"],
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
