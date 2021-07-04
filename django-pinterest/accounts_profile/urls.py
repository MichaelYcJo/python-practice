from django.urls import path
from accounts_profile.views import ProfileCreateView, ProfileUpdateView

app_name = 'accounts_profile'

urlpatterns = [
    path('create/', ProfileCreateView.as_view(), name='create'),
    path('update/<int:pk>', ProfileUpdateView.as_view(), name='update'),

]