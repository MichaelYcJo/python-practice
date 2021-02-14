from django.db import models
#from froala_editor.fields import FroalaField

class Post(models.Model):
    title = models.CharField(max_length=10)
    content = models.TextField()

    def __str__(self):
        return self.title

'''

class QuillPost(models.Model):
    title = models.CharField(max_length=200)
    content = QuillField()




  '''