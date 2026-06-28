"""
Django signal to auto-trigger invoice generation when a payment is completed.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def connect_payment_signal():
    """
    Connect the payment signal. Called from InvoicingConfig.ready().
    We import Payment here to avoid circular imports at module level.
    """
    from apps.payment.models import Payment

    @receiver(post_save, sender=Payment, weak=False)
    def on_payment_completed(sender, instance, created, **kwargs):
        """
        When a Payment transitions to 'completed', trigger invoice generation.
        Uses Celery for async processing; falls back to synchronous if unavailable.
        """
        if instance.status != 'completed':
            return

        order = instance.order

        # Guard: don't generate if invoice already exists
        if hasattr(order, 'invoice'):
            logger.debug(
                "Order %s already has an invoice. Skipping signal.", order.number
            )
            return

        logger.info(
            "Payment completed for order %s — triggering invoice generation.",
            order.number,
        )

        try:
            from apps.invoicing.tasks import generate_invoice_task
            generate_invoice_task.delay(order.pk)
        except Exception as exc:
            logger.warning(
                "Celery unavailable (%s). Generating invoice synchronously.", exc
            )
            try:
                from apps.invoicing.services import InvoiceService
                InvoiceService.issue_invoice(order)
            except Exception as service_exc:
                logger.exception(
                    "Failed to generate invoice for order %s: %s",
                    order.number,
                    service_exc,
                )


# Connect immediately when this module is imported (called from apps.py ready())
connect_payment_signal()
