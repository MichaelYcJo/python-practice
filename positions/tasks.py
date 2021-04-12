from celery import shared_task
from .models import Test
from .utils import get_random_code

from celery.decorators import periodic_task
from celery.task.schedules import crontab

@shared_task
def create_test_object(name):
    Test.objects.create(name=name)


@shared_task
def create_all_codes():
    for test in Test.objects.all():
        test.code = get_random_code()
        test.save()


@periodic_task(run_every=(crontab(minute='*/1')))
def run_create_objs():
    create_test_object.delay(name='new2020')