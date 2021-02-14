from django.db import models
from datetime import datetime
from django.template.defaultfilters import slugify
from django.utils.text import slugify


class Categories(models.TextChoices):
        WORLD = 'world'
        ENVIRONMENT = 'environment'
        TECHNOLOGY = 'technology'
        DESIGN = 'design'
        CULTURE = 'culture'
        BUSINESS = 'business'
        POLITICS = 'politics'
        OPINION = 'opinion'
        SCIENCE = 'science'
        HEALTH = 'health'
        STYLE = 'style'
        TRAVEL = 'travel'

class BlogPost(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    category = models.CharField(max_length=50, choices=Categories.choices, default=Categories.WORLD)
    thumbnail = models.ImageField(upload_to='photos/%Y/%m/%d/')
    excerpt = models.CharField(max_length=150, blank=False)  # 한줄 요약과같은 모델필드
    month = models.CharField(max_length=3)
    day = models.CharField(max_length=2)
    content = models.TextField()
    featured = models.BooleanField(default=False) #추천
    date_created = models.DateTimeField(default=datetime.now, blank=True)

    def save(self, *args, **kwargs):
        original_slug = slugify(self.title)
        queryset = BlogPost.objects.all().filter(slug__iexact=original_slug).count()

        count = 1
        slug = original_slug 

    #무한 루프 돌면서 다시 하단의 쿼리가 0 (=False) 가 될때까지 슬러그에 +=1 되는 형태
        while(queryset):
            slug = original_slug + '-' + str(count)
            count += 1
            queryset = BlogPost.objects.all().filter(slug__iexact=slug).count()
        
        self.slug = slug
            
        # 다른글을 추천하면 이전의 추천글은 취소됨     
        if self.featured:
            try:
                temp = BlogPost.objects.get(featured=True)
                if self != temp:
                    temp.featured = False
                    temp.save()
            except BlogPost.DoesNotExist:
                pass
        super(BlogPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title