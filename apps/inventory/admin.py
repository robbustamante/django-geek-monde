from django.contrib import admin
from .models import Stock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reserved', 'available', 'created_at')
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('created_at', 'updated_at')
