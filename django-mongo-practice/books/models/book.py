from bson import ObjectId
from djongo import models
from django.utils import timezone


class EmbeddedAuthor(models.Model):
    _id = models.ObjectIdField()
    name = models.CharField(max_length=100)
    bio = models.TextField()

    class Meta:
        abstract = True


class Book(models.Model):
    _id = models.ObjectIdField(default=ObjectId, primary_key=True, editable=False)
    title = models.CharField(max_length=200)
    publication_date = models.DateTimeField(default=timezone.now)
    author = models.EmbeddedField(model_container=EmbeddedAuthor)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "books_book"
        verbose_name = "book"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
