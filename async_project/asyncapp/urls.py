from django.urls import path
from .views import *


app_name = "asyncapp"
urlpatterns = [
    path("", homeview, name="home"),
    path("article-create/", articlecreateview, name="articlecreate"),
]
