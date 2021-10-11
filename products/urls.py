from django.urls import path

from products.views import product_list


urlpatterns = [
    path('list', product_list, name='product_list'),

]