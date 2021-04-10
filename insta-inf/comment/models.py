from django.conf import settings
from django.db import models
from post.models import Post
from core import models as core_models

class Comment(core_models.TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=40)


    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.content

