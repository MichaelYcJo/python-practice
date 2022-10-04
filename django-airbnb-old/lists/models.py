from django.db import models
from core import models as core_models


class List(core_models.TimeStampedModel):

    """ List Model Definition """

    name = models.CharField(max_length=80)
    # models.OneToOneField()를 사용하면 한 유저는 하나의 리스트만 가질 수 있다.
    # 이는 현재 fav_list가 get_or_create()등을 사용해서 유저가 2개이상의 리스트를 가지면 멀티플에러를 발생시킬 수 있기때문
    user = models.OneToOneField(
        "users.User", related_name="list", on_delete=models.CASCADE
    )
    rooms = models.ManyToManyField("rooms.Room", related_name="lists", blank=True)

    def __str__(self):
        return self.name

    def count_rooms(self):
        return self.rooms.count()

    count_rooms.short_description = "Number of Rooms"
