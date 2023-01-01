from rest_framework import pagination, views, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from core.serializers import inline_serializer
from products.models import Product
from products.selectors import product_list_queryset_selector
from products.serializers import ProductSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class ProductListAPI(views.APIView):
    """Product List API"""

    permission_classes = (AllowAny,)

    class OutputSerializer(serializers.Serializer):
        """
        Output Serializer
        """

        id = serializers.IntegerField(label="Product ID")
        seller = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "first_name": serializers.CharField(),
                "last_name": serializers.CharField(),
                "phone": serializers.CharField(),
                "email": serializers.CharField(),
            },
        )
        category = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "depth": serializers.IntegerField(),
                # TODO parent_category
                "parent_category": inline_serializer(
                    fields={
                        "id": serializers.IntegerField(),
                        "name": serializers.CharField(),
                    },
                ),
            },
        )

        name = serializers.CharField(label="Product Name")
        product_image1 = serializers.ImageField(label="Product Image1")
        product_image2 = serializers.ImageField(label="Product Image2")
        brand = serializers.CharField(label="Product Brand")
        description = serializers.CharField(label="Product Description")
        weight = serializers.CharField(label="Product Weight")
        dimensions = serializers.CharField(label="Product Dimensions")
        materials = serializers.CharField(label="Product Materials")
        other_info = serializers.CharField(label="Product Other Info")
        price = serializers.IntegerField(label="Product Price")
        count_in_stock = serializers.IntegerField(label="Product Count In Stock")
        recommendation_rank = serializers.IntegerField(
            label="Product Recommendation Rank"
        )
        product_status = serializers.CharField(label="Product Status")
        is_new = serializers.BooleanField(label="Product Is New")
        url_path = serializers.CharField(label="Product URL Path")

        class Meta:
            ref_name = "product_list_output"

    @swagger_auto_schema(
        operation_summary="[Product] 상품 리스트",
        operation_description="Product 모델 기준으로 조회한 리스트",
        responses={
            status.HTTP_200_OK: openapi.Response("싱픔 리스트", OutputSerializer(many=True))
        },
    )
    def get(self, request: Request) -> Response:
        category = request.GET.get("category")
        products = product_list_queryset_selector(category)
        serializer = self.OutputSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(["GET"])
def product_search_api(request):
    query = request.GET.get("query")
    products = Product.objects.filter(name__icontains=query)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
