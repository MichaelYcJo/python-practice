from django.shortcuts import render,redirect, get_object_or_404
from .forms import TinyForm
from .models import Tinynote



def tiny_create(request):
    if request.method == "POST":
        form = TinyForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect("note:home")
    else:
        form = TinyForm()
    context = {
        'form' : form
    }
    return render(request, 'tiny_form.html', context)

