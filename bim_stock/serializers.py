from rest_framework import serializers
from django.db import transaction

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


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ("id", "name")


class CategorySerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="type.name", read_only=True)

    class Meta:
        model = Category
        fields = ("id", "type", "type_name", "name")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "brandname")


class ProductModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.brandname", read_only=True)

    class Meta:
        model = ProductModel
        fields = ("id", "brand", "brand_name", "modelname")


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name")


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
    type_id = serializers.IntegerField(source="category.type_id", read_only=True)
    type_name = serializers.CharField(source="category.type.name", read_only=True)
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
    is_critical_stock = serializers.SerializerMethodField()
    stock_alert_tone = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "descript",
            "printed",
            "display_name",
            "category",
            "category_name",
            "type_id",
            "type_name",
            "model",
            "model_name",
            "brand_id",
            "brand_name",
            "brand",
            "model_name_input",
            "sku",
            "barcode",
            "image",
            "minimum_stock_level",
            "reorder_stock_level",
            "crdate",
            "isactive",
            "total_units",
            "available_units",
            "reserved_units",
            "sold_units",
            "returned_units",
            "is_low_stock",
            "is_critical_stock",
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
            "is_critical_stock",
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
        return obj.reorder_stock_level > 0 and self.get_available_units(obj) <= obj.reorder_stock_level

    def get_is_critical_stock(self, obj):
        return obj.minimum_stock_level > 0 and self.get_available_units(obj) <= obj.minimum_stock_level

    def get_stock_alert_tone(self, obj):
        if self.get_is_critical_stock(obj):
            return "critical"
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
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
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
