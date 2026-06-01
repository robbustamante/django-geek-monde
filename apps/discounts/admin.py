from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.core.admin import TimeStampedAdmin
from .models import Coupon, CouponUsage

@admin.register(Coupon)
class CouponAdmin(TimeStampedAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('current_use', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'description', 'is_active')
        }),
        (_('Discount Configuration'), {
            'fields': ('discount_type', 'discount_value', 'max_discount_amount')
        }),
        (_('Validity & Limits'), {
            'fields': ('valid_from', 'valid_until', 'min_purchase_amount', 'max_use', 'usage_limit_per_customer')
        }),
        (_('Statistics'), {
            'fields': ('current_use', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'order', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('coupon__code', 'user__email', 'order__number')
    readonly_fields = ('used_at',)
