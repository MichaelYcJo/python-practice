  
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Post, Comment, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["photo_tag", "caption"]
    list_display_links = ["caption"] #caption에서 링크달림 

    def photo_tag(self, post):
        return mark_safe(f"<img src={post.photo.url} style='width: 100px;' />")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass