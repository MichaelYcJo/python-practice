from django.contrib import admin

from products.models import Product, ProductCategory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('seller', 'category', 'name', 'brand', 'is_published', 'created_at')
    list_filter = ('category', 'seller', 'brand')
    search_fields = ('name',)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category')
    list_filter = ('name', 'parent_category')
    search_fields = ('name',)
