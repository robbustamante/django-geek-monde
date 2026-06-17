from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import TimeStampedAdmin
from .models import Category, Product, ProductVariant


@admin.register(Category)
class CategoryAdmin(TimeStampedAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name',)


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'sku', 'price_adjustment', 'is_active')


@admin.register(Product)
class ProductAdmin(TimeStampedAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'geek_category', 'clothing_type', 'is_active', 'created_at')
    list_filter = ('category', 'geek_category', 'clothing_type', 'is_active', 'created_at')
    search_fields = ('name', 'sku', 'description', 'franchise', 'character_name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        (_('Organization'), {
            'fields': ('category',)
        }),
        (_('Geek Details'), {
            'fields': ('geek_category', 'franchise', 'character_name'),
            'description': _('Anime, Gaming, Movies, or other geek culture details')
        }),
        (_('Clothing Details'), {
            'fields': ('clothing_type', 'gender_fit', 'size', 'color', 'material'),
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


@admin.register(ProductVariant)
class ProductVariantAdmin(TimeStampedAdmin):
    list_display = ('product', 'size', 'color', 'sku', 'price_adjustment', 'is_active')
    list_filter = ('product', 'size', 'color', 'is_active', 'created_at')
    search_fields = ('product__name', 'sku', 'color')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Product & Variant'), {
            'fields': ('product', 'size', 'color', 'sku')
        }),
        (_('Pricing'), {
            'fields': ('price_adjustment',),
            'description': _('Additional cost for this specific variant')
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
