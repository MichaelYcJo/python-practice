from django.db import models
from froala_editor.fields import FroalaField

class FroalaPost(models.Model):
    title = models.CharField(max_length=200)
    content = FroalaField(options={
    'toolbarInline': True,
  })