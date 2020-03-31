from math import ceil
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage
from . import models


def all_rooms(request):
    # paginator을 사용할경우 default를 1로잡아주기때문에 "page", 1을 따로 선언할 필요 없음
    page = request.GET.get("page", 1)
    room_list = models.Room.objects.all()
    # Paginator(object_list, per_page(페이지당 개수))
    paginator = Paginator(room_list, 10, orphans=5)
    # print(vars(page.paginator))

    try:
        rooms = paginator.page(int(page))
        return render(request, "rooms/home.html", {"page": rooms})
    except EmptyPage:
        return redirect("/")
