from djongo import models
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=200)
    publication_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey("books.Author", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "books_book"
        verbose_name = "book"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
