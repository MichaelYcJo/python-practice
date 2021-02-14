from django.shortcuts import render,redirect, get_object_or_404
from .forms import SummerNoteForm
# CKEditorForm, QuillPostForm, FroalaForm
from .models import Post
# CKEditor, QuillPost, FroalaPost


def home(request):
    post_list = Post.objects.all()
    context = {
        'post_list': post_list,
    }
    return render(request, "home.html", context)

def summer_create(request):
    if request.method == "POST":
        form = SummerNoteForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("note:home")
    else:
        form = SummerNoteForm()
    context = {
        'form' : form
    }
    return render(request, 'summer_form.html', context)


'''
def ck_home(request):
    post_list = CKEditor.objects.all()
    context = {
        'post_list': post_list,
    }
    return render(request, "ckeditor_list.html", context)


def ckeditor_create(request):
    if request.method == "POST":
        form = CKEditorForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("note:ck_home")
    else:
        form = CKEditorForm()
    context = {
        'form' : form
    }
    return render(request, 'ckeditor_form.html', context)



def quill_home(request):
    post_list = QuillPost.objects.all()
    context = {
        'post_list': post_list,
    }
    return render(request, "quill_list.html", context)



def quill_create(request):
    if request.method == "POST":
        form = QuillPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("note:quill_home")
    else:
        form = QuillPostForm()
    return render(request, 'quill_create.html', {'form': QuillPostForm()})
'''


