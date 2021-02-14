
from django.urls import path
from . import views


app_name = "youtube"

urlpatterns = [

    path('', views.HomeView.as_view()),
    path('register', views.RegisterView.as_view()),
    path('login', views.LoginView.as_view()),
    path('new_video', views.NewVideo.as_view()),
    path('video/<int:id>', views.VideoView.as_view()),
    path('get_video/<file_name>', views.VideoFileView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('comment', views.CommentView.as_view())
    ]