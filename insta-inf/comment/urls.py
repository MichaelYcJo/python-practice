from django.urls import path
from .views import *

app_name = 'comment'


urlpatterns = [


    path('comment/new/', comment_new, name='comment_new'),
    path('comment/delete/', comment_delete, name='comment_delete'),
    path('comment_detail/new/', comment_new_detail, name='comment_new_detail'),

]