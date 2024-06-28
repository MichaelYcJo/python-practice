from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.request import Request

from books.models.author import Author


class AuthorCreateService:
    def __init__(self, request: Request, data: dict) -> None:
        self.request = request
        self.name = data.get("name")
        self.bio = data.get("bio")

    def create_author(self):
        author = Author.objects.create(name=self.name, bio=self.bio)
        return author
