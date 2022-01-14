from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("classroom.api.urls")),
    re_path(r"^api-auth/", include("rest_framework.urls")),
    re_path(r"^api-token-auth/", views.obtain_auth_token),
]
