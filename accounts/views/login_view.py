from django.contrib.auth import authenticate


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import LoginTokenSerializer

import jwt


class LogIn(TokenObtainPairView):
    serializer_class = LoginTokenSerializer


class TokenTestView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)