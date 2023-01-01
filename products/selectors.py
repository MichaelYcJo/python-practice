from django.db.models import QuerySet

from products.models import Product


def product_list_queryset_selector(category: str) -> QuerySet[Product]:
    if category == "main":
        products = Product.objects.all().order_by("-created_at")[:4]
    else:
        products = Product.objects.all().order_by("-created_at")

    return products
