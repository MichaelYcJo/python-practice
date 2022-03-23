from django.contrib import admin

from accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'total_account', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name','last_name',)}),
        ('Bank Setting', {'fields': ('total_account','fee_free_of_day')}),
    )
