from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


class EmailLoginOnlyView(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.login_method == "email"

    def handle_no_permission(self):
        messages.error(self.request, "Social_User can't use this")
        return redirect("core:home")


# 로그아웃한사람만 볼 수 있음(ex: 회원가입, 로그인)
class LoggedOutOnlyView(UserPassesTestMixin):

    permission_denied_message = "Page not found"

    # test_func이 True면 다음 값으로 넘어갈 수 있게됨
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.error(self.request, "Can't go there")
        return redirect("core:home")


class LoggedInOnlyView(LoginRequiredMixin):

    login_url = reverse_lazy("users:login")
