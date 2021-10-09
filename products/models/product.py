from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Product(models.Model):
    seller = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    product_image  = models.ImageField(null=True, blank=True, upload_to='products/')
    brand = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True)
    countInStock = models.IntegerField(null=True, blank=True, default=0)
    recommendation_rank = models.IntegerField(default=0, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
