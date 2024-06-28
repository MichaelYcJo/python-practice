from django.urls import path

from books.controllers.author import AuthorAPI
from books.controllers.book import BooksAPI


urlpatterns = [
    path(
        "v1/create/author",
        AuthorAPI.as_view(),
        name="crate_author",
    ),
    path(
        "v1/create/book",
        BooksAPI.as_view(),
        name="create_book",
    ),
]
