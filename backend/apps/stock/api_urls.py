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
        "receiving-records/",
        api_views.ReceivingRecordListCreateAPIView.as_view(),
        name="receiving-records",
    ),
    path(
        "receiving-records/<int:pk>/",
        api_views.ReceivingRecordDetailAPIView.as_view(),
        name="receiving-record-detail",
    ),
    path("suppliers/", api_views.SupplierListAPIView.as_view(), name="suppliers"),
    path("brands/", api_views.BrandListAPIView.as_view(), name="brands"),
    path("models/", api_views.ProductModelListAPIView.as_view(), name="models"),
    path("categories/", api_views.CategoryListAPIView.as_view(), name="categories"),
]
