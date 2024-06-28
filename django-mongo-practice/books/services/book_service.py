from bson import ObjectId
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.request import Request

from books.models.author import Author
from books.models.book import Book


class BookCreateService:
    def __init__(self, request: Request, data: dict) -> None:
        self.request = request
        self.title = data.get("title")
        self.publication_date = data.get("publication_date")
        self.authorId = data.get("author_id")

    def create_book(self):
        author = Author.objects.filter(_id=ObjectId(self.authorId)).first()

        embedded_author = {
            "_id": str(author._id),
            "name": author.name,
            "bio": author.bio,
        }

        book = Book.objects.create(
            title=self.title,
            publication_date=self.publication_date,
            author=embedded_author,
        )
        return book
