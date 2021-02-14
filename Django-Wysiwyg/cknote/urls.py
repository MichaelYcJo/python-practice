from django.urls import path
from . import views


app_name = "cknote"

urlpatterns = [
    path('ck_list/',views.ck_home, name="ck_home"),
    path("ck_create/", views.ckeditor_create, name="ckeditor_create"),
    #path("quill_list/", views.quill_home, name="quill_home"),
    #path("quill_create/", views.quill_create, name="quill_create"),
]
