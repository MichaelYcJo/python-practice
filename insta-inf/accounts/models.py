from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill



def user_path(instance, filename):
    from random import choice
    import string
    #대소문자 관계없이 문자를 불러옴 
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1] # 확장자명 추출 
    return 'account/{}/{}.{}'.format(instance.user.username, pid, extension)
    
    

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    
    nickname = models.CharField('별명', max_length=20, unique=True)
    follow_set = models.ManyToManyField('self',
                                        blank=True,
                                        through='Follow',
                                        symmetrical=False,) # 비대칭관계 한쪽만 팔로우를해도 문제가 없게 구현 
                                                            #through : follow_set는 Follew를 통해 생긴다. 

    picture = ProcessedImageField(upload_to=user_path,
                                 processors=[ResizeToFill(150, 150)],
                                 format='JPEG',
                                 options={'quality':90},
                                 blank=True,
                                 null = True,
                                 )
                            
    
    about = models.CharField(max_length=300, blank= True)
    
    GENDER_C = (
    ('선택안함', '선택안함'),
    ('여성', '여성'),
    ('남성', '남성'),
    )
    
    gender = models.CharField('성별(선택사항',
                              max_length=10,
                              choices=GENDER_C,
                              default='N'
                              )
     
    def __str__(self):
        return self.nickname

    # self는 Profile
    @property
    def get_follower(self):
        return [i.from_user for i in self.follower_user.all()]
    
    @property
    def get_following(self):
        return [i.to_user for i in self.follow_user.all()]
    
    @property
    def follower_count(self):
        return len(self.get_follower)
    
    @property
    def following_count(self):
        return len(self.get_following)
    
    
    def is_follower(self, user):
        return user in self.get_follower
    
    def is_following(self, user):
        return user in self.get_following
    

    
    

class Follow(models.Model):
    from_user = models.ForeignKey(Profile,
                                 related_name='follow_user',
                                 on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile,
                               related_name='follower_user',
                               on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{} -> {}".format(self.from_user, self.to_user)
    
    class Meta:
        unique_together = (
            ('from_user', 'to_user')
        )

