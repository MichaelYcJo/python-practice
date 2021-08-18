from django.urls import path
from base.views.product_views import getProducts, getProduct, uploadImage, createProduct, updateProduct, deleteProduct


urlpatterns = [
    path('', getProducts, name="products"),
    path('upload/', uploadImage, name="image-upload"),
    path('create/', createProduct, name="product-create"),
    path('<str:pk>/', getProduct, name="product"),
    path('update/<str:pk>/', updateProduct, name="product-update"),
    path('delete/<str:pk>/', deleteProduct, name="product-delete"),
]


