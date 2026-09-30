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
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

urlpatterns = [
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('api/stock/', include('apps.stock.api_urls')),
]

# Served unconditionally, not just under DEBUG: this app runs on an internal
# LAN with no nginx/reverse proxy in front of it (same reasoning as whitenoise
# serving STATIC_ROOT directly in bim/settings.py), so Django has to be the
# one serving uploaded product images in production too. Note this uses
# django.views.static.serve directly, not the django.conf.urls.static.static()
# shortcut - that shortcut silently no-ops whenever DEBUG=False, which is
# exactly why the previous version of this file never worked in production.
urlpatterns += [
    re_path(
        r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
        serve_static,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
