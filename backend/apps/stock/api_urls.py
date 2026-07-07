from django.urls import path

from . import api_views

app_name = "bim_stock_api"

urlpatterns = [
    path("summary/", api_views.InventorySummaryAPIView.as_view(), name="summary"),
    path("products/", api_views.ProductListCreateAPIView.as_view(), name="products"),
    path(
        "products/<int:pk>/",
        api_views.ProductDetailAPIView.as_view(),
        name="product-detail",
    ),
    path(
        "products/<int:pk>/movements/",
        api_views.ProductStockMovementListAPIView.as_view(),
        name="product-movements",
    ),
    path(
        "product-units/",
        api_views.ProductUnitListCreateAPIView.as_view(),
        name="product-units",
    ),
    path(
        "product-units/<int:pk>/",
        api_views.ProductUnitDetailAPIView.as_view(),
        name="product-unit-detail",
    ),
    path(
        "deliveries/",
        api_views.DeliveryRecordListCreateAPIView.as_view(),
        name="deliveries",
    ),
    path(
        "deliveries/<int:pk>/cancel/",
        api_views.DeliveryRecordCancelAPIView.as_view(),
        name="delivery-cancel",
    ),
    path(
        "deliveries/<int:pk>/",
        api_views.DeliveryRecordDetailAPIView.as_view(),
        name="delivery-detail",
    ),
    path(
        "reservations/",
        api_views.ReservationRecordListCreateAPIView.as_view(),
        name="reservations",
    ),
    path(
        "reservations/<int:pk>/release/",
        api_views.ReservationRecordReleaseAPIView.as_view(),
        name="reservation-release",
    ),
    path(
        "reservations/<int:pk>/cancel/",
        api_views.ReservationRecordCancelAPIView.as_view(),
        name="reservation-cancel",
    ),
    path(
        "reservations/<int:pk>/",
        api_views.ReservationRecordDetailAPIView.as_view(),
        name="reservation-detail",
    ),
    path(
        "issues/",
        api_views.IssueRecordListCreateAPIView.as_view(),
        name="issues",
    ),
    path(
        "issues/<int:pk>/return/",
        api_views.IssueRecordReturnAPIView.as_view(),
        name="issue-return",
    ),
    path(
        "issues/<int:pk>/",
        api_views.IssueRecordDetailAPIView.as_view(),
        name="issue-detail",
    ),
    path(
        "repairs/",
        api_views.RepairRecordListCreateAPIView.as_view(),
        name="repairs",
    ),
    path(
        "repairs/<int:pk>/resolve/",
        api_views.RepairRecordResolveAPIView.as_view(),
        name="repair-resolve",
    ),
    path(
        "repairs/<int:pk>/",
        api_views.RepairRecordDetailAPIView.as_view(),
        name="repair-detail",
    ),
    path(
        "client-returns/",
        api_views.ClientReturnRecordListCreateAPIView.as_view(),
        name="client-returns",
    ),
    path(
        "client-returns/<int:pk>/",
        api_views.ClientReturnRecordDetailAPIView.as_view(),
        name="client-return-detail",
    ),
    path(
        "receiving-records/",
        api_views.ReceivingRecordListCreateAPIView.as_view(),
        name="receiving-records",
    ),
    path(
        "receiving-records/<int:pk>/cancel/",
        api_views.ReceivingRecordCancelAPIView.as_view(),
        name="receiving-record-cancel",
    ),
    path(
        "receiving-records/<int:pk>/",
        api_views.ReceivingRecordDetailAPIView.as_view(),
        name="receiving-record-detail",
    ),
    path("suppliers/", api_views.SupplierListAPIView.as_view(), name="suppliers"),
    path("suppliers/<int:pk>/", api_views.SupplierDetailAPIView.as_view(), name="supplier-detail"),
    path("clients/", api_views.ClientListCreateAPIView.as_view(), name="clients"),
    path("clients/<int:pk>/", api_views.ClientDetailAPIView.as_view(), name="client-detail"),
    path("brands/", api_views.BrandListAPIView.as_view(), name="brands"),
    path("models/", api_views.ProductModelListAPIView.as_view(), name="models"),
    path("categories/", api_views.CategoryListAPIView.as_view(), name="categories"),
]
