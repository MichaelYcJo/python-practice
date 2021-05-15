from django.urls import path
from accounts.views import register, login, logout, activate

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('activate/<uidb64>/<token>/', activate, name='activate')

]