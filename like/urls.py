
from django.urls import path

from like.views import LikeArticleView

app_name = 'like'

urlpatterns = [
    path('article/like/<int:pk>', LikeArticleView.as_view(), name='article_like'),
]