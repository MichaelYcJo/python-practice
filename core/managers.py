from django.db import models
from django.contrib.auth.models import UserManager


class CustomModelManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

# superuser을 만드는 create_super()은 UserManager에 내장되어있는 메소드임
class CustomUserManager(CustomModelManager, UserManager):
    pass