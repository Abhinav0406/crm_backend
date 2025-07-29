from django.contrib import admin
from .models import Product, Category, ProductVariant

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'status', 'quantity', 'tenant')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'status', 'tenant')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'tenant', 'is_active')
    search_fields = ('name',)
    list_filter = ('tenant', 'is_active')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'product', 'quantity', 'is_active')
    search_fields = ('name', 'sku')
    list_filter = ('product', 'is_active')
