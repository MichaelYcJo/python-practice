from django.contrib import auth
from django.shortcuts import render, redirect


def login(request):
    template = "accounts/login.html"
    context = {"next": request.GET.get("next", "/")}

    if request.method == "GET":
        url_next = request.GET.get("next", "/")
        query = request.GET.get("q", "")
        
        if query != "":
            next_path = url_next + f'&q={query}'
        else:
            next_path = request.GET.get("next", "/")
    
        context = {"next": next_path}
    # Post Method
    if request.method == "POST":
        if request.POST["username"] and request.POST["password"]:
            user = auth.authenticate(
                request, username=request.POST["username"], password=request.POST["password"]
            )
            if user is not None:
                auth.login(request, user)
                return redirect(request.POST.get("next", "/"))
            else:
                context["error"] = "이메일 또는 비밀번호를 다시 확인해주세요."
        else:
            context["error"] = "이메일와 비밀번호를 모두 입력해주세요."

    return render(request, template, context)


def logout(request):
    auth.logout(request)
    return redirect("/")
