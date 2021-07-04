from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug']
    
    # 2개의 필드를 섞어서 하나로 만들어줌
    prepopulated_fields = {'slug':['name']}

admin.site.register(Category, CategoryAdmin)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','slug','category','price','stock','available_display','available_order','created','updated']
    list_filter = ['available_display','created','updated','category']
    prepopulated_fields = {'slug':('name',)}
    list_editable = ['price','stock','available_display','available_order']