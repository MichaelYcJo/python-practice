from django.urls import path
from accounts.views import register, login, logout, activate, dashboard, forgotPassword, resetpassword_validate, resetPassword

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('forgotPassword/', forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', resetPassword, name='resetPassword'),

]