from django.db import models
from tinymce.models import HTMLField

class Tinynote(models.Model):
    title = models.CharField(max_length=10)
    content = HTMLField()