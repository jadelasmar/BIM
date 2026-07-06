from django.urls import path

from . import views


urlpatterns = [
    path("", views.module_launcher, name="module_launcher"),
    path("api/command-center/", views.command_center_data, name="command_center_data"),
    path("operations/", views.module_launcher, name="operations"),
    path("operations/receiving/", views.module_launcher, name="operations_receiving"),
    path("operations/receiving/new/", views.module_launcher, name="operations_receive_stock"),
    path("operations/receiving/<int:pk>/", views.module_launcher, name="operations_receiving_detail"),
    path("operations/deliveries/", views.module_launcher, name="operations_deliveries"),
    path("operations/deliveries/new/", views.module_launcher, name="operations_create_delivery"),
    path("operations/deliveries/<int:pk>/", views.module_launcher, name="operations_delivery_detail"),
    path("inventory/", views.module_launcher, name="inventory"),
    path("inventory/products/new/", views.module_launcher, name="inventory_add_product"),
    path("inventory/products/<int:pk>/", views.module_launcher, name="inventory_product_detail"),
    path("inventory/stock-units/new/", views.module_launcher, name="inventory_add_stock_unit"),
    path("suppliers/", views.module_launcher, name="suppliers"),
    path("clients/", views.module_launcher, name="clients"),
    path("assets/", views.module_launcher, name="assets"),
    path("knowledge-base/", views.module_launcher, name="knowledge_base"),
    path("settings/", views.module_launcher, name="settings"),
]
