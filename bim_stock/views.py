from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Product, ProductUnit


def require_any_stock_view_permission(user):
    if user.has_perm("bim_stock.view_product") or user.has_perm(
        "bim_stock.view_productunit"
    ):
        return

    raise PermissionDenied


# Dashboard page: /stock/
# Shows high-level stock counts only.
@login_required
def dashboard(request):
    require_any_stock_view_permission(request.user)
    active_products = Product.objects.filter(isactive=True)
    context = {
        "total_products": active_products.count(),
        "available_units": ProductUnit.objects.filter(
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        ).count(),
        "sold_units": ProductUnit.objects.filter(
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        ).count(),
        "low_stock_products": sum(1 for product in active_products if product.is_low_stock),
    }

    return render(request, "bim_stock/dashboard.html", context)


# Product list page: /stock/products/
# q is the optional search text from the URL, for example:
# /stock/products/?q=zebra
@login_required
def product_list(request):
    if not request.user.has_perm("bim_stock.view_product"):
        raise PermissionDenied

    query = request.GET.get("q", "").strip()
    products = (
        Product.objects.filter(isactive=True)
        .select_related("category__type", "model__brand")
        .annotate(
            available_unit_count=Count(
                "units",
                filter=Q(
                    units__status=ProductUnit.STATUS_AVAILABLE,
                    units__isactive=True,
                ),
            )
        )
        .order_by("descript", "printed", "sku")
    )

    if query:
        # Search active products by name, SKU, or product barcode.
        products = products.filter(
            Q(descript__icontains=query)
            | Q(printed__icontains=query)
            | Q(sku__icontains=query)
            | Q(barcode__icontains=query)
        )

    return render(
        request,
        "bim_stock/product_list.html",
        {
            "products": products,
            "query": query,
        },
    )


# Product detail page: /stock/products/<id>/
# Shows one active product and its active available units.
@login_required
def product_detail(request, pk):
    if not request.user.has_perm("bim_stock.view_product"):
        raise PermissionDenied
    can_view_product_units = request.user.has_perm("bim_stock.view_productunit")

    product = get_object_or_404(
        Product.objects.select_related("category__type", "model__brand"),
        pk=pk,
        isactive=True,
    )
    available_units_query = (
        product.units.filter(
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        .select_related("supplier")
        .order_by("serial_number")
    )
    available_units = (
        available_units_query if can_view_product_units else ProductUnit.objects.none()
    )

    context = {
        "product": product,
        "available_units": available_units,
        "available_unit_count": available_units_query.count(),
        "can_view_product_units": can_view_product_units,
    }

    return render(request, "bim_stock/product_detail.html", context)


# Stock unit list page: /stock/units/
# q is the optional search text from the URL, for example:
# /stock/units/?q=SN123
@login_required
def stock_list(request):
    if not request.user.has_perm("bim_stock.view_productunit"):
        raise PermissionDenied

    query = request.GET.get("q", "").strip()
    units = (
        ProductUnit.objects.filter(isactive=True)
        .select_related("product", "product__model__brand", "supplier")
        .order_by("product__descript", "serial_number")
    )

    if query:
        # Search stock units by serial number or related product identifiers.
        units = units.filter(
            Q(serial_number__icontains=query)
            | Q(product__descript__icontains=query)
            | Q(product__printed__icontains=query)
            | Q(product__sku__icontains=query)
            | Q(product__barcode__icontains=query)
        )

    return render(
        request,
        "bim_stock/stock_list.html",
        {
            "units": units,
            "query": query,
        },
    )
