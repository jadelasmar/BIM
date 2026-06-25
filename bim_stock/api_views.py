from django.db.models import Count, Q
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Brand,
    Category,
    DeliveryRecord,
    Product,
    ProductModel,
    ProductUnit,
    Supplier,
)
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    DeliveryRecordSerializer,
    ProductModelSerializer,
    ProductSerializer,
    ProductUnitSerializer,
    SupplierSerializer,
)


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
            api_sold_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_SOLD),
                distinct=True,
            ),
            api_returned_units=Count(
                "units",
                filter=_active_unit_filter(ProductUnit.STATUS_RETURNED),
                distinct=True,
            ),
        )
        .order_by("descript", "sku")
    )


class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_product")
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
        _require_perm(self.request.user, "bim_stock.add_product")
        serializer.save()


class ProductDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_product")
        return _product_queryset()

    def perform_update(self, serializer):
        _require_perm(self.request.user, "bim_stock.change_product")
        serializer.save()


class ProductUnitListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductUnitSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_productunit")
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
        _require_perm(self.request.user, "bim_stock.add_productunit")
        serializer.save()


class ProductUnitDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductUnitSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_productunit")
        return ProductUnit.objects.select_related(
            "product",
            "product__category",
            "product__model__brand",
            "supplier",
        )

    def perform_update(self, serializer):
        _require_perm(self.request.user, "bim_stock.change_productunit")
        serializer.save()


class DeliveryRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DeliveryRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_productunit")
        queryset = (
            DeliveryRecord.objects.filter(isactive=True)
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
        _require_perm(self.request.user, "bim_stock.change_productunit")
        serializer.save()


class InventorySummaryAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        _require_perm(request.user, "bim_stock.view_product")
        active_units = ProductUnit.objects.filter(isactive=True)
        return Response(
            {
                "total_products": Product.objects.filter(isactive=True).count(),
                "available_units": active_units.filter(
                    status=ProductUnit.STATUS_AVAILABLE,
                ).count(),
                "reserved_units": active_units.filter(
                    status=ProductUnit.STATUS_RESERVED,
                ).count(),
                "sold_units": active_units.filter(status=ProductUnit.STATUS_SOLD).count(),
                "returned_units": active_units.filter(
                    status=ProductUnit.STATUS_RETURNED,
                ).count(),
                "low_stock_products": sum(
                    1
                    for product in _product_queryset()
                    if (
                        product.reorder_stock_level > 0
                        and product.available_units <= product.reorder_stock_level
                    )
                ),
            }
        )


class CategoryListAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_product")
        return Category.objects.order_by("name")

    def perform_create(self, serializer):
        _require_perm(self.request.user, "bim_stock.add_category")
        serializer.save()


class BrandListAPIView(generics.ListCreateAPIView):
    serializer_class = BrandSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_product")
        return Brand.objects.order_by("brandname")

    def perform_create(self, serializer):
        _require_perm(self.request.user, "bim_stock.add_brand")
        serializer.save()


class ProductModelListAPIView(generics.ListAPIView):
    serializer_class = ProductModelSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_product")
        return ProductModel.objects.select_related("brand").order_by(
            "brand__brandname",
            "modelname",
        )


class SupplierListAPIView(generics.ListAPIView):
    serializer_class = SupplierSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        _require_perm(self.request.user, "bim_stock.view_supplier")
        return Supplier.objects.order_by("name")
