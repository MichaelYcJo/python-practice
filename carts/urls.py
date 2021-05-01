from django.urls import path

from carts.views import cart, add_cart

urlpatterns = [
    path('', cart, name='cart'),
    path('add-cart/<int:product_id>', add_cart, name='add_cart' )
]
