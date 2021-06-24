from django.urls import path
from base.views import getRoutes, getProducts, getProduct
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)



urlpatterns = [
    path('api/users/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', getRoutes, name="routes"),
    path('products/', getProducts, name="products"),
    path('products/<str:pk>/', getProduct, name="product"),
]


