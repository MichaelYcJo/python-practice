from django.contrib import admin

from products.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('seller', 'category', 'name', 'brand', 'is_published', 'created_at')
    list_filter = ('category', 'seller', 'brand')
    search_fields = ('name',)
