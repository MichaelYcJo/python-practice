from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone",
            "special_code",
            "email_checked",
        )
        extra_kwargs ={'password':{'write_only':True}}
        read_only_fields = ("id", "email_checked" )
    

    def validate_phone(self, phone):
        if len(phone) > 13:
            raise serializers.ValidationError('-을 포함하여 13글자를 넘을 수 없습니다')
        return phone

    def validate_first_name(self, value):
        return value.upper()
    
    def validate_last_name(self, value):
        return value.upper()

    def save(self):
        #request = self.context.get("request")
        user = User(
            email = self.validated_data['email']
        )
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password == confirm_password:
            #check exist email
            if User.objects.filter(email=user.email).exists():
                raise serializers.ValidationError({'email': 'A user with that email already exists'})
            else:
                #save signup data
                user.set_password(password)
                user.first_name = self.validated_data['first_name']
                user.last_name = self.validated_data['last_name']
                user.phone = self.validated_data['phone']
                user.save()
                return user
        else:
            raise serializers.ValidationError({'password': 'Both Passwords Must Be Matched!'})


class LoginTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        return token
