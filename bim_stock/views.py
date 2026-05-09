from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Product, ProductUnit


def dashboard(request):
    context = {
        "total_products": Product.objects.filter(isactive=True).count(),
        "available_units": ProductUnit.objects.filter(
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        ).count(),
        "sold_units": ProductUnit.objects.filter(
            status=ProductUnit.STATUS_SOLD,
            isactive=True,
        ).count(),
        "damaged_units": ProductUnit.objects.filter(
            status=ProductUnit.STATUS_DAMAGED,
            isactive=True,
        ).count(),
    }

    return render(request, "bim_stock/dashboard.html", context)


def product_list(request):
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


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category__type", "model__brand"),
        pk=pk,
        isactive=True,
    )
    available_units = (
        product.units.filter(
            status=ProductUnit.STATUS_AVAILABLE,
            isactive=True,
        )
        .select_related("supplier")
        .order_by("serial_number")
    )

    context = {
        "product": product,
        "available_units": available_units,
        "available_unit_count": available_units.count(),
    }

    return render(request, "bim_stock/product_detail.html", context)


def stock_list(request):
    query = request.GET.get("q", "").strip()
    units = (
        ProductUnit.objects.filter(isactive=True)
        .select_related("product", "product__model__brand", "supplier")
        .order_by("product__descript", "serial_number")
    )

    if query:
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
