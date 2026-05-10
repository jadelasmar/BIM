from django.urls import path

from . import views

# Namespace used by templates and redirects.
# Example: {% url 'bim_stock:dashboard' %}
app_name = "bim_stock"

urlpatterns = [
    # /stock/
    path("", views.dashboard, name="dashboard"),

    # /stock/products/
    path("products/", views.product_list, name="product_list"),

    # /stock/products/1/
    path("products/<int:pk>/", views.product_detail, name="product_detail"),

    # /stock/units/
    path("units/", views.stock_list, name="stock_list"),
]
