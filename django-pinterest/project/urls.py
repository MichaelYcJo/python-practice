from django.urls import path

from project.views import ProjectListView, ProjectCreateView, ProjectDetailView

app_name = 'project'

urlpatterns = [
    path('list/', ProjectListView.as_view(), name='list'),

    path('create/', ProjectCreateView.as_view(), name='create'),
    path('detail/<int:pk>', ProjectDetailView.as_view(), name='detail'),
]