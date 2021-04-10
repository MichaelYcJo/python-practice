from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from core import models as core_models
import re


def photo_path(instance, filename):
    from time import strftime
    from random import choice
    import string
    arr = [choice(string.ascii_letters)for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return '{}/{}/{}.{}'.format(strftime('post/%Y/%m/%d'), instance.author.username, pid, extension)


class Post(core_models.TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = ProcessedImageField(upload_to=photo_path,
                                processors=[ResizeToFill(600, 600)],
                                format='JPEG',
                                options={'quality': 90},)
    content = models.CharField(max_length=140, help_text="최대 140자 입력 가능")
    tag_set = models.ManyToManyField('Tag', blank=True )

    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='like_user_set',
                                           through='Like')  # post.like_set 으로 접근 가능, through : like_iser_set은 like를통해 생긴다. 
    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='bookmark_user_set',
                                           through='Bookmark')  # post.bookmark_set 으로 접근 가능

    class Meta:
        ordering = ['-created_at']
        
    
    # content에서 tags를 추출하여, Tag 객체 가져오기, 신규 태그는 Tag instance 생성, 본인의 tag_set에 등록,
    def tag_save(self):
        tags = re.findall(r'#(\w+)\b', self.content) #re.정규표현식(매칭되는 모든것을 찾음)

        if not tags:
            return

        for t in tags:
            tag, tag_created = Tag.objects.get_or_create(name=t)
            self.tag_set.add(tag)  # ManyToManyField 에 인스턴스 추가

#get set에서 get의 역할
    @property
    def like_count(self):
        return self.like_user_set.count()
    
    @property
    def bookmark_count(self):
        return self.bookmark_user_set.count()

    def __str__(self):
        return self.content


class Tag(models.Model):
    name = models.CharField(max_length=140, unique=True)
    
    def __str__(self):
        return self.name


class Like(core_models.TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user', 'post')
        )
        
class Bookmark(core_models.TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user', 'post')
        )


