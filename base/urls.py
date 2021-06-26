from django.urls import path
from base.views import getRoutes, getProducts, getProduct, MyTokenObtainPairView, getuserProfile




urlpatterns = [
    path('', getRoutes, name="routes"),
    path('api/users/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/users/profile/', getuserProfile, name="user-profile"),
    path('products/', getProducts, name="products"),
    path('products/<str:pk>/', getProduct, name="product"),
]


