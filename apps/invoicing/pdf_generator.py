"""
KuDE PDF Generator for SIFEN electronic invoices.

Generates the KuDE (Kuatia Documento Electrónico), the visual PDF
representation of a SIFEN electronic invoice, including:
  - QR code linking to e-Kuatia portal
  - CDC in readable format
  - Full IVA breakdown
  - DNIT-compliant layout
"""
import io
import os
import qrcode
import base64
from typing import Optional
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from xhtml2pdf import pisa


def _generate_qr_base64(url: str) -> str:
    """
    Generate a QR code image from a URL and return it as a base64-encoded PNG.
    Used for embedding directly in HTML without needing a file URL.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def generate_kude_pdf(invoice) -> Optional[bytes]:
    """
    Generate the KuDE PDF for the given Invoice instance.

    Args:
        invoice: apps.invoicing.Invoice instance with related items loaded

    Returns:
        PDF content as bytes, or None if generation fails.
    """
    # Generate QR code as base64 image
    qr_base64 = ''
    if invoice.qr_url:
        qr_base64 = _generate_qr_base64(invoice.qr_url)

    # Build context for the template
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
        'qr_base64': qr_base64,
        # Emisor data from settings
        'emisor': {
            'razon_social': getattr(settings, 'SIFEN_RAZON_SOCIAL', 'Geek Monde S.A.'),
            'nombre_fantasia': getattr(settings, 'SIFEN_NOMBRE_FANTASIA', 'Geek Monde'),
            'ruc': getattr(settings, 'SIFEN_RUC_EMISOR', '80012345-1'),
            'direccion': getattr(settings, 'SIFEN_DIRECCION', 'Asunción, Paraguay'),
            'telefono': getattr(settings, 'SIFEN_TELEFONO', ''),
            'email': getattr(settings, 'SIFEN_EMAIL', ''),
            'actividad': getattr(settings, 'SIFEN_ACTIVIDAD', ''),
            'tipo_contribuyente': getattr(settings, 'SIFEN_TIPO_CONTRIBUYENTE', '2'),
        },
    }

    html_string = render_to_string('invoicing/kude.html', context)

    result_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=result_buffer)

    if not pisa_status.err:
        return result_buffer.getvalue()

    return None


def save_kude_to_invoice(invoice) -> bool:
    """
    Generate the KuDE PDF and save it to the invoice.kude_pdf field.

    Args:
        invoice: Invoice instance (will be saved)

    Returns:
        True if successful, False otherwise.
    """
    pdf_bytes = generate_kude_pdf(invoice)
    if pdf_bytes is None:
        return False

    filename = f"kude_{invoice.numero_display.replace('-', '_')}_{invoice.cdc[:8]}.pdf"
    invoice.kude_pdf.save(
        filename,
        ContentFile(pdf_bytes),
        save=True,
    )
    return True
