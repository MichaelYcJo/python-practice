from django.urls import path

from order.views import checkout_order_api, checkout_complate_api


urlpatterns = [
    path('checkout', checkout_order_api, name='checkout_order_api'),
    path('checkout/complate', checkout_complate_api, name='checkout_complate_api'),

]