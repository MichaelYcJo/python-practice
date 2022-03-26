from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from django.contrib.auth import authenticate

from accounts.models import User, Token


@api_view(['POST'])
def login(request):
    user = authenticate(email=request.data['email'], password=request.data['password'])
    print(request.data['email'], request.data['password'])
    if user is not None:
        try:
            token = Token.objects.get(user=user)
            return Response({"Token": token.key})
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
            return Response({"Token": token.key})
    else:
        return Response(status=401)