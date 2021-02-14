from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

class Blog(models.Model):
    title = models.CharField(max_length=100)
    pub_data = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField()
    img_url = models.CharField(max_length=200)


    def publish(self):
        self.save()