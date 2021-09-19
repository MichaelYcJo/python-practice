from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from accounts.models import User
from accounts.serializers import UserSerializer


@api_view(['POST'])
def registerUser(request):
    data = request.data
    serializer = UserSerializer(data = request.data, context = {'request': request})
    response_data = {}

    if serializer.is_valid():
        user = serializer.save()
        response_data['response'] = 'Successfully registered new user'
    else:
        response_data['response'] = 'Failed to register new user'
        response_data['error'] = serializer.errors
    return Response(response_data)