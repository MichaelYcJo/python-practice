from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from books.services.author_service import AuthorCreateService


class AuthorAPI(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField()
        bio = serializers.CharField()

        class Meta:
            ref_name = "author_input"

    class OutputSerializer(serializers.Serializer):
        name = serializers.CharField()

        class Meta:
            ref_name = "author_output"

    def post(self, request: Request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        service = AuthorCreateService(request, input_serializer.validated_data)
        author = service.create_author()
        output_serializer = self.OutputSerializer(data={"name": author.name})
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
