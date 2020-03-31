from math import ceil
from django.shortcuts import render
from . import models


def all_rooms(request):
    page = request.GET.get("page", 1)
    page = int(page or 1)
    page_size = 10
    limit = page_size * page
    offset = limit - page_size
    all_rooms = models.Room.objects.all()[offset:limit]
    page_count = ceil(models.Room.objects.count() / page_size)
    return render(
        request,
        "rooms/home.html",
        {
            "potato": all_rooms,
            "page": page,
            "page_count": page_count,
            # 템플릿에선 range함수를 사용할수 없으므로 만들어서 보내줌
            "page_range": range(1, page_count),
        },
    )
