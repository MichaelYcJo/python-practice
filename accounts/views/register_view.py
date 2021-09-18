from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from accounts.models import User
from accounts.serializers import UserSerializer


@api_view(['POST'])
def registerUser(request):
    print('왔어요왔어')
    data = request.data
    try:
        user = User.objects.create(
            email = data['email'],
            password = data['password'],
            first_name = data['first_name'],
            last_name = data['last_name'],
            phone = data['phone']
        )

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST) 
