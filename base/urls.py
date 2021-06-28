from django.urls import path
from base.views.product_view import getProducts, getProduct
from base.views.user_view import MyTokenObtainPairView, getuserProfile, getUsers
from base.views.register_view import registerUser



urlpatterns = [
    path('api/users/register/', registerUser, name='register'),
    path('api/users/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/users/profile/', getuserProfile, name="user-profile"),
    path('api/users/', getUsers, name="users"),
    path('products/', getProducts, name="products"),
    path('products/<str:pk>/', getProduct, name="product"),
]


