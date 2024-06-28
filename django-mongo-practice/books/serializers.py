from books.models.author import Author
from rest_framework import serializers


class EmbeddedAuthorSerializer(serializers.Serializer):
    _id = serializers.CharField()
    name = serializers.CharField()
    bio = serializers.CharField()
