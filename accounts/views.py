from django.shortcuts import render
from django.http import HttpResponse


def hello_world(request):
    template = 'base.html'
    return render(request, template)
