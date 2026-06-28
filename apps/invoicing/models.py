"""
Models for the SIFEN electronic invoicing app.

Implements the KuDE (Kuatia Documento Electrónico) structure
following DNIT Paraguay SIFEN specifications.

Document types (SIFEN):
    1 - Factura Electrónica
    4 - Autofactura Electrónica
    5 - Nota de Crédito Electrónica
    6 - Nota de Débito Electrónica
    7 - Nota de Remisión Electrónica

IVA types (Paraguay):
    10% - Standard goods and services
    5%  - Basic food items and medicines
    0%  - Exempt (exento)
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.order.models import Order
from apps.invoicing.managers import InvoiceManager


class Invoice(TimeStampedModel):
    """
    Electronic invoice (Factura Electrónica) following SIFEN DNIT Paraguay.
    Stores all data needed to render the KuDE (visual PDF representation).
    """

    # ── Document type choices ────────────────────────────────────────────────
    TIPO_FACTURA = '1'
    TIPO_AUTOFACTURA = '4'
    TIPO_NOTA_CREDITO = '5'
    TIPO_NOTA_DEBITO = '6'
    TIPO_NOTA_REMISION = '7'

    TIPO_DOCUMENTO_CHOICES = [
        (TIPO_FACTURA, _('Factura Electrónica')),
        (TIPO_AUTOFACTURA, _('Autofactura Electrónica')),
        (TIPO_NOTA_CREDITO, _('Nota de Crédito Electrónica')),
        (TIPO_NOTA_DEBITO, _('Nota de Débito Electrónica')),
        (TIPO_NOTA_REMISION, _('Nota de Remisión Electrónica')),
    ]

    # ── Status choices ────────────────────────────────────────────────────────
    STATUS_DRAFT = 'draft'
    STATUS_ISSUED = 'issued'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Borrador')),
        (STATUS_ISSUED, _('Emitida')),
        (STATUS_CANCELLED, _('Anulada')),
    ]

    # ── Condición de venta ────────────────────────────────────────────────────
    CONDICION_CONTADO = '1'
    CONDICION_CREDITO = '2'

    CONDICION_CHOICES = [
        (CONDICION_CONTADO, _('Contado')),
        (CONDICION_CREDITO, _('Crédito')),
    ]

    # ── Receptor type ─────────────────────────────────────────────────────────
    RECEPTOR_RUC = '1'
    RECEPTOR_CEDULA = '2'
    RECEPTOR_PASAPORTE = '3'
    RECEPTOR_INNOMINADO = '4'  # Sin nombre ("Sin Nombre")

    RECEPTOR_TIPO_CHOICES = [
        (RECEPTOR_RUC, _('RUC')),
        (RECEPTOR_CEDULA, _('Cédula de Identidad')),
        (RECEPTOR_PASAPORTE, _('Pasaporte')),
        (RECEPTOR_INNOMINADO, _('Innominado')),
    ]

    # ── Relationships ─────────────────────────────────────────────────────────
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='invoice',
        verbose_name=_('Pedido'),
    )

    objects = InvoiceManager()

    # ── SIFEN document identification ─────────────────────────────────────────
    cdc = models.CharField(
        max_length=44,
        unique=True,
        verbose_name=_('CDC (Código de Control)'),
        help_text=_('44-digit unique identifier (SIFEN)'),
    )
    tipo_documento = models.CharField(
        max_length=1,
        choices=TIPO_DOCUMENTO_CHOICES,
        default=TIPO_FACTURA,
        verbose_name=_('Tipo de Documento'),
    )
    # Número formato SIFEN: 001-001-0000001
    establecimiento = models.CharField(
        max_length=3,
        default='001',
        verbose_name=_('Establecimiento'),
    )
    punto_expedicion = models.CharField(
        max_length=3,
        default='001',
        verbose_name=_('Punto de Expedición'),
    )
    numero_documento = models.PositiveIntegerField(
        verbose_name=_('Número de Documento'),
    )
    timbrado = models.CharField(
        max_length=8,
        verbose_name=_('Timbrado'),
        help_text=_('Authorization number issued by DNIT'),
    )
    timbrado_fecha_inicio = models.DateField(
        verbose_name=_('Timbrado Vigente Desde'),
        null=True,
        blank=True,
    )

    # ── Dates ─────────────────────────────────────────────────────────────────
    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Fecha y Hora de Emisión'),
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name=_('Estado'),
    )

    # ── Receptor data ─────────────────────────────────────────────────────────
    receptor_tipo_doc = models.CharField(
        max_length=1,
        choices=RECEPTOR_TIPO_CHOICES,
        default=RECEPTOR_CEDULA,
        verbose_name=_('Tipo de Doc. Receptor'),
    )
    receptor_ruc = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('RUC / Cédula Receptor'),
    )
    receptor_nombre = models.CharField(
        max_length=255,
        verbose_name=_('Nombre/Razón Social Receptor'),
    )
    receptor_direccion = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Dirección Receptor'),
    )
    receptor_email = models.EmailField(
        blank=True,
        verbose_name=_('Email Receptor'),
    )

    # ── Sale conditions ───────────────────────────────────────────────────────
    condicion_venta = models.CharField(
        max_length=1,
        choices=CONDICION_CHOICES,
        default=CONDICION_CONTADO,
        verbose_name=_('Condición de Venta'),
    )
    moneda = models.CharField(
        max_length=3,
        default='PYG',
        verbose_name=_('Moneda'),
    )

    # ── Tax totals (PYG) ──────────────────────────────────────────────────────
    subtotal_gravado10 = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Subtotal Gravado IVA 10%'),
        help_text=_('Base imponible IVA 10% (precio sin IVA)'),
    )
    subtotal_gravado5 = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Subtotal Gravado IVA 5%'),
        help_text=_('Base imponible IVA 5% (precio sin IVA)'),
    )
    subtotal_exento = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Subtotal Exento'),
    )
    total_iva10 = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Total IVA 10%'),
    )
    total_iva5 = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Total IVA 5%'),
    )
    total_iva = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Total IVA'),
    )
    total_general = models.DecimalField(
        max_digits=14, decimal_places=0, default=0,
        verbose_name=_('Total General'),
    )

    # ── Generated KuDE PDF ───────────────────────────────────────────────────
    kude_pdf = models.FileField(
        upload_to='invoices/kude/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_('KuDE PDF'),
    )

    # ── QR data ───────────────────────────────────────────────────────────────
    qr_url = models.URLField(
        blank=True,
        verbose_name=_('URL QR e-Kuatia'),
        help_text=_('URL for QR code pointing to e-Kuatia portal'),
    )

    class Meta:
        verbose_name = _('Factura Electrónica')
        verbose_name_plural = _('Facturas Electrónicas')
        ordering = ('-issued_at', '-created_at')

    def __str__(self):
        return f"{self.get_numero_display()} - {self.receptor_nombre}"

    @property
    def numero_display(self):
        """Return formatted invoice number: 001-001-0000001"""
        return f"{self.establecimiento}-{self.punto_expedicion}-{str(self.numero_documento).zfill(7)}"

    @property
    def cdc_display(self):
        """Return CDC formatted in groups of 4 for readability."""
        from apps.invoicing.cdc_generator import format_cdc_display
        return format_cdc_display(self.cdc)

    def get_numero_display(self):
        return self.numero_display


class InvoiceItem(TimeStampedModel):
    """
    A single line item in an electronic invoice.
    Linked to the Order's items with IVA classification.
    """

    # IVA rate choices for Paraguay
    IVA_10 = '10'
    IVA_5 = '5'
    IVA_EXENTO = '0'

    IVA_RATE_CHOICES = [
        (IVA_10, _('Gravado 10%')),
        (IVA_5, _('Gravado 5%')),
        (IVA_EXENTO, _('Exento')),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Factura'),
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name=_('Descripción'),
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Cantidad'),
    )
    precio_unitario = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        verbose_name=_('Precio Unitario (con IVA)'),
    )
    tasa_iva = models.CharField(
        max_length=2,
        choices=IVA_RATE_CHOICES,
        default=IVA_10,
        verbose_name=_('Tasa IVA'),
    )
    subtotal_item = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        verbose_name=_('Subtotal'),
    )
    iva_item = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name=_('IVA del ítem'),
    )

    class Meta:
        verbose_name = _('Ítem de Factura')
        verbose_name_plural = _('Ítems de Factura')
        ordering = ('id',)

    def __str__(self):
        return f"{self.cantidad} x {self.descripcion}"

    @property
    def tasa_iva_display(self):
        if self.tasa_iva == self.IVA_10:
            return '10%'
        elif self.tasa_iva == self.IVA_5:
            return '5%'
        return 'Exento'
