from rest_framework import pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from products.models import Product
from products.serializers import ProductSerializer


@permission_classes([AllowAny])
@api_view(['GET'])
def product_list(request):

    products = Product.objects.all().order_by('-created_at')

    paginator = PageNumberPagination()
    paginator.page_size = 8

    results = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)
