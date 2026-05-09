from django.urls import path

from . import views

app_name = "bim_stock"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("units/", views.stock_list, name="stock_list"),
]
