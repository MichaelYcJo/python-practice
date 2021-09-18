from django.urls import path


from accounts.views.register_view import registerUser
 



urlpatterns = [
    path('register/', registerUser, name='register'),

]