from django.contrib import admin
from django_fsm_admin.mixins import FSMTransitionMixin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'unit_price')
    readonly_fields = ('product', 'unit_price')


@admin.register(Order)
class OrderAdmin(FSMTransitionMixin, admin.ModelAdmin):
    list_display = ('number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('number', 'user__email')
    readonly_fields = ('number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        (_('Order Information'), {
            'fields': ('number', 'user', 'status')
        }),
        (_('Totals'), {
            'fields': ('total_amount',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
