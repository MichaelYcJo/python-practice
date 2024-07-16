from bson import ObjectId
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models.author import Author
from books.models.book import Book
from books.serializers import EmbeddedAuthorSerializer
from books.services.book_service import BookCreateService


class BooksAPI(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField()
        publication_date = serializers.DateTimeField(default=timezone.now)
        author_id = serializers.CharField()

        class Meta:
            ref_name = "book_input"

    class OutputSerializer(serializers.Serializer):
        _id = serializers.CharField()
        title = serializers.CharField()
        author = EmbeddedAuthorSerializer()

        class Meta:
            ref_name = "book_output"

    def get(self, request: Request):
        # find book
        book_id = request.query_params.get("id")
        book = Book.objects.filter(_id=ObjectId(book_id)).first()
        if not book:
            return Response(
                {"message": "Book not found"}, status=status.HTTP_404_NOT_FOUND
            )
        output_serializer = self.OutputSerializer(
            data={
                "_id": str(book._id),
                "title": book.title,
                "author": book.author,
            }
        )
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        service = BookCreateService(request, input_serializer.validated_data)
        book = service.create_book()
        output_serializer = self.OutputSerializer(
            data={"_id": str(book._id), "title": book.title, "author": book.author}
        )

        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
