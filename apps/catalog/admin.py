from django.contrib import admin
from apps.core.admin import TimeStampedAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(TimeStampedAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(TimeStampedAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        (_('Organization'), {
            'fields': ('category',)
        }),
        (_('Pricing'), {
            'fields': ('price',)
        }),
        (_('Media'), {
            'fields': ('image',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
