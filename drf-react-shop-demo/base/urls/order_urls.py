from django.urls import path

from base.views.order_views import getOrders, addOrderItems, getMyOrders, updateOrderToPaid, getOrderById, updateOrderToDelivered

urlpatterns = [

    path('', getOrders, name='orders'),
    path('add/', addOrderItems, name='orders-add'),
    path('myorders/', getMyOrders, name='myorders'),

    path('<str:pk>/deliver/', updateOrderToDelivered, name='order-delivered'),

    path('<str:pk>/', getOrderById, name='user-order'),
    path('<str:pk>/pay/', updateOrderToPaid, name='pay'),
]

