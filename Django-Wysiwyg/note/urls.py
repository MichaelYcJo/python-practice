from django.urls import path
from . import views


app_name = "note"

urlpatterns = [
    path('summer_list',views.home, name="home"),
    path("summer_create/", views.summer_create, name="summer_create"),
    #path("quill_list/", views.quill_home, name="quill_home"),
    #path("quill_create/", views.quill_create, name="quill_create"),
    #path("froala_list/", views.froala_home, name="froala_home"),
    #path("froala_create/", views.froala_create, name="froala_create")

]
