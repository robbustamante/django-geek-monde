from django.contrib import admin
from .models import StockLevel, StockMovement


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reserved', 'available', 'created_at')
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('stock', 'movement_type', 'quantity', 'reason', 'created_at')
    list_filter = ('movement_type',)
    search_fields = ('stock__product__name', 'reason')
    readonly_fields = ('created_at', 'updated_at')
