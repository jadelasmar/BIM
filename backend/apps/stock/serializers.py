from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from .models import (
    Brand,
    Category,
    Client,
    ClientReturnItem,
    ClientReturnRecord,
    DeliveryItem,
    DeliveryRecord,
    InternalParty,
    IssueItem,
    IssueRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingItem,
    ReceivingRecord,
    RemovalItem,
    RemovalRecord,
    RepairItem,
    RepairRecord,
    ReservationItem,
    ReservationRecord,
    StockMovement,
    Supplier,
)
from .services import (
    cancel_client_return_record,
    cancel_delivery_record,
    cancel_receiving_record,
    create_client_return_record,
    create_delivery_record,
    create_issue_record,
    create_receiving_record,
    create_removal_record,
    create_repair_record,
    create_reservation_record,
    release_reservation_record,
    resolve_repair_record,
    return_issue_record,
    update_client_return_record_header,
    update_delivery_record_header,
    update_issue_record_header,
    update_receiving_record_header,
    update_repair_record_header,
    update_reservation_record_header,
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


class InternalPartySerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = InternalParty
        fields = ("id", "kind", "kind_label", "name")
        read_only_fields = fields


def _party_payload(party_type, party):
    """Compact {type, id, name, kind?} used by detail/list views to render a
    party as a link (client/supplier) or a plain tagged name (internal)."""
    if party is None:
        return None
    payload = {"type": party_type, "id": party.pk, "name": party.name}
    if party_type == "internal":
        payload["kind"] = party.kind
        payload["kind_label"] = party.get_kind_display()
    return payload


class ProductSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
    )
    category_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        required=False,
        write_only=True,
    )
    brand_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
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
    removed_units = serializers.SerializerMethodField()
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
            "category_name_input",
            "model",
            "model_name",
            "brand_id",
            "brand_name",
            "brand",
            "brand_name_input",
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
            "removed_units",
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
            "removed_units",
            "is_low_stock",
            "stock_alert_tone",
        )
        validators = []

    def get_display_name(self, obj):
        return str(obj)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        category = attrs.get("category") or getattr(self.instance, "category", None)
        category_name = attrs.get("category_name_input", "").strip()
        model = attrs.get("model") or getattr(self.instance, "model", None)
        brand = attrs.get("brand")
        brand_name = attrs.get("brand_name_input", "").strip()
        model_name = attrs.get("model_name_input", "").strip()

        errors = {}
        if not category and not category_name:
            errors["category"] = "Select or enter a Category."
        if not model and not ((brand or brand_name) and model_name):
            if not brand and not brand_name:
                errors["brand"] = "Brand is required to save a Model name."
            if not model_name:
                errors["model_name_input"] = "Enter a Model name."
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def _save_with_model_name(self, attrs, save_func):
        with transaction.atomic():
            category_name = attrs.pop("category_name_input", "").strip()
            if not attrs.get("category") and category_name:
                attrs["category"], _created = Category.objects.get_or_create(name=category_name)

            brand = attrs.pop("brand", None)
            brand_name = attrs.pop("brand_name_input", "").strip()
            if not brand and brand_name:
                brand, _created = Brand.objects.get_or_create(brandname=brand_name)

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

    def get_removed_units(self, obj):
        return self._count(obj, "api_removed_units", "removed_units")

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
    removal = serializers.IntegerField(source="removal_record_id", read_only=True)
    removal_number = serializers.SerializerMethodField()

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
            "removal",
            "removal_record",
            "removal_number",
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

    def get_removal_number(self, obj):
        return obj.removal_record.removal_number if obj.removal_record else ""


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
            "sale_price",
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
    reserved_for_type = serializers.ChoiceField(
        choices=ReservationRecord.RESERVED_FOR_TYPE_CHOICES,
    )
    reserved_for_client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    reserved_for_supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    reserved_for_internal = serializers.PrimaryKeyRelatedField(
        queryset=InternalParty.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    internal_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    internal_kind_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    reserved_for_party = serializers.SerializerMethodField()
    delivery = serializers.SerializerMethodField()
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
            "reserved_for_type",
            "reserved_for_client",
            "reserved_for_supplier",
            "reserved_for_internal",
            "internal_name_input",
            "internal_kind_input",
            "reserved_for_party",
            "delivery",
            "reason",
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
            "reserved_for",
            "reserved_for_party",
            "delivery",
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

    def get_delivery(self, obj):
        # The delivery this reservation was turned into, if any (newest first
        # in case an earlier one was cancelled).
        deliveries = sorted(obj.deliveries.all(), key=lambda row: row.pk, reverse=True)
        if not deliveries:
            return None
        latest = deliveries[0]
        return {
            "id": latest.pk,
            "delivery_number": latest.delivery_number,
            "status": latest.status,
        }

    def get_reserved_for_party(self, obj):
        party = _party_payload(
            obj.reserved_for_type,
            {
                ReservationRecord.TYPE_CLIENT: obj.reserved_for_client,
                ReservationRecord.TYPE_SUPPLIER: obj.reserved_for_supplier,
                ReservationRecord.TYPE_INTERNAL: obj.reserved_for_internal,
            }.get(obj.reserved_for_type),
        )
        # The party row can be gone (SET_NULL) or never linked; fall back to
        # the name snapshot so the record still shows who it was for.
        return party or {"type": obj.reserved_for_type, "id": None, "name": obj.reserved_for}

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


class ReservationRecordCorrectionSerializer(serializers.ModelSerializer):
    reserved_for_type = serializers.ChoiceField(
        choices=ReservationRecord.RESERVED_FOR_TYPE_CHOICES,
        required=False,
    )
    reserved_for_client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    reserved_for_supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    reserved_for_internal = serializers.PrimaryKeyRelatedField(
        queryset=InternalParty.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    internal_name_input = serializers.CharField(required=False, allow_blank=True)
    internal_kind_input = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ReservationRecord
        fields = (
            "reserved_for_type",
            "reserved_for_client",
            "reserved_for_supplier",
            "reserved_for_internal",
            "internal_name_input",
            "internal_kind_input",
            "reason",
            "notes",
        )
        extra_kwargs = {
            "reason": {"required": False, "allow_blank": True},
            "notes": {"required": False, "allow_blank": True},
        }

    def update(self, instance, validated_data):
        try:
            return update_reservation_record_header(instance, **validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def to_representation(self, instance):
        return ReservationRecordSerializer(instance, context=self.context).data


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
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=InternalParty.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    assigned_to_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    assigned_to_kind_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    assigned_to_party = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
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
            "assigned_to",
            "assigned_to_name_input",
            "assigned_to_kind_input",
            "assigned_to_party",
            "reason",
            "issue_date",
            "expected_return_date",
            "is_overdue",
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
            "issued_to",
            "assigned_to_party",
            "is_overdue",
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

    def get_assigned_to_party(self, obj):
        party = _party_payload("internal", obj.assigned_to)
        return party or {"type": "internal", "id": None, "name": obj.issued_to}

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


class IssueRecordCorrectionSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=InternalParty.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    assigned_to_name_input = serializers.CharField(required=False, allow_blank=True)
    assigned_to_kind_input = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = IssueRecord
        fields = (
            "assigned_to",
            "assigned_to_name_input",
            "assigned_to_kind_input",
            "reason",
            "issue_date",
            "expected_return_date",
            "notes",
        )
        extra_kwargs = {
            "reason": {"required": False, "allow_blank": True},
            "issue_date": {"required": False},
            "expected_return_date": {"required": False, "allow_null": True},
            "notes": {"required": False, "allow_blank": True},
        }

    def update(self, instance, validated_data):
        try:
            return update_issue_record_header(instance, **validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def to_representation(self, instance):
        return IssueRecordSerializer(instance, context=self.context).data


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
    vendor = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(isactive=True),
        required=True,
        allow_null=False,
    )
    vendor_name = serializers.CharField(source="vendor.name", read_only=True, default="")
    source = serializers.ChoiceField(
        choices=RepairRecord.SOURCE_CHOICES,
        required=False,
        default=RepairRecord.SOURCE_INTERNAL_STOCK,
    )
    source_label = serializers.CharField(source="get_source_display", read_only=True)
    source_client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    source_internal = serializers.PrimaryKeyRelatedField(
        queryset=InternalParty.objects.filter(isactive=True),
        required=False,
        allow_null=True,
    )
    source_internal_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    source_internal_kind_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    source_party = serializers.SerializerMethodField()
    return_delivery_id = serializers.SerializerMethodField()
    return_delivery_number = serializers.SerializerMethodField()
    client_return_id = serializers.IntegerField(read_only=True)
    sent_by_name = serializers.CharField(
        source="sent_by.get_username",
        read_only=True,
    )
    resolved_by_name = serializers.CharField(
        source="resolved_by.get_username",
        read_only=True,
        default="",
    )
    client_return_number = serializers.CharField(
        source="client_return.return_number",
        read_only=True,
        default="",
    )

    class Meta:
        model = RepairRecord
        fields = (
            "id",
            "repair_number",
            "repair_reason",
            "vendor",
            "vendor_name",
            "source",
            "source_label",
            "source_client",
            "source_internal",
            "source_internal_name_input",
            "source_internal_kind_input",
            "source_party",
            "return_delivery_id",
            "return_delivery_number",
            "client_return_id",
            "repair_date",
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
            "client_return",
            "client_return_number",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "repair_number",
            "vendor_name",
            "source_label",
            "source_party",
            "return_delivery_id",
            "return_delivery_number",
            "client_return_id",
            "resolved_date",
            "resolution",
            "resolution_notes",
            "status",
            "sent_by",
            "sent_by_name",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "client_return",
            "client_return_number",
            "total_units",
            "items",
            "crdate",
        )

    def get_total_units(self, obj):
        return obj.total_units

    def _return_delivery(self, obj):
        return obj.return_deliveries.filter(is_warranty_return=True).order_by("-pk").first()

    def get_return_delivery_id(self, obj):
        delivery = self._return_delivery(obj)
        return delivery.pk if delivery else None

    def get_return_delivery_number(self, obj):
        delivery = self._return_delivery(obj)
        return delivery.delivery_number if delivery else ""

    def get_source_party(self, obj):
        if obj.source == RepairRecord.SOURCE_CLIENT_RETURN:
            return _party_payload("client", obj.source_client)
        if obj.source == RepairRecord.SOURCE_INTERNAL_PARTY:
            return _party_payload("internal", obj.source_internal)
        return None

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


class RepairRecordCorrectionSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(isactive=True),
        required=False,
        allow_null=False,
    )

    class Meta:
        model = RepairRecord
        fields = (
            "repair_reason",
            "vendor",
            "repair_date",
            "notes",
        )
        extra_kwargs = {
            "repair_reason": {"required": False, "allow_blank": False},
            "repair_date": {"required": False},
            "notes": {"required": False, "allow_blank": True},
        }

    def update(self, instance, validated_data):
        try:
            return update_repair_record_header(instance, **validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def to_representation(self, instance):
        return RepairRecordSerializer(instance, context=self.context).data


class RepairResolveSerializer(serializers.Serializer):
    resolution = serializers.ChoiceField(
        choices=(
            ProductUnit.STATUS_AVAILABLE,
            ProductUnit.STATUS_INACTIVE,
            ProductUnit.STATUS_SOLD,
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


class RemovalItemSerializer(serializers.ModelSerializer):
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
        model = RemovalItem
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


class RemovalRecordSerializer(serializers.ModelSerializer):
    items = RemovalItemSerializer(many=True, read_only=True)
    total_units = serializers.SerializerMethodField()
    unit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        allow_empty=False,
    )
    reason_label = serializers.CharField(source="get_reason_display", read_only=True)
    removed_by_name = serializers.CharField(
        source="removed_by.get_username",
        read_only=True,
        default="",
    )

    class Meta:
        model = RemovalRecord
        fields = (
            "id",
            "removal_number",
            "reason",
            "reason_label",
            "removal_date",
            "notes",
            "removed_by",
            "removed_by_name",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "removal_number",
            "reason_label",
            "removed_by",
            "removed_by_name",
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
            return create_removal_record(
                unit_ids=unit_ids,
                removed_by=request.user if request else None,
                **validated_data,
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
    # The client comes from the units' latest delivery. A client sent here is
    # only cross-checked against it by the service (mismatch is rejected).
    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(isactive=True),
        required=False,
        allow_null=True,
        write_only=True,
    )
    client_id = serializers.IntegerField(read_only=True)
    client_name = serializers.CharField(source="client.name", read_only=True, default="")
    repair_vendor = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(isactive=True),
        required=False,
        allow_null=True,
        write_only=True,
    )
    received_by_name = serializers.CharField(
        source="received_by.get_username",
        read_only=True,
        default="",
    )
    cancelled_by_name = serializers.CharField(
        source="cancelled_by.get_username",
        read_only=True,
        default="",
    )
    repair_record_id = serializers.SerializerMethodField()
    repair_record_number = serializers.SerializerMethodField()
    repair_vendor_id = serializers.SerializerMethodField()
    repair_vendor_name = serializers.SerializerMethodField()

    class Meta:
        model = ClientReturnRecord
        fields = (
            "id",
            "return_number",
            "delivery",
            "delivery_number",
            "client",
            "client_id",
            "client_name",
            "customer_name",
            "received_from",
            "return_date",
            "reason",
            "resolution",
            "repair_vendor",
            "notes",
            "status",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
            "cancelled_by_name",
            "received_by",
            "received_by_name",
            "repair_record_id",
            "repair_record_number",
            "repair_vendor_id",
            "repair_vendor_name",
            "total_units",
            "unit_ids",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "return_number",
            "delivery_number",
            "client_id",
            "client_name",
            "customer_name",
            "status",
            "cancel_reason",
            "cancelled_at",
            "cancelled_by",
            "cancelled_by_name",
            "received_by",
            "received_by_name",
            "repair_record_id",
            "repair_record_number",
            "repair_vendor_id",
            "repair_vendor_name",
            "total_units",
            "items",
            "crdate",
        )

    def get_total_units(self, obj):
        return obj.total_units

    def validate(self, attrs):
        if (
            attrs.get("resolution") == ClientReturnRecord.RESOLUTION_REPAIR
            and not attrs.get("repair_vendor")
        ):
            raise serializers.ValidationError(
                {"repair_vendor": "Choose the repair vendor for units going to repair."}
            )
        return attrs

    def get_repair_vendor_id(self, obj):
        repair = self._latest_repair(obj)
        return repair.vendor_id if repair else None

    def get_repair_vendor_name(self, obj):
        repair = self._latest_repair(obj)
        return repair.vendor.name if repair and repair.vendor_id else ""

    def _latest_repair(self, obj):
        return obj.repair_records.order_by("-crdate").first()

    def get_repair_record_id(self, obj):
        repair = self._latest_repair(obj)
        return repair.id if repair else None

    def get_repair_record_number(self, obj):
        repair = self._latest_repair(obj)
        return repair.repair_number if repair else ""

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


class ClientReturnRecordCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientReturnRecord
        fields = (
            "received_from",
            "return_date",
            "reason",
            "notes",
        )
        extra_kwargs = {
            "received_from": {"required": False, "allow_blank": True},
            "return_date": {"required": False},
            "reason": {"required": False, "allow_blank": True},
            "notes": {"required": False, "allow_blank": True},
        }

    def update(self, instance, validated_data):
        try:
            return update_client_return_record_header(instance, **validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def to_representation(self, instance):
        return ClientReturnRecordSerializer(instance, context=self.context).data


class ClientReturnRecordCancelSerializer(serializers.Serializer):
    cancel_reason = serializers.CharField(required=True, allow_blank=False)

    def save(self, **kwargs):
        client_return = self.context["client_return"]
        request = self.context.get("request")
        try:
            return cancel_client_return_record(
                client_return,
                cancelled_by=request.user if request else None,
                cancel_reason=self.validated_data["cancel_reason"],
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
    client_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    unit_sale_prices = serializers.DictField(
        required=False,
        write_only=True,
        default=dict,
    )
    from_repair_number = serializers.CharField(
        source="from_repair.repair_number",
        read_only=True,
        default="",
    )
    from_reservation = serializers.PrimaryKeyRelatedField(
        queryset=ReservationRecord.objects.all(),
        required=False,
        allow_null=True,
    )
    from_reservation_number = serializers.CharField(
        source="from_reservation.reservation_number",
        read_only=True,
        default="",
    )

    class Meta:
        model = DeliveryRecord
        fields = (
            "id",
            "delivery_number",
            "is_warranty_return",
            "from_repair",
            "from_repair_number",
            "from_reservation",
            "from_reservation_number",
            "client",
            "client_name",
            "client_name_input",
            "customer_name",
            "receiver_name",
            "invoice_number",
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
            "unit_sale_prices",
            "items",
            "crdate",
            "isactive",
        )
        read_only_fields = (
            "delivery_number",
            "is_warranty_return",
            "from_repair",
            "from_repair_number",
            "from_reservation_number",
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
        extra_kwargs = {
            "customer_name": {"required": False, "allow_blank": True},
        }

    def get_total_units(self, obj):
        return obj.total_units

    def validate_unit_ids(self, value):
        unique_ids = list(dict.fromkeys(value))
        units = ProductUnit.objects.filter(pk__in=unique_ids, isactive=True)
        units_by_id = {unit.pk: unit for unit in units}
        missing_ids = [unit_id for unit_id in unique_ids if unit_id not in units_by_id]

        if missing_ids:
            raise serializers.ValidationError("One or more stock units were not found.")

        return unique_ids

    def validate(self, attrs):
        # Units delivered from a reservation are reserved, not available; the
        # service validates that case against the reservation's own lines.
        if not attrs.get("from_reservation"):
            unavailable_units = ProductUnit.objects.filter(
                pk__in=attrs.get("unit_ids", []),
            ).exclude(status=ProductUnit.STATUS_AVAILABLE)
            if unavailable_units.exists():
                raise serializers.ValidationError(
                    {"unit_ids": "Only available stock units can be delivered."}
                )
        return attrs

    def create(self, validated_data):
        unit_ids = validated_data.pop("unit_ids")
        request = self.context.get("request")
        try:
            return create_delivery_record(
                unit_ids=unit_ids,
                created_by=request.user if request else None,
                **validated_data,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


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
            "invoice_number",
            "delivery_date",
            "notes",
            "items",
        )
        extra_kwargs = {
            "customer_name": {"required": False, "allow_blank": False},
            "receiver_name": {"required": False, "allow_blank": True},
            "invoice_number": {"required": False, "allow_blank": True},
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
                invoice_number=validated_data.get("invoice_number")
                if "invoice_number" in validated_data
                else instance.invoice_number,
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
    supplier_name_input = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
    )
    created_by_name = serializers.CharField(
        source="created_by.get_username",
        read_only=True,
    )
    idempotency_key = serializers.CharField(
        required=False,
        write_only=True,
        allow_blank=True,
        max_length=64,
    )

    class Meta:
        model = ReceivingRecord
        fields = (
            "id",
            "receiving_number",
            "supplier",
            "supplier_name",
            "supplier_name_input",
            "po_number",
            "supplier_invoice_number",
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
            "idempotency_key",
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
            "po_number",
            "supplier_invoice_number",
            "received_date",
            "notes",
            "items",
        )
        extra_kwargs = {
            "supplier": {"required": False, "allow_null": True},
            "po_number": {"required": False, "allow_blank": True},
            "supplier_invoice_number": {"required": False, "allow_blank": True},
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
                po_number=validated_data.get("po_number")
                if "po_number" in validated_data
                else instance.po_number,
                supplier_invoice_number=validated_data.get("supplier_invoice_number")
                if "supplier_invoice_number" in validated_data
                else instance.supplier_invoice_number,
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
