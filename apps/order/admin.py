from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'unit_price')
    readonly_fields = ('product', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
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

    actions = ['action_generate_invoice']

    @admin.action(description=_('Generar Factura para Órdenes Seleccionadas'))
    def action_generate_invoice(self, request, queryset):
        from apps.invoicing.services import InvoiceService
        count = 0
        errors = 0
        for order in queryset:
            if not hasattr(order, 'invoice'):
                try:
                    InvoiceService.issue_invoice(order)
                    count += 1
                except Exception as e:
                    errors += 1
                    self.message_user(request, f"Error en orden {order.number}: {e}", level='error')
        
        if count > 0:
            self.message_user(request, f"Se generaron {count} facturas correctamente.")
        elif errors == 0:
            self.message_user(request, "Las órdenes seleccionadas ya tenían factura.", level='warning')
