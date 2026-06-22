"""
URL configuration for bim project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from bim_accounts.forms import EmailOrUsernameAuthenticationForm

from . import views

urlpatterns = [
    path('', views.module_launcher, name='module_launcher'),
    path('api/command-center/', views.command_center_data, name='command_center_data'),
    path('operations/', views.module_launcher, name='operations'),
    path('operations/receiving/', views.module_launcher, name='operations_receiving'),
    path('operations/receiving/<int:pk>/', views.module_launcher, name='operations_receiving_detail'),
    path('operations/deliveries/', views.module_launcher, name='operations_deliveries'),
    path('operations/deliveries/<int:pk>/', views.module_launcher, name='operations_delivery_detail'),
    path('inventory/', views.module_launcher, name='inventory'),
    path('inventory/products/new/', views.module_launcher, name='inventory_add_product'),
    path('inventory/products/<int:pk>/', views.module_launcher, name='inventory_product_detail'),
    path('inventory/receiving/new/', views.module_launcher, name='inventory_receive_stock'),
    path('inventory/deliveries/new/', views.module_launcher, name='inventory_create_delivery'),
    path('suppliers/', views.module_launcher, name='suppliers'),
    path('clients/', views.module_launcher, name='clients'),
    path('assets/', views.module_launcher, name='assets'),
    path('knowledge-base/', views.module_launcher, name='knowledge_base'),
    path('settings/', views.module_launcher, name='settings'),
    path(
        'accounts/login/',
        LoginView.as_view(
            authentication_form=EmailOrUsernameAuthenticationForm,
            template_name='registration/login.html',
        ),
        name='login',
    ),
    path('accounts/', include('bim_accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('api/stock/', include('bim_stock.api_urls')),
    path('stock/', include('bim_stock.urls')),
]
