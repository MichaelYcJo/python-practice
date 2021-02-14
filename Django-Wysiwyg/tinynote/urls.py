from django.urls import path
from . import views


app_name = "tinynote"

urlpatterns = [
    path("tiny_create/", views.tiny_create, name="tiny_create"),


]
