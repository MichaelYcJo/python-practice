from django.urls import path
from base.views.product_views import getProducts, getProduct


urlpatterns = [
    path('', getProducts, name="products"),
    path('<str:pk>/', getProduct, name="product"),
]


