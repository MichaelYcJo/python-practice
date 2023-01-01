from django.urls import path

from products.views import ProductListAPI, product_detail, product_search_api


urlpatterns = [
    path("list", ProductListAPI.as_view(), name="product_list"),
    path("detail/<str:pk>/", product_detail, name="product_detail"),
    path("search", product_search_api, name="product_search"),
]
