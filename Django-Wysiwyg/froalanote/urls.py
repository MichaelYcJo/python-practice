from django.urls import path
from . import views


app_name = "froalanote"

urlpatterns = [

    path("froala_list/", views.froala_home, name="froala_home"),
    path("froala_create/", views.froala_create, name="froala_create")

]
