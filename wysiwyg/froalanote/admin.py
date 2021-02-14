from django.contrib import admin
from django.utils.html import mark_safe
from . import models

'''
@admin.register(models.QuillPost)
class QuillPostAdmin(admin.ModelAdmin):
    pass
'''

@admin.register(models.FroalaPost)
class PostAdmin(admin.ModelAdmin):

    """ Item Admin Definition """

    list_display = ("title", "content")

