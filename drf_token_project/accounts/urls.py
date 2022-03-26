from django.urls import path

from accounts import views


urlpatterns = [
    path('signup/', views.sign_up, name='sign_up'),
    path('login/', views.login, name='login'),

]