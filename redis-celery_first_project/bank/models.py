from django.db import models


class BankAccountType(models.Model):

    account_type = models.CharField(max_length=10, verbose_name='계좌 종류(예금, 적금)')
    default_limit_onetime = models.IntegerField(verbose_name=' 1회 출금한도')
    default_limit_oneday = models.IntegerField(verbose_name='1일 출금한도')

    def __str__(self):
        return self.account_type
    
    class Meta:
        verbose_name = '계좌 종류'
        verbose_name_plural = '계좌 종류'


class BankAccount(models.Model):
    uuid = models.CharField(max_length=100, unique=True, verbose_name='고유 uuid')
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, verbose_name='회원 아이디')
    bank_code = models.CharField(max_length=5, verbose_name='은행 코드')
    account_number = models.CharField(max_length=20, verbose_name='계좌번호')
    account_type = models.ForeignKey('BankAccountType', on_delete=models.DO_NOTHING, verbose_name='계좌 종류')
    amount = models.IntegerField(default=0, verbose_name='총 보유액')
    is_active = models.BooleanField(default=True, verbose_name='계좌 유효성')
    
    
    def __str__(self):
        return self.uuid

    class Meta:
        verbose_name = '계좌정보'
        verbose_name_plural = '계좌정보'
        


class AccountTransferHistory(models.Model):
    
    sender_account = models.ForeignKey('BankAccount', related_name='sender_account', on_delete=models.DO_NOTHING, verbose_name='발신 계좌번호')
    receiver_account = models.ForeignKey('BankAccount', related_name='receiver_account', on_delete=models.DO_NOTHING, verbose_name='수신 계좌번호')
    sended_label = models.CharField(max_length=20, verbose_name='보낼 때 작성할 문구')
    received_label = models.CharField(max_length=20, verbose_name='받을 때 작성할 문구')
    amount = models.IntegerField(verbose_name='송금액')
    fee =  models.IntegerField(verbose_name='수수료')
    reg_date = models.DateField(auto_now_add=True, verbose_name='송금 날짜')
    

    class Meta: 
        verbose_name = '이체 내역'
        verbose_name_plural = '이체 내역'