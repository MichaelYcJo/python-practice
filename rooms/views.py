from django.utils import timezone
from django.shortcuts import render
from django.views.generic import ListView
from . import models


class HomeView(ListView):

    """ HomeView Definition """

    # 어떤 모델을 list화 할것인가
    model = models.Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context


def room_detail(request, pk):
    print(pk)
    return render(request, "rooms/detail.html")
