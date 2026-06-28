"""
Manager for Invoice model.
Handles creation of invoices from orders with SIFEN-compliant logic.
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.invoicing.cdc_generator import generate_cdc


class InvoiceManager(models.Manager):
    """
    Custom manager for Invoice model.
    """

    def get_next_numero(self, establecimiento, punto_expedicion):
        """
        Get the next sequential document number for the given
        establishment and dispatch point.
        """
        last = (
            self.filter(
                establecimiento=establecimiento,
                punto_expedicion=punto_expedicion,
            )
            .order_by('-numero_documento')
            .first()
        )
        if last:
            return last.numero_documento + 1
        return 1

    def create_from_order(self, order):
        """
        Create a SIFEN-compliant Invoice from an Order instance.

        - Generates CDC 44 digits
        - Calculates IVA breakdown (10%, 5%, exento) per order item
        - Creates associated InvoiceItem records
        - Builds QR URL for e-Kuatia portal

        Args:
            order: apps.order.Order instance (must have items and user)

        Returns:
            Invoice instance (not yet issued — status='draft')
        """
        from apps.invoicing.models import Invoice, InvoiceItem

        # ── SIFEN settings from Django config ─────────────────────────────
        timbrado = getattr(settings, 'SIFEN_TIMBRADO', '12345678')
        establecimiento = getattr(settings, 'SIFEN_ESTABLECIMIENTO', '001')
        punto_expedicion = getattr(settings, 'SIFEN_PUNTO_EXPEDICION', '001')
        ruc_emisor = getattr(settings, 'SIFEN_RUC_EMISOR', '80012345-1')
        ekuatia_url = getattr(settings, 'SIFEN_EKUATIA_URL', 'https://ekuatia.set.gov.py/consultas/qr')

        # ── Determine next document number ────────────────────────────────
        numero_doc = self.get_next_numero(establecimiento, punto_expedicion)
        now = timezone.now()

        # ── Generate CDC ──────────────────────────────────────────────────
        # Extract numeric part of RUC (remove DV and hyphens)
        ruc_sin_dv = ruc_emisor.split('-')[0].replace('.', '')

        cdc = generate_cdc(
            ruc_emisor=ruc_sin_dv,
            tipo_documento='01',
            establecimiento=establecimiento,
            punto_expedicion=punto_expedicion,
            numero_documento=str(numero_doc).zfill(7),
            timbrado=timbrado,
            fecha_emision=now,
        )

        # ── Build QR URL ──────────────────────────────────────────────────
        qr_url = f"{ekuatia_url}?nVersion=150&Id={cdc}"

        # ── Determine receptor data ───────────────────────────────────────
        user = order.user
        receptor_nombre = (
            user.get_full_name() or user.email or 'Consumidor Final'
        )
        receptor_ruc = getattr(user, 'ruc', '') or ''
        receptor_tipo = (
            Invoice.RECEPTOR_RUC if receptor_ruc else Invoice.RECEPTOR_INNOMINADO
        )
        receptor_direccion = ''
        if order.shipping_address:
            addr = order.shipping_address
            receptor_direccion = (
                f"{addr.street_address}, {addr.city}, {addr.state}"
            )
            receptor_nombre = addr.name or receptor_nombre

        # ── Calculate IVA per item ────────────────────────────────────────
        subtotal_gravado10 = 0
        subtotal_gravado5 = 0
        subtotal_exento = 0
        total_iva10 = 0
        total_iva5 = 0
        total_general = 0

        item_data_list = []
        for order_item in order.items.select_related('product').all():
            precio_unit = int(order_item.unit_price)
            cantidad = order_item.quantity
            subtotal = precio_unit * cantidad
            total_general += subtotal

            # Default: 10% IVA for all products
            # In production, this would come from product.iva_type field
            tasa_iva = getattr(order_item.product, 'iva_type', InvoiceItem.IVA_10)
            if tasa_iva not in [InvoiceItem.IVA_10, InvoiceItem.IVA_5, InvoiceItem.IVA_EXENTO]:
                tasa_iva = InvoiceItem.IVA_10

            if tasa_iva == InvoiceItem.IVA_10:
                # In Paraguay: price already includes IVA
                # IVA 10% = total * 10 / 110
                iva_item = round(subtotal * 10 / 110)
                base_item = subtotal - iva_item
                subtotal_gravado10 += base_item
                total_iva10 += iva_item
            elif tasa_iva == InvoiceItem.IVA_5:
                # IVA 5% = total * 5 / 105
                iva_item = round(subtotal * 5 / 105)
                base_item = subtotal - iva_item
                subtotal_gravado5 += base_item
                total_iva5 += iva_item
            else:
                iva_item = 0
                subtotal_exento += subtotal

            item_data_list.append({
                'descripcion': order_item.product.name,
                'cantidad': cantidad,
                'precio_unitario': precio_unit,
                'tasa_iva': tasa_iva,
                'subtotal_item': subtotal,
                'iva_item': iva_item,
            })

        total_iva = total_iva10 + total_iva5

        # ── Create Invoice ────────────────────────────────────────────────
        invoice = self.create(
            order=order,
            cdc=cdc,
            tipo_documento=Invoice.TIPO_FACTURA,
            establecimiento=establecimiento,
            punto_expedicion=punto_expedicion,
            numero_documento=numero_doc,
            timbrado=timbrado,
            receptor_tipo_doc=receptor_tipo,
            receptor_ruc=receptor_ruc,
            receptor_nombre=receptor_nombre,
            receptor_direccion=receptor_direccion,
            receptor_email=user.email,
            condicion_venta=Invoice.CONDICION_CONTADO,
            moneda='PYG',
            subtotal_gravado10=subtotal_gravado10,
            subtotal_gravado5=subtotal_gravado5,
            subtotal_exento=subtotal_exento,
            total_iva10=total_iva10,
            total_iva5=total_iva5,
            total_iva=total_iva,
            total_general=total_general,
            qr_url=qr_url,
            status=Invoice.STATUS_DRAFT,
        )

        # ── Create InvoiceItems ───────────────────────────────────────────
        invoice_items = [
            InvoiceItem(invoice=invoice, **item_data)
            for item_data in item_data_list
        ]
        InvoiceItem.objects.bulk_create(invoice_items)

        return invoice
