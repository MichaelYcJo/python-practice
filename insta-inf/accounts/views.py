from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib.auth import logout as django_logout
from . import forms, models, mixins
from post import models as PostModel
from django.contrib import messages
from django.contrib.auth import get_user_model
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def myprofile(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    user_profile = user.profile
    
    target_user = get_user_model().objects.filter(id=user.id).select_related('profile') \
        .prefetch_related('profile__follower_user__from_user', 'profile__follow_user__to_user')
        
    post_list = user.post_set.all()
    
    all_post_list = PostModel.Post.objects.all()
    
    return render(request, 'accounts/myprofile.html', {
        'user_profile': user_profile,
        'target_user': target_user,
        'post_list': post_list,
        'all_post_list': all_post_list,
        'pk': pk,
        'user': user,
    })


def signup(request):
    if request.user.is_authenticated:
        messages.error(request, "잘못된 접근경로입니다.")
        return redirect(reverse("post:post_list"))
    if request.method == 'POST':
        form = forms.SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            return redirect('accounts:login')
    else:
        form = forms.SignupForm()
    return render(request, 'accounts/signup.html',{
        'form': form,
    }) 


def login_check(request):
    if request.user.is_authenticated:
        messages.error(request, "잘못된 접근경로입니다.")
        return redirect(reverse("post:post_list"))
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        name = request.POST.get('username')
        pwd = request.POST.get('password')

        user = authenticate(username=name, password=pwd)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, 'accounts/login_fail.html')
    else:
        form = forms.LoginForm()
        return render(request, 'accounts/login.html', {"form":form})



def logout(request):
    django_logout(request)
    return redirect("/")


@login_required
@require_POST
def follow(request):
    if not request.user.is_authenticated:
        messages.error(request, "잘못된 접근경로입니다.")
        return redirect(reverse("post:post_list"))
    from_user = request.user.profile
    pk = request.POST.get('pk')
    to_user = get_object_or_404(models.Profile, pk=pk)
    follow, created = models.Follow.objects.get_or_create(from_user=from_user, to_user=to_user)
    
    if created:
        message = '팔로우 시작!'
        status = 1
    else:
        follow.delete()
        message = '팔로우 취소'
        status = 0
        
    context = {
        'message': message,
        'status': status,
    }
    return HttpResponse(json.dumps(context), content_type="application/json")