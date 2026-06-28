"""
Django admin for the SIFEN electronic invoicing app.
"""
from django.contrib import admin
from django.http import FileResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from apps.invoicing.models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = [
        'descripcion', 'cantidad', 'precio_unitario',
        'tasa_iva', 'subtotal_item', 'iva_item',
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'numero_display', 'receptor_nombre', 'receptor_ruc',
        'total_general_display', 'status_badge', 'issued_at',
        'kude_download_link',
    ]
    list_filter = ['status', 'tipo_documento', 'condicion_venta', 'issued_at']
    search_fields = [
        'cdc', 'receptor_nombre', 'receptor_ruc',
        'order__number', 'timbrado',
    ]
    readonly_fields = [
        'cdc', 'cdc_display_field', 'numero_display', 'issued_at',
        'qr_url', 'kude_download_link', 'status',
        'subtotal_gravado10', 'subtotal_gravado5', 'subtotal_exento',
        'total_iva10', 'total_iva5', 'total_iva', 'total_general',
        'created_at', 'updated_at',
    ]
    inlines = [InvoiceItemInline]
    actions = ['action_issue', 'action_cancel', 'action_regenerate_kude', 'action_resend_email']

    fieldsets = (
        (_('Identificación SIFEN'), {
            'fields': (
                'cdc', 'cdc_display_field', 'numero_display',
                'tipo_documento', 'timbrado', 'timbrado_fecha_inicio',
                'status', 'issued_at',
            )
        }),
        (_('Emisor (configurado en settings)'), {
            'classes': ('collapse',),
            'fields': ('establecimiento', 'punto_expedicion', 'moneda'),
        }),
        (_('Receptor'), {
            'fields': (
                'receptor_tipo_doc', 'receptor_ruc', 'receptor_nombre',
                'receptor_direccion', 'receptor_email',
            )
        }),
        (_('Condición de Venta'), {
            'fields': ('condicion_venta', 'order'),
        }),
        (_('Totales (Gs.)'), {
            'fields': (
                'subtotal_gravado10', 'total_iva10',
                'subtotal_gravado5', 'total_iva5',
                'subtotal_exento', 'total_iva',
                'total_general',
            )
        }),
        (_('KuDE / QR'), {
            'fields': ('kude_pdf', 'kude_download_link', 'qr_url'),
        }),
        (_('Timestamps'), {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/download-kude/',
                self.admin_site.admin_view(self.download_kude_view),
                name='invoicing_invoice_download_kude',
            ),
        ]
        return custom_urls + urls

    def download_kude_view(self, request, pk):
        invoice = self.get_object(request, pk)
        if invoice and invoice.kude_pdf:
            return FileResponse(
                invoice.kude_pdf.open('rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=f"kude_{invoice.numero_display}.pdf",
            )
        self.message_user(request, 'KuDE PDF not available.', messages.ERROR)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    # ── Display helpers ───────────────────────────────────────────────────────

    @admin.display(description=_('Número'))
    def numero_display(self, obj):
        return obj.numero_display

    @admin.display(description=_('Total (Gs.)'))
    def total_general_display(self, obj):
        return f"₲ {obj.total_general:,.0f}"

    @admin.display(description=_('Estado'))
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'issued': '#198754',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description=_('CDC (legible)'))
    def cdc_display_field(self, obj):
        return obj.cdc_display

    @admin.display(description=_('Descargar KuDE'))
    def kude_download_link(self, obj):
        if obj.pk and obj.kude_pdf:
            url = reverse('admin:invoicing_invoice_download_kude', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank">📄 Descargar PDF</a>', url
            )
        return '—'

    # ── Admin actions ─────────────────────────────────────────────────────────

    @admin.action(description=_('Emitir facturas seleccionadas'))
    def action_issue(self, request, queryset):
        from apps.invoicing.services import InvoiceService
        count = 0
        for invoice in queryset.filter(status='draft'):
            try:
                invoice.status = Invoice.STATUS_ISSUED
                from django.utils import timezone
                invoice.issued_at = timezone.now()
                invoice.save(update_fields=['status', 'issued_at'])
                count += 1
            except Exception as exc:
                self.message_user(request, f"Error: {exc}", messages.ERROR)
        self.message_user(request, f"{count} factura(s) emitida(s).")

    @admin.action(description=_('Anular facturas seleccionadas'))
    def action_cancel(self, request, queryset):
        from apps.invoicing.services import InvoiceService
        count = 0
        for invoice in queryset.filter(status='issued'):
            try:
                InvoiceService.cancel_invoice(invoice)
                count += 1
            except Exception as exc:
                self.message_user(request, f"Error: {exc}", messages.ERROR)
        self.message_user(request, f"{count} factura(s) anulada(s).")

    @admin.action(description=_('Regenerar KuDE PDF'))
    def action_regenerate_kude(self, request, queryset):
        from apps.invoicing.services import InvoiceService
        count = 0
        for invoice in queryset:
            if InvoiceService.regenerate_kude(invoice):
                count += 1
        self.message_user(request, f"{count} KuDE(s) regenerado(s).")

    @admin.action(description=_('Reenviar KuDE por email'))
    def action_resend_email(self, request, queryset):
        from apps.invoicing.services import InvoiceService
        count = 0
        for invoice in queryset.filter(status='issued'):
            InvoiceService.send_kude_email_sync(invoice)
            count += 1
        self.message_user(request, f"{count} email(s) enviado(s).")
