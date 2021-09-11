from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200, unique=True)
    email_checked = models.BooleanField(default=False)
    phone = models.CharField(max_length=100, blank=True, null=True)
    special_code = models.CharField(max_length=10, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


    USERNAME_FIELD = "email"


    def __str__(self):
        return str(f'{self.first_name} {self.last_name}')

