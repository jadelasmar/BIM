from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import (
    Brand,
    Category,
    Client,
    ClientReturnItem,
    ClientReturnRecord,
    DeliveryItem,
    DeliveryRecord,
    IssueItem,
    IssueRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    RepairItem,
    RepairRecord,
    ReservationItem,
    ReservationRecord,
    StockMovement,
    Supplier,
)
from .services import (
    cancel_delivery_record,
    cancel_receiving_record,
    create_client_return_record,
    create_delivery_record,
    create_issue_record,
    create_receiving_record,
    create_repair_record,
    create_reservation_record,
    release_reservation_record,
    resolve_repair_record,
    return_issue_record,
    update_delivery_record_header,
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
        fields = (
            "id",
            "name",
            "contact_person",
            "phone",
            "email",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = ("crdate",)

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


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "contact_person",
            "phone",
            "email",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = ("crdate",)

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Client name is required.")
        queryset = Client.objects.filter(name__iexact=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Client already exists.")
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
    issued_units = serializers.SerializerMethodField()
    sold_units = serializers.SerializerMethodField()
    repair_units = serializers.SerializerMethodField()
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
            "issued_units",
            "sold_units",
            "repair_units",
            "is_low_stock",
            "stock_alert_tone",
        )
        read_only_fields = (
            "sku",
            "crdate",
            "total_units",
            "available_units",
            "reserved_units",
            "issued_units",
            "sold_units",
            "repair_units",
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
            errors = {}
            if not brand:
                errors["brand"] = "Brand is required to save a Model name."
            if not model_name:
                errors["model_name_input"] = "Enter a Model name."
            raise serializers.ValidationError(errors)

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

    def get_issued_units(self, obj):
        return self._count(obj, "api_issued_units", "issued_units")

    def get_sold_units(self, obj):
        return self._count(obj, "api_sold_units", "sold_units")

    def get_repair_units(self, obj):
        return self._count(obj, "api_repair_units", "repair_units")

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


class StockMovementSerializer(serializers.ModelSerializer):
    movement_type_label = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )
    performed_by_name = serializers.SerializerMethodField()
    receiving_number = serializers.SerializerMethodField()
    delivery_number = serializers.SerializerMethodField()
    reservation = serializers.IntegerField(source="reservation_record_id", read_only=True)
    reservation_number = serializers.SerializerMethodField()
    issue = serializers.IntegerField(source="issue_record_id", read_only=True)
    issue_number = serializers.SerializerMethodField()
    repair = serializers.IntegerField(source="repair_record_id", read_only=True)
    repair_number = serializers.SerializerMethodField()
    client_return = serializers.IntegerField(source="client_return_record_id", read_only=True)
    client_return_number = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "serial_number",
            "movement_type",
            "movement_type_label",
            "from_status",
            "to_status",
            "reason",
            "notes",
            "performed_by",
            "performed_by_name",
            "movement_date",
            "receiving_record",
            "receiving_number",
            "delivery_record",
            "delivery_number",
            "reservation",
            "reservation_record",
            "reservation_number",
            "issue",
            "issue_record",
            "issue_number",
            "repair",
            "repair_record",
            "repair_number",
            "client_return",
            "client_return_record",
            "client_return_number",
            "reference",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)

    def get_performed_by_name(self, obj):
        return obj.performed_by.get_username() if obj.performed_by else ""

    def get_receiving_number(self, obj):
        return obj.receiving_record.receiving_number if obj.receiving_record else ""

    def get_delivery_number(self, obj):
        return obj.delivery_record.delivery_number if obj.delivery_record else ""

    def get_reservation_number(self, obj):
        return obj.reservation_record.reservation_number if obj.reservation_record else ""

    def get_issue_number(self, obj):
        return obj.issue_record.issue_number if obj.issue_record else ""

    def get_repair_number(self, obj):
        return obj.repair_record.repair_number if obj.repair_record else ""

    def get_client_return_number(self, obj):
        return obj.client_return_record.return_number if obj.client_return_record else ""


class DeliveryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )
    product_unit_status = serializers.CharField(
        source="product_unit.status",
        read_only=True,
    )
    product_unit_status_label = serializers.CharField(
        source="product_unit.get_status_display",
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
            "product_unit_status",
            "product_unit_status_label",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class ReservationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )
    product_unit_status = serializers.CharField(
        source="product_unit.status",
        read_only=True,
    )
    product_unit_status_label = serializers.CharField(
        source="product_unit.get_status_display",
        read_only=True,
    )

    class Meta:
        model = ReservationItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "serial_number",
            "product_unit_status",
            "product_unit_status_label",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class ReservationRecordSerializer(serializers.ModelSerializer):
    items = ReservationItemSerializer(many=True, read_only=True)
    total_units = serializers.SerializerMethodField()
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        allow_empty=False,
    )
    reserved_by_name = serializers.CharField(
        source="reserved_by.get_username",
        read_only=True,
    )
    released_by_name = serializers.CharField(
        source="released_by.get_username",
        read_only=True,
        default="",
    )

    class Meta:
        model = ReservationRecord
        fields = (
            "id",
            "reservation_number",
            "reserved_for",
            "reason",
            "expected_release_date",
            "notes",
            "status",
            "reserved_by",
            "reserved_by_name",
            "reserved_at",
            "release_reason",
            "released_by",
            "released_by_name",
            "released_at",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "reservation_number",
            "status",
            "reserved_by",
            "reserved_by_name",
            "reserved_at",
            "release_reason",
            "released_by",
            "released_by_name",
            "released_at",
            "total_units",
            "items",
            "crdate",
        )

    def get_total_units(self, obj):
        return obj.total_units

    def create(self, validated_data):
        unit_ids = validated_data.pop("unit_ids")
        request = self.context.get("request")
        try:
            return create_reservation_record(
                unit_ids=unit_ids,
                reserved_by=request.user if request else None,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class ReservationReleaseSerializer(serializers.Serializer):
    release_reason = serializers.CharField(required=True, allow_blank=False)

    def save(self, **kwargs):
        reservation = self.context["reservation"]
        request = self.context.get("request")
        try:
            return release_reservation_record(
                reservation,
                released_by=request.user if request else None,
                release_reason=self.validated_data["release_reason"],
                cancel=self.context.get("cancel", False),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class IssueItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )
    product_unit_status = serializers.CharField(
        source="product_unit.status",
        read_only=True,
    )
    product_unit_status_label = serializers.CharField(
        source="product_unit.get_status_display",
        read_only=True,
    )

    class Meta:
        model = IssueItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "serial_number",
            "product_unit_status",
            "product_unit_status_label",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class IssueRecordSerializer(serializers.ModelSerializer):
    items = IssueItemSerializer(many=True, read_only=True)
    total_units = serializers.SerializerMethodField()
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        allow_empty=False,
    )
    issued_by_name = serializers.CharField(
        source="issued_by.get_username",
        read_only=True,
    )
    returned_by_name = serializers.CharField(
        source="returned_by.get_username",
        read_only=True,
        default="",
    )

    class Meta:
        model = IssueRecord
        fields = (
            "id",
            "issue_number",
            "issued_to",
            "department",
            "branch_or_site",
            "reason",
            "issue_date",
            "expected_return_date",
            "returned_date",
            "notes",
            "status",
            "issued_by",
            "issued_by_name",
            "returned_by",
            "returned_by_name",
            "return_reason",
            "returned_at",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "issue_number",
            "returned_date",
            "status",
            "issued_by",
            "issued_by_name",
            "returned_by",
            "returned_by_name",
            "return_reason",
            "returned_at",
            "total_units",
            "items",
            "crdate",
        )

    def get_total_units(self, obj):
        return obj.total_units

    def create(self, validated_data):
        unit_ids = validated_data.pop("unit_ids")
        request = self.context.get("request")
        try:
            return create_issue_record(
                unit_ids=unit_ids,
                issued_by=request.user if request else None,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class IssueReturnSerializer(serializers.Serializer):
    return_reason = serializers.CharField(required=True, allow_blank=False)
    returned_date = serializers.DateField(required=False)

    def save(self, **kwargs):
        issue = self.context["issue"]
        request = self.context.get("request")
        try:
            return return_issue_record(
                issue,
                returned_by=request.user if request else None,
                return_reason=self.validated_data["return_reason"],
                returned_date=self.validated_data.get("returned_date"),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class RepairItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )
    product_unit_status = serializers.CharField(
        source="product_unit.status",
        read_only=True,
    )
    product_unit_status_label = serializers.CharField(
        source="product_unit.get_status_display",
        read_only=True,
    )

    class Meta:
        model = RepairItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "serial_number",
            "product_unit_status",
            "product_unit_status_label",
            "notes",
            "resolution_notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class RepairRecordSerializer(serializers.ModelSerializer):
    items = RepairItemSerializer(many=True, read_only=True)
    total_units = serializers.SerializerMethodField()
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        allow_empty=False,
    )
    sent_by_name = serializers.CharField(
        source="sent_by.get_username",
        read_only=True,
    )
    resolved_by_name = serializers.CharField(
        source="resolved_by.get_username",
        read_only=True,
        default="",
    )

    class Meta:
        model = RepairRecord
        fields = (
            "id",
            "repair_number",
            "repair_reason",
            "reported_by_name",
            "repair_location",
            "technician",
            "repair_date",
            "expected_resolution_date",
            "resolved_date",
            "resolution",
            "resolution_notes",
            "notes",
            "status",
            "sent_by",
            "sent_by_name",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "repair_number",
            "resolved_date",
            "resolution",
            "resolution_notes",
            "status",
            "sent_by",
            "sent_by_name",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "total_units",
            "items",
            "crdate",
        )

    def get_total_units(self, obj):
        return obj.total_units

    def create(self, validated_data):
        unit_ids = validated_data.pop("unit_ids")
        request = self.context.get("request")
        try:
            return create_repair_record(
                unit_ids=unit_ids,
                sent_by=request.user if request else None,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class RepairResolveSerializer(serializers.Serializer):
    resolution = serializers.ChoiceField(
        choices=(
            ProductUnit.STATUS_AVAILABLE,
            ProductUnit.STATUS_INACTIVE,
        )
    )
    resolution_notes = serializers.CharField(required=True, allow_blank=False)
    resolved_date = serializers.DateField(required=False)

    def save(self, **kwargs):
        repair = self.context["repair"]
        request = self.context.get("request")
        try:
            return resolve_repair_record(
                repair,
                resolved_by=request.user if request else None,
                resolution=self.validated_data["resolution"],
                resolution_notes=self.validated_data["resolution_notes"],
                resolved_date=self.validated_data.get("resolved_date"),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class ClientReturnItemSerializer(serializers.ModelSerializer):
    delivery = serializers.IntegerField(source="delivery_item.delivery_id", read_only=True)
    delivery_number = serializers.CharField(
        source="delivery_item.delivery.delivery_number",
        read_only=True,
    )
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    serial_number = serializers.CharField(
        source="product_unit.serial_number",
        read_only=True,
    )
    product_unit_status = serializers.CharField(
        source="product_unit.status",
        read_only=True,
    )
    product_unit_status_label = serializers.CharField(
        source="product_unit.get_status_display",
        read_only=True,
    )

    class Meta:
        model = ClientReturnItem
        fields = (
            "id",
            "delivery_item",
            "delivery",
            "delivery_number",
            "product",
            "product_name",
            "product_sku",
            "product_unit",
            "serial_number",
            "product_unit_status",
            "product_unit_status_label",
            "notes",
            "crdate",
            "isactive",
        )
        read_only_fields = fields

    def get_product_name(self, obj):
        return str(obj.product)


class ClientReturnRecordSerializer(serializers.ModelSerializer):
    items = ClientReturnItemSerializer(many=True, read_only=True)
    total_units = serializers.SerializerMethodField()
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        allow_empty=False,
    )
    delivery_number = serializers.CharField(
        source="delivery.delivery_number",
        read_only=True,
        default="",
    )
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    client_name = serializers.CharField(source="client.name", read_only=True, default="")
    received_by_name = serializers.CharField(
        source="received_by.get_username",
        read_only=True,
        default="",
    )

    class Meta:
        model = ClientReturnRecord
        fields = (
            "id",
            "return_number",
            "delivery",
            "delivery_number",
            "client",
            "client_name",
            "customer_name",
            "received_from",
            "return_date",
            "reason",
            "resolution",
            "notes",
            "received_by",
            "received_by_name",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "return_number",
            "delivery_number",
            "client_name",
            "received_by",
            "received_by_name",
            "total_units",
            "items",
            "crdate",
        )
        extra_kwargs = {
            "customer_name": {"required": False, "allow_blank": True},
        }

    def get_total_units(self, obj):
        return obj.total_units

    def create(self, validated_data):
        unit_ids = validated_data.pop("unit_ids")
        request = self.context.get("request")
        try:
            return create_client_return_record(
                unit_ids=unit_ids,
                received_by=request.user if request else None,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


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
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    client_name = serializers.CharField(source="client.name", read_only=True, default="")

    class Meta:
        model = DeliveryRecord
        fields = (
            "id",
            "delivery_number",
            "client",
            "client_name",
            "customer_name",
            "receiver_name",
            "delivery_date",
            "notes",
            "status",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
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
            "client_name",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
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
        return create_delivery_record(
            unit_ids=unit_ids,
            created_by=request.user if request else None,
            **validated_data,
        )


class DeliveryItemCorrectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)


class DeliveryRecordCorrectionSerializer(serializers.ModelSerializer):
    items = DeliveryItemCorrectionSerializer(many=True, required=False)

    class Meta:
        model = DeliveryRecord
        fields = (
            "customer_name",
            "receiver_name",
            "delivery_date",
            "notes",
            "items",
        )
        extra_kwargs = {
            "customer_name": {"required": False, "allow_blank": False},
            "receiver_name": {"required": False, "allow_blank": True},
            "delivery_date": {"required": False},
            "notes": {"required": False, "allow_blank": True},
        }

    def update(self, instance, validated_data):
        item_updates = validated_data.pop("items", [])
        try:
            return update_delivery_record_header(
                instance,
                customer_name=validated_data.get("customer_name")
                if "customer_name" in validated_data
                else instance.customer_name,
                receiver_name=validated_data.get("receiver_name")
                if "receiver_name" in validated_data
                else instance.receiver_name,
                delivery_date=validated_data.get("delivery_date")
                if "delivery_date" in validated_data
                else instance.delivery_date,
                notes=validated_data.get("notes")
                if "notes" in validated_data
                else instance.notes,
                items=item_updates,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def to_representation(self, instance):
        return DeliveryRecordSerializer(instance, context=self.context).data


class DeliveryRecordCancelSerializer(serializers.Serializer):
    cancel_reason = serializers.CharField(required=True, allow_blank=False)

    def save(self, **kwargs):
        delivery = self.context["delivery"]
        request = self.context.get("request")
        try:
            return cancel_delivery_record(
                delivery,
                cancelled_by=request.user if request else None,
                cancel_reason=self.validated_data["cancel_reason"],
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


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
        extra_kwargs = {
            "customer_name": {"required": False, "allow_blank": True},
        }

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
