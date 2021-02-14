from django.shortcuts import render, redirect
from .models import Blog
from .forms import CKEditorForm


def ck_home(request):
    post_list = Blog.objects.all()
    context = {
        'post_list': post_list,
    }
    return render(request, "ckeditor_list.html", context)


def ckeditor_create(request):
    if request.method == "POST":
        form = CKEditorForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("cknote:ck_home")
    else:
        form = CKEditorForm()
    context = {
        'form' : form
    }
    return render(request, 'ckeditor_form.html', context)
