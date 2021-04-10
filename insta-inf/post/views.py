from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Like, Tag
from accounts import models as a_models
from .forms import PostForm
from comment.models import Comment
from comment.forms import CommentForm
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import json
from django.http import HttpResponse
from django.db.models import Count


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()
    
    return render(request, 'post/post_detail.html', {
        'comment_form': comment_form,
        'post': post,
    })


def post_list(request, tag=None):
    # 필드 추가 다른 필드의 값을 그대로 복사하거나, 다른 필드의 값들을 조합한 값을 넣을 수 있음.
    # num_post필드를 만들고 그 내용은 num_post의 역순인 post의 Count한 값을 담음 
    tag_all = Tag.objects.annotate(num_post=Count('post')).order_by('-num_post')
    
        #태그를 영소문상관없이 tag_name에 저장
    if tag:
        # prefetch는 1:1은 물론 다대다관계에서도 적용 
        post_list = Post.objects.filter(tag_set__name__iexact=tag) \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile') #select_related 는 1:1의 관계일때 적용됨 author이 하나면 profile도 하나임
    else:
        post_list = Post.objects.all() \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')

    comment_form = CommentForm()
    
    paginator = Paginator(post_list, 3)
    page_num = request.POST.get('page')
    
    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
        
    
    if request.is_ajax():
        return render(request, 'post/post_list_ajax.html', {
            'posts': posts,
            'comment_form': comment_form,
        })
    
    if request.method == 'POST':
        tag = request.POST.get('tag')
        tag_clean = ''.join(e for e in tag if e.isalnum()) # isalnum - 문자 숫자 구분 
        return redirect('post:post_search', tag_clean)

    if request.user.is_authenticated:
        username = request.user
        user = get_object_or_404(get_user_model(), username=username)
        user_profile = user.profile
        follow_set = request.user.profile.get_following
        follow_post_list = Post.objects.filter(author__profile__in=follow_set)
        
        return render(request, 'post/post_list.html', {
            'user_profile': user_profile,
            'tag': tag,
            'posts': posts,
            'follow_post_list': follow_post_list,
            'comment_form': comment_form,
            'tag_all': tag_all,
        })
    else:
        return render(request, 'post/post_list.html', {
            'tag': tag,
            'posts': posts,
            'comment_form': comment_form,
            'tag_all': tag_all,
        })


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post.tag_save()
            messages.info(request, '새 글이 등록되었습니다')
            return redirect('post:post_list')
    else:
        form = PostForm()
    return render(request, 'post/post_new.html', {
        'form': form,
    })



@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.warning(request, '잘못된 접근입니다')
        return redirect('post:post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            post.tag_set.clear()
            post.tag_save()
            messages.success(request, '수정완료')
            return redirect('post:post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'post/post_edit.html', {
        'post': post,
        'form': form,
    })


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user or request.method == 'GET':
        messages.warning(request, '잘못된 접근입니다.')
        return redirect('post:post_list')

    if request.method == 'POST':
        post.delete()
        messages.success(request, '삭제완료')
        return redirect('post:post_list')


@login_required
@require_POST
def post_like(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_like, post_like_created = post.like_set.get_or_create(user=request.user)

    if not post_like_created:
        post_like.delete()
        message = "좋아요 취소"
    else:
        message = "좋아요"

    context = {'like_count': post.like_count,
               'message': message}

    return HttpResponse(json.dumps(context), content_type="application/json")



@login_required
@require_POST
def post_bookmark(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_bookmark, post_bookmark_created = post.bookmark_set.get_or_create(user=request.user)

    if not post_bookmark_created:
        post_bookmark.delete()
        message = "북마크 취소"
    else:
        message = "북마크"

    context = {'bookmark_count': post.bookmark_count,
               'message': message}

    return HttpResponse(json.dumps(context), content_type="application/json")



def recommand(request):
    users = a_models.Profile.objects.all()
    post_list = Post.objects.all()

    print(post_list[1])

    return render(request, 'post/recommand.html', {
        'users': users,
        'post_list': post_list,
    })

