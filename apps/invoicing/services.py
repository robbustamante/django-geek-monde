"""
Invoice service layer for SIFEN electronic invoices.
Orchestrates: creation → PDF generation → email dispatch.
"""
import logging
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Service class to manage the full lifecycle of a SIFEN electronic invoice:
    creation, issuance, KuDE generation, email dispatch and cancellation.
    """

    @staticmethod
    def issue_invoice(order):
        """
        Create and issue an electronic invoice for a given order.

        Steps:
          1. Create Invoice + InvoiceItems from order
          2. Mark as 'issued' with current timestamp
          3. Generate KuDE PDF
          4. Send KuDE by email to customer (async via Celery if available)

        Args:
            order: apps.order.Order instance

        Returns:
            Invoice instance (status='issued')

        Raises:
            ValueError: If order already has an invoice
        """
        from apps.invoicing.models import Invoice
        from apps.invoicing.pdf_generator import save_kude_to_invoice

        # Guard: don't duplicate invoices
        if hasattr(order, 'invoice') and order.invoice is not None:
            logger.warning(
                "Order %s already has an invoice (%s). Skipping.",
                order.number,
                order.invoice.cdc,
            )
            return order.invoice

        try:
            # 1. Create invoice
            invoice = Invoice.objects.create_from_order(order)

            # 2. Mark as issued
            invoice.status = Invoice.STATUS_ISSUED
            invoice.issued_at = timezone.now()
            invoice.save(update_fields=['status', 'issued_at'])

            logger.info(
                "Invoice created: %s for order %s",
                invoice.numero_display,
                order.number,
            )

            # 3. Generate KuDE PDF
            pdf_ok = save_kude_to_invoice(invoice)
            if not pdf_ok:
                logger.error(
                    "Failed to generate KuDE PDF for invoice %s",
                    invoice.cdc,
                )

            # 4. Send email (try async with Celery, fallback to sync)
            InvoiceService._send_kude_email(invoice)

            return invoice

        except Exception as exc:
            logger.exception(
                "Error issuing invoice for order %s: %s",
                order.number,
                exc,
            )
            raise

    @staticmethod
    def _send_kude_email(invoice):
        """
        Dispatch KuDE PDF by email to the customer.
        Attempts Celery task first; falls back to synchronous send.
        """
        try:
            from apps.invoicing.tasks import send_kude_email_task
            send_kude_email_task.delay(invoice.pk)
        except Exception:
            # Celery not available; send synchronously
            InvoiceService.send_kude_email_sync(invoice)

    @staticmethod
    def send_kude_email_sync(invoice):
        """
        Send KuDE PDF by email synchronously using Django's email backend.
        """
        if not invoice.receptor_email:
            logger.warning(
                "No email for invoice %s recipient. Skipping email.",
                invoice.cdc,
            )
            return

        subject = (
            f"Factura Electrónica N° {invoice.numero_display} — "
            f"{getattr(settings, 'SIFEN_RAZON_SOCIAL', 'Geek Monde S.A.')}"
        )
        body = (
            f"Estimado/a {invoice.receptor_nombre},\n\n"
            f"Adjunto encontrará su Factura Electrónica N° {invoice.numero_display}.\n\n"
            f"CDC: {invoice.cdc}\n"
            f"Fecha de emisión: {invoice.issued_at.strftime('%d/%m/%Y %H:%M') if invoice.issued_at else '-'}\n"
            f"Total: {invoice.total_general:,.0f} Gs.\n\n"
            f"Puede verificar este documento en: {invoice.qr_url}\n\n"
            f"Gracias por su compra.\n"
            f"{getattr(settings, 'SIFEN_RAZON_SOCIAL', 'Geek Monde S.A.')}"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@geek-monde.com.py'),
            to=[invoice.receptor_email],
        )

        if invoice.kude_pdf:
            invoice.kude_pdf.open('rb')
            email.attach(
                filename=f"factura_{invoice.numero_display}.pdf",
                content=invoice.kude_pdf.read(),
                mimetype='application/pdf',
            )
            invoice.kude_pdf.close()

        try:
            email.send(fail_silently=False)
            logger.info(
                "KuDE email sent for invoice %s to %s",
                invoice.cdc,
                invoice.receptor_email,
            )
        except Exception as exc:
            logger.error(
                "Failed to send KuDE email for invoice %s: %s",
                invoice.cdc,
                exc,
            )

    @staticmethod
    def cancel_invoice(invoice, motivo=''):
        """
        Cancel an issued invoice.

        Args:
            invoice: Invoice instance to cancel
            motivo: Cancellation reason (optional)

        Returns:
            Updated Invoice instance
        """
        from apps.invoicing.models import Invoice

        if invoice.status != Invoice.STATUS_ISSUED:
            raise ValueError(
                f"Cannot cancel invoice with status '{invoice.status}'. "
                "Only 'issued' invoices can be cancelled."
            )

        invoice.status = Invoice.STATUS_CANCELLED
        invoice.save(update_fields=['status'])
        logger.info("Invoice %s cancelled. Motivo: %s", invoice.cdc, motivo)
        return invoice

    @staticmethod
    def regenerate_kude(invoice):
        """
        Regenerate the KuDE PDF for an existing invoice.
        Useful if the template was updated or PDF was lost.

        Args:
            invoice: Invoice instance

        Returns:
            True if successful, False otherwise
        """
        from apps.invoicing.pdf_generator import save_kude_to_invoice

        # Delete existing PDF if present
        if invoice.kude_pdf:
            invoice.kude_pdf.delete(save=False)

        return save_kude_to_invoice(invoice)
