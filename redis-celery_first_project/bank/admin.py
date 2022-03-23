from django.contrib import admin
from bank.models import BankAccount, BankAccountType, AccountTransferHistory




@admin.register(BankAccount)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'amount', 'bank_code', 'account_type')
    


@admin.register(AccountTransferHistory)
class AccountTransferReportAdmin(admin.ModelAdmin):
    list_display = ('sender_account', 'receiver_account', 'sended_label', 'received_label', 'amount', 'fee', 'reg_date')


admin.site.register(BankAccountType)