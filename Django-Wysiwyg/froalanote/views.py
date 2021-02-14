from django.shortcuts import render,redirect, get_object_or_404
from .forms import FroalaForm
from .models import FroalaPost

def froala_home(request):
    post_list = FroalaPost.objects.all()
    context = {
        'post_list': post_list,
    }
    return render(request, "froala_list.html", context)



def froala_create(request):
    if request.method == "POST":
        form = FroalaForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("froalanote:froala_home")
    else:
        form = FroalaForm()
    return render(request, 'froala_create.html', {'form': FroalaForm()})
