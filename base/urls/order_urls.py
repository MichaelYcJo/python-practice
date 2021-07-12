from django.urls import path

from base.views.order_views import getOrders, addOrderItems

urlpatterns = [
    path('', getOrders, name='orders'),
    path('add/', addOrderItems, name='orders-add'),

]


