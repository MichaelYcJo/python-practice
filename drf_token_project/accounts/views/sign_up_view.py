from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from accounts.models import User



@api_view(['POST'])
def sign_up(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            email=request.data['email'], 
            password=request.data['password'],
            first_name = request.data['first_name'],
            last_name = request.data['last_name'],
            phone = request.data['phone']
            )

        user.save()

        token = Token.objects.create(user=user)
        return Response({"Token": token.key})
        
