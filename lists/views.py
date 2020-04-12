from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rooms import models as room_models
from . import models


@login_required
def toggle_room(request, room_pk):
    action = request.GET.get("action", None)
    room = room_models.Room.objects.get_or_none(pk=room_pk)
    if room is not None and action is not None:
        # 첫번째는 사용하려는 모델의 인스턴스, 두번째는 boolean flag이다.
        # get_or_create는 한개만 찾기때문에 유저의 리스트가 복수개라면 에러가 발생한다.(multiple objects have been returned)
        the_list, _ = models.List.objects.get_or_create(
            user=request.user, name="My Favourites Houses"
        )
        if action == "add":
            the_list.rooms.add(room)
        elif action == "remove":
            the_list.rooms.remove(room)
    return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))


class SeeFavsView(TemplateView):

    template_name = "lists/list_detail.html"


"""
def see_favs(request):
    user = request.user
    user.lists.all()
"""
