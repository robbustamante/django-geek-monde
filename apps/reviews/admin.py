"""
Admin configuration for the reviews app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import TimeStampedAdmin
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    """Inline admin for review images."""
    model = ReviewImage
    extra = 0
    fields = ('image', 'caption')


@admin.register(Review)
class ReviewAdmin(TimeStampedAdmin):
    list_display = ('product', 'author', 'rating', 'title', 'verified_purchase', 'helpful_count', 'created_at')
    list_filter = ('rating', 'verified_purchase', 'created_at')
    search_fields = ('title', 'body', 'author__email', 'product__name')
    readonly_fields = ('created_at', 'updated_at', 'helpful_count')
    inlines = [ReviewImageInline]

    fieldsets = (
        (_('Review'), {
            'fields': ('product', 'author', 'rating', 'title', 'body')
        }),
        (_('Status'), {
            'fields': ('verified_purchase', 'helpful_count')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
