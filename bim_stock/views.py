from django.shortcuts import render

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
