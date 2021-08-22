from django.urls import path
from base.views.product_views import getProducts, getProduct, getTopProducts, uploadImage, createProduct, updateProduct, deleteProduct, createProductReview


urlpatterns = [
    path('', getProducts, name="products"),
    path('create/', createProduct, name="product-create"),
    path('upload/', uploadImage, name="image-upload"),
    path('<str:pk>/reviews/', createProductReview, name="create-review"),
    path('top/', getTopProducts, name='top-products'),

    path('<str:pk>/', getProduct, name="product"),
    path('update/<str:pk>/', updateProduct, name="product-update"),
    path('delete/<str:pk>/', deleteProduct, name="product-delete"),
]


