from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.order.models import Order
from apps.payment.models import Payment
from .models import Notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Crea notificación cuando se crea o cambia el estado de una orden."""
    notification = None

    if created:
        notification = Notification.objects.create(
            user=instance.user,
            notification_type='order_confirmed',
            title='¡Orden confirmada!',
            message=f'Tu orden #{instance.number} ha sido confirmada.',
            order=instance,
        )
    else:
        if instance.status == 'shipped':
            notification = Notification.objects.create(
                user=instance.user,
                notification_type='order_shipped',
                title='¡Tu orden está en camino!',
                message=f'Orden #{instance.number} ha sido enviada.',
                order=instance,
            )
        elif instance.status == 'delivered':
            notification = Notification.objects.create(
                user=instance.user,
                notification_type='order_delivered',
                title='¡Orden entregada!',
                message=f'Orden #{instance.number} ha sido entregada exitosamente.',
                order=instance,
            )

    if notification:
        logger.info(f"Notificación creada: {notification.title} para {instance.user}")


@receiver(post_save, sender=Payment)
def payment_completed(sender, instance, **kwargs):
    """Notifica cuando un pago se completa."""
    if instance.status == 'completed':
        notification = Notification.objects.create(
            user=instance.order.user,
            notification_type='payment_received',
            title='¡Pago recibido!',
            message=(
                f'Hemos recibido tu pago de ${instance.amount} '
                f'para la orden #{instance.order.number}'
            ),
            order=instance.order,
        )
        logger.info(f"Notificación de pago creada: {notification.title}")