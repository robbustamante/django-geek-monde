from django.contrib import admin
from .models import Shipping


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'tracking_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__number', 'tracking_number')
    readonly_fields = ('created_at', 'updated_at')
