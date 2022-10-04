import datetime
from django import template
from reservations import models as reservation_models

register = template.Library()

# simpletag(takes_context=True) 면 장고가 전달하는 user나 다른 context를 받을 수 있다.
@register.simple_tag
def is_booked(room, day):
    if day.number == 0:
        return
    try:
        date = datetime.datetime(year=day.year, month=day.month, day=day.number)
        # 결과적으로 template으로부터 얻어온 day의 bookedDay를 얻게됨
        reservation_models.BookedDay.objects.get(day=date, reservation__room=room)
        return True
    except reservation_models.BookedDay.DoesNotExist:
        return False
