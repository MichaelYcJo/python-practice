from accounts.views import hello_world, AccountCreateView
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path('hello_world', hello_world, name="hello_world"),
    path('create/', AccountCreateView.as_view(), name='create'),
]
