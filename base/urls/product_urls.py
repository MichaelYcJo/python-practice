from django.urls import path
from base.views.product_views import getProducts, getProduct, createProduct, updateProduct, deleteProduct


urlpatterns = [
    path('', getProducts, name="products"),
    path('<str:pk>/', getProduct, name="product"),
    path('create/', createProduct, name="product-create"),
    path('update/<str:pk>/', updateProduct, name="product-update"),
    path('delete/<str:pk>/', deleteProduct, name="product-delete"),
]


