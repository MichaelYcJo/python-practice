import os, requests
from django.http.response import JsonResponse

from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from decouple import config

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from accounts.models import User, LoginType
from accounts.serializers import LoginTokenSerializer



class LogIn(TokenObtainPairView):
    serializer_class = LoginTokenSerializer


class TokenTestView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


def kakao_login(request):
    client_id = config("KAKAO_ID")	

    if settings.DEBUG is False:
        redirect_uri = "http://127.0.0.1:8000/api/v1/accounts/login/kakao/callback"
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        )
    else:
        redirect_uri = "http://127.0.0.1:8000/api/v1/accounts/login/kakao/callback"
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    pass