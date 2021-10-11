from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.

class ProductStatus(models.TextChoices):
    SOLD_OUT = 'sold-out', _("재고 소진")
    PLACED = 'placed', _("판매 중")



class Product(models.Model):
    seller = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='products')
    category = models.ForeignKey('products.ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name="product_category")
    name = models.CharField(max_length=200, null=True, blank=True)
    product_image  = models.ImageField(null=True, blank=True, upload_to='products/')
    brand = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(default=0)
    count_in_stock = models.IntegerField(null=True, blank=True, default=0)
    recommendation_rank = models.IntegerField(default=0, null=True)
    product_status = models.CharField(
        max_length=100,
        choices=ProductStatus.choices,
        default=ProductStatus.PLACED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
