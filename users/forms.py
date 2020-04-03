from django import forms
from . import models


class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        # cleaned_data를 email, pwd 변수에 넣음
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            # 해당 email과 같은 username이 있는 모델을 찾아 유효성검사를함
            user = models.User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Password is wrong"))
            # 있으면 email을 반환 없으면 예외처리발생
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("User does not exist"))
