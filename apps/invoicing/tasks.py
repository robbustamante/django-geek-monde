"""
Celery tasks for asynchronous invoice processing.
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_invoice_task(self, order_id: int):
    """
    Asynchronously generate and issue an electronic invoice for an order.

    Args:
        order_id: Primary key of the Order instance
    """
    from apps.order.models import Order
    from apps.invoicing.services import InvoiceService

    try:
        order = Order.objects.select_related(
            'user', 'shipping_address'
        ).prefetch_related('items__product').get(pk=order_id)

        InvoiceService.issue_invoice(order)

        logger.info("Invoice generated successfully for order %s", order.number)

    except Order.DoesNotExist:
        logger.error("Order %d not found. Cannot generate invoice.", order_id)

    except Exception as exc:
        logger.exception(
            "Error generating invoice for order %d: %s", order_id, exc
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_kude_email_task(self, invoice_id: int):
    """
    Asynchronously send the KuDE PDF by email to the customer.

    Args:
        invoice_id: Primary key of the Invoice instance
    """
    from apps.invoicing.models import Invoice
    from apps.invoicing.services import InvoiceService

    try:
        invoice = Invoice.objects.select_related('order__user').get(pk=invoice_id)
        InvoiceService.send_kude_email_sync(invoice)

    except Invoice.DoesNotExist:
        logger.error("Invoice %d not found. Cannot send KuDE email.", invoice_id)

    except Exception as exc:
        logger.exception(
            "Error sending KuDE email for invoice %d: %s", invoice_id, exc
        )
        raise self.retry(exc=exc)
