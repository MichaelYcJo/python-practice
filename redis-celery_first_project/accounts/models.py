from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    total_account = models.IntegerField(default=0,  verbose_name='총 보유 계좌')
    fee_free_of_day = models.IntegerField(default=3, verbose_name='일당 수수료 면제 카운트')
    
    REQUIRED_FIELDS = ['total_account', 'fee_free_of_day']
    
    class Meta:
        verbose_name = '유저 정보'
        verbose_name_plural = '유저 정보'