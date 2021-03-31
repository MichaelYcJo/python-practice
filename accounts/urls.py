from accounts.views import hello_world
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path('hello_world', hello_world, name="hello_world")
]
