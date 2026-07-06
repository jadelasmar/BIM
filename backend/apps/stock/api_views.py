from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from . import constants as stock_constants
from .models import (
    Brand,
    Category,
    ClientReturnRecord,
    DeliveryRecord,
    IssueRecord,
    Product,
    ProductModel,
    ProductUnit,
    ReceivingRecord,
    RepairRecord,
    ReservationRecord,
    StockMovement,
    Supplier,
)
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ClientReturnRecordSerializer,
    DeliveryRecordCancelSerializer,
    DeliveryRecordCorrectionSerializer,
    DeliveryRecordSerializer,
    IssueRecordSerializer,
    IssueReturnSerializer,
    ProductModelSerializer,
    ProductSerializer,
    ProductUnitSerializer,
    ReceivingRecordCancelSerializer,
    ReceivingRecordCorrectionSerializer,
    ReceivingRecordSerializer,
    RepairRecordSerializer,
    RepairResolveSerializer,
    ReservationRecordSerializer,
    ReservationReleaseSerializer,
    StockMovementSerializer,
    SupplierSerializer,
)
from .services import create_stock_movement


def _require_perm(user, permission):
    if not user.has_perm(permission):
        raise PermissionDenied("You do not have permission to use this API.")


def _active_unit_filter(status=None):
    filters = Q(units__isactive=True)
    if status:
        filters &= Q(units__status=status)
    return filters


def _product_queryset():
    return (
        Product.objects.filter(isactive=True)
        .select_related("category", "model__brand")
        .annotate(
            api_total_units=Count("units", filter=_active_unit_filter(), distinct=True),
            api_available_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_AVAILABLE),
                distinct=True,
            ),
            api_reserved_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_RESERVED),
                distinct=True,
            ),
            api_issued_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_ISSUED),
                distinct=True,
            ),
            api_sold_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_SOLD),
                distinct=True,
            ),
            api_repair_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_REPAIR),
                distinct=True,
            ),
        )
        .order_by("descript", "sku")
    )


class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT)
        queryset = _product_queryset()
        query = self.request.query_params.get("q", "").strip()
        category = self.request.query_params.get("category", "").strip()
        brand = self.request.query_params.get("brand", "").strip()
        status = self.request.query_params.get("status", "").strip()

        if query:
            queryset = queryset.filter(
                Q(descript__icontains=query)
                | Q(sku__icontains=query)
                | Q(barcode__icontains=query)
                | Q(units__serial_number__icontains=query)
            ).distinct()
        if category:
            queryset = queryset.filter(category_id=category)
        if brand:
            queryset = queryset.filter(model__brand_id=brand)
        if status:
            queryset = queryset.filter(units__isactive=True, units__status=status).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_PRODUCT)
        serializer.save()


class ProductDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT)
        return _product_queryset()

    def perform_update(self, serializer):
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT)
        serializer.save()


class ProductUnitListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductUnitSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT_UNIT)
        queryset = (
            ProductUnit.objects.filter(isactive=True)
            .select_related(
                "product",
                "product__category",
                "product__model__brand",
                "supplier",
            )
            .order_by("product__descript", "serial_number")
        )
        query = self.request.query_params.get("q", "").strip()
        status = self.request.query_params.get("status", "").strip()
        category = self.request.query_params.get("category", "").strip()
        brand = self.request.query_params.get("brand", "").strip()
        product = self.request.query_params.get("product", "").strip()

        if query:
            queryset = queryset.filter(
                Q(serial_number__icontains=query)
                | Q(product__descript__icontains=query)
                | Q(product__sku__icontains=query)
                | Q(product__barcode__icontains=query)
            )
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(product__category_id=category)
        if brand:
            queryset = queryset.filter(product__model__brand_id=brand)
        if product:
            queryset = queryset.filter(product_id=product)

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_PRODUCT_UNIT)
        with transaction.atomic():
            unit = serializer.save()
            create_stock_movement(
                product_unit=unit,
                movement_type=StockMovement.TYPE_MANUAL_ADD,
                from_status="",
                to_status=unit.status,
                reason="Manual Add Unit",
                notes=unit.notes,
                performed_by=self.request.user,
                movement_date=unit.purchase_date,
                reference="Manual Add Unit",
            )


class ProductUnitDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductUnitSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT_UNIT)
        return ProductUnit.objects.select_related(
            "product",
            "product__category",
            "product__model__brand",
            "supplier",
        )

    def perform_update(self, serializer):
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        old_status = serializer.instance.status
        with transaction.atomic():
            unit = serializer.save()
            if old_status != unit.status:
                create_stock_movement(
                    product_unit=unit,
                    movement_type=StockMovement.TYPE_MANUAL_UPDATE,
                    from_status=old_status,
                    to_status=unit.status,
                    reason="Manual stock unit update",
                    notes=unit.notes,
                    performed_by=self.request.user,
                    movement_date=timezone.localdate(),
                    reference="Manual Unit Update",
                )


class ProductStockMovementListAPIView(generics.ListAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_STOCK_MOVEMENT)
        get_object_or_404(Product.objects.filter(isactive=True), pk=self.kwargs["pk"])
        return (
            StockMovement.objects.filter(product_id=self.kwargs["pk"], isactive=True)
            .select_related(
                "product",
                "product_unit",
                "performed_by",
                "receiving_record",
                "delivery_record",
                "reservation_record",
                "issue_record",
                "repair_record",
                "client_return_record",
            )
            .order_by("-movement_date", "-crdate", "-pk")[:50]
        )


class ClientReturnRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ClientReturnRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_CLIENT_RETURN_RECORD)
        queryset = (
            ClientReturnRecord.objects.all()
            .select_related("delivery", "received_by")
            .prefetch_related(
                "items",
                "items__delivery_item",
                "items__delivery_item__delivery",
                "items__product",
                "items__product_unit",
            )
            .order_by("-return_date", "-return_number")
        )
        query = self.request.query_params.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(return_number__icontains=query)
                | Q(delivery__delivery_number__icontains=query)
                | Q(customer_name__icontains=query)
                | Q(received_from__icontains=query)
                | Q(reason__icontains=query)
                | Q(items__product_unit__serial_number__icontains=query)
                | Q(items__product__descript__icontains=query)
                | Q(items__product__sku__icontains=query)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_CLIENT_RETURN_RECORD)
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        serializer.save()


class ClientReturnRecordDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ClientReturnRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_CLIENT_RETURN_RECORD)
        return (
            ClientReturnRecord.objects.all()
            .select_related("delivery", "received_by")
            .prefetch_related(
                "items",
                "items__delivery_item",
                "items__delivery_item__delivery",
                "items__product",
                "items__product_unit",
            )
        )


class DeliveryRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DeliveryRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_DELIVERY_RECORD)
        queryset = (
            DeliveryRecord.objects.all()
            .select_related("created_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
            .order_by("-delivery_date", "-delivery_number")
        )
        query = self.request.query_params.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(delivery_number__icontains=query)
                | Q(customer_name__icontains=query)
                | Q(receiver_name__icontains=query)
                | Q(items__product_unit__serial_number__icontains=query)
                | Q(items__product__descript__icontains=query)
                | Q(items__product__sku__icontains=query)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_DELIVERY_RECORD)
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        serializer.save()


class DeliveryRecordDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = DeliveryRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return DeliveryRecordCorrectionSerializer
        return DeliveryRecordSerializer

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_DELIVERY_RECORD)
        return (
            DeliveryRecord.objects.all()
            .select_related("created_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
        )

    def perform_update(self, serializer):
        _require_perm(self.request.user, stock_constants.CHANGE_DELIVERY_RECORD)
        serializer.save()


class DeliveryRecordCancelAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        _require_perm(request.user, stock_constants.CHANGE_DELIVERY_RECORD)
        _require_perm(request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        delivery = get_object_or_404(
            DeliveryRecord.objects.select_related("created_by").prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            ),
            pk=pk,
        )

        serializer = DeliveryRecordCancelSerializer(
            data=request.data,
            context={"request": request, "delivery": delivery},
        )
        serializer.is_valid(raise_exception=True)
        delivery = serializer.save()
        return Response(DeliveryRecordSerializer(delivery).data)


class ReservationRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReservationRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_RESERVATION_RECORD)
        queryset = (
            ReservationRecord.objects.all()
            .select_related("reserved_by", "released_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
            .order_by("-reserved_at", "-reservation_number")
        )
        query = self.request.query_params.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(reservation_number__icontains=query)
                | Q(reserved_for__icontains=query)
                | Q(reason__icontains=query)
                | Q(items__product_unit__serial_number__icontains=query)
                | Q(items__product__descript__icontains=query)
                | Q(items__product__sku__icontains=query)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_RESERVATION_RECORD)
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        serializer.save()


class ReservationRecordDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ReservationRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_RESERVATION_RECORD)
        return (
            ReservationRecord.objects.all()
            .select_related("reserved_by", "released_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
        )


class ReservationRecordReleaseAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    cancel = False

    def post(self, request, pk):
        _require_perm(request.user, stock_constants.CHANGE_RESERVATION_RECORD)
        _require_perm(request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        reservation = get_object_or_404(
            ReservationRecord.objects.select_related(
                "reserved_by",
                "released_by",
            ).prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            ),
            pk=pk,
        )
        serializer = ReservationReleaseSerializer(
            data=request.data,
            context={
                "request": request,
                "reservation": reservation,
                "cancel": self.cancel,
            },
        )
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        return Response(ReservationRecordSerializer(reservation).data)


class ReservationRecordCancelAPIView(ReservationRecordReleaseAPIView):
    cancel = True


class IssueRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = IssueRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_ISSUE_RECORD)
        queryset = (
            IssueRecord.objects.all()
            .select_related("issued_by", "returned_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
            .order_by("-issue_date", "-issue_number")
        )
        query = self.request.query_params.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(issue_number__icontains=query)
                | Q(issued_to__icontains=query)
                | Q(department__icontains=query)
                | Q(branch_or_site__icontains=query)
                | Q(reason__icontains=query)
                | Q(items__product_unit__serial_number__icontains=query)
                | Q(items__product__descript__icontains=query)
                | Q(items__product__sku__icontains=query)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_ISSUE_RECORD)
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        serializer.save()


class IssueRecordDetailAPIView(generics.RetrieveAPIView):
    serializer_class = IssueRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_ISSUE_RECORD)
        return (
            IssueRecord.objects.all()
            .select_related("issued_by", "returned_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
        )


class IssueRecordReturnAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        _require_perm(request.user, stock_constants.CHANGE_ISSUE_RECORD)
        _require_perm(request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        issue = get_object_or_404(
            IssueRecord.objects.select_related(
                "issued_by",
                "returned_by",
            ).prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            ),
            pk=pk,
        )
        serializer = IssueReturnSerializer(
            data=request.data,
            context={"request": request, "issue": issue},
        )
        serializer.is_valid(raise_exception=True)
        issue = serializer.save()
        return Response(IssueRecordSerializer(issue).data)


class RepairRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RepairRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_REPAIR_RECORD)
        queryset = (
            RepairRecord.objects.all()
            .select_related("sent_by", "resolved_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
            .order_by("-repair_date", "-repair_number")
        )
        query = self.request.query_params.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(repair_number__icontains=query)
                | Q(repair_reason__icontains=query)
                | Q(reported_by_name__icontains=query)
                | Q(repair_location__icontains=query)
                | Q(technician__icontains=query)
                | Q(items__product_unit__serial_number__icontains=query)
                | Q(items__product__descript__icontains=query)
                | Q(items__product__sku__icontains=query)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_REPAIR_RECORD)
        _require_perm(self.request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        serializer.save()


class RepairRecordDetailAPIView(generics.RetrieveAPIView):
    serializer_class = RepairRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_REPAIR_RECORD)
        return (
            RepairRecord.objects.all()
            .select_related("sent_by", "resolved_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
        )


class RepairRecordResolveAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        _require_perm(request.user, stock_constants.CHANGE_REPAIR_RECORD)
        _require_perm(request.user, stock_constants.CHANGE_PRODUCT_UNIT)
        repair = get_object_or_404(
            RepairRecord.objects.select_related(
                "sent_by",
                "resolved_by",
            ).prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            ),
            pk=pk,
        )
        serializer = RepairResolveSerializer(
            data=request.data,
            context={"request": request, "repair": repair},
        )
        serializer.is_valid(raise_exception=True)
        repair = serializer.save()
        return Response(RepairRecordSerializer(repair).data)


class ReceivingRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReceivingRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_RECEIVING_RECORD)
        queryset = (
            ReceivingRecord.objects.all()
            .select_related("supplier", "created_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
            .order_by("-received_date", "-receiving_number")
        )
        query = self.request.query_params.get("q", "").strip()

        if query:
            queryset = queryset.filter(
                Q(receiving_number__icontains=query)
                | Q(reference_number__icontains=query)
                | Q(supplier__name__icontains=query)
                | Q(items__product__descript__icontains=query)
                | Q(items__product__sku__icontains=query)
                | Q(items__serial_number__icontains=query)
                | Q(items__product_unit__serial_number__icontains=query)
            ).distinct()

        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_RECEIVING_RECORD)
        _require_perm(self.request.user, stock_constants.ADD_PRODUCT_UNIT)
        serializer.save()


class ReceivingRecordDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ReceivingRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ReceivingRecordCorrectionSerializer
        return ReceivingRecordSerializer

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_RECEIVING_RECORD)
        return (
            ReceivingRecord.objects.all()
            .select_related("supplier", "created_by")
            .prefetch_related(
                "items",
                "items__product",
                "items__product_unit",
            )
        )

    def perform_update(self, serializer):
        _require_perm(self.request.user, stock_constants.CHANGE_RECEIVING_RECORD)
        serializer.save()


class ReceivingRecordCancelAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        _require_perm(request.user, stock_constants.CHANGE_RECEIVING_RECORD)
        receiving = get_object_or_404(
            ReceivingRecord.objects.select_related("supplier", "created_by")
            .prefetch_related("items", "items__product", "items__product_unit"),
            pk=pk,
        )
        if any(item.product_unit_id for item in receiving.items.all()):
            _require_perm(request.user, stock_constants.CHANGE_PRODUCT_UNIT)

        serializer = ReceivingRecordCancelSerializer(
            data=request.data,
            context={"request": request, "receiving": receiving},
        )
        serializer.is_valid(raise_exception=True)
        receiving = serializer.save()
        return Response(ReceivingRecordSerializer(receiving).data)


class InventorySummaryAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        _require_perm(request.user, stock_constants.VIEW_PRODUCT)
        active_units = ProductUnit.objects.filter(isactive=True)
        products = _product_queryset()
        return Response(
            {
                "total_products": Product.objects.filter(isactive=True).count(),
                "available_units": active_units.filter(
                    status=ProductUnit.STATUS_AVAILABLE,
                ).count(),
                "reserved_units": active_units.filter(
                    status=ProductUnit.STATUS_RESERVED,
                ).count(),
                "issued_units": active_units.filter(
                    status=ProductUnit.STATUS_ISSUED,
                ).count(),
                "sold_units": active_units.filter(status=ProductUnit.STATUS_SOLD).count(),
                "repair_units": active_units.filter(
                    status=ProductUnit.STATUS_REPAIR,
                ).count(),
                "out_of_stock_products": sum(
                    1 for product in products if product.available_units == 0
                ),
                "low_stock_products": sum(
                    1
                    for product in products
                    if product.is_low_stock
                ),
            }
        )


class CategoryListAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT)
        queryset = Category.objects.order_by("name")
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_CATEGORY)
        serializer.save()


class BrandListAPIView(generics.ListCreateAPIView):
    serializer_class = BrandSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT)
        queryset = Brand.objects.order_by("brandname")
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(brandname__icontains=query)
        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_BRAND)
        serializer.save()


class ProductModelListAPIView(generics.ListAPIView):
    serializer_class = ProductModelSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_PRODUCT)
        return ProductModel.objects.select_related("brand").order_by(
            "brand__brandname",
            "modelname",
        )


class SupplierListAPIView(generics.ListCreateAPIView):
    serializer_class = SupplierSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, stock_constants.VIEW_SUPPLIER)
        queryset = Supplier.objects.order_by("name")
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def perform_create(self, serializer):
        _require_perm(self.request.user, stock_constants.ADD_SUPPLIER)
        serializer.save()
