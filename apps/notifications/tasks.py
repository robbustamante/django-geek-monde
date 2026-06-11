from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Notification
import logging

logger = logging.getLogger(_name_)


@shared_task
def send_notification_email(notification_id):
    """Envía email de notificación de forma asincrónica."""
    try:
        notification = Notification.objects.get(id=notification_id)

        subject = notification.title
        html_message = render_to_string('notifications/email.html', {
            'notification': notification
        })

        send_mail(
            subject,
            notification.message,
            'noreply@geekmonde.com',
            [notification.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        notification.email_sent = True
        notification.save(update_fields=['email_sent'])

        logger.info(f"Notificación #{notification_id} enviada a {notification.user.email}")

    except Exception as e:
        logger.error(f"Error enviando notificación #{notification_id}: {str(e)}")
        raise


@shared_task
def check_abandoned_carts():
    """Verifica carritos abandonados cada hora."""
    from django.utils.timezone import now
    from datetime import timedelta
    from apps.cart.models import Cart

    abandoned_carts = Cart.objects.filter(
        updated_at__lt=now() - timedelta(hours=2),
        items__isnull=False
    ).distinct()

    for cart in abandoned_carts:
        notification = Notification.objects.create(
            user=cart.user,
            notification_type='abandoned_cart',
            title='¿Olvidaste tu carrito?',
            message=f'Tienes {cart.items.count()} items en tu carrito esperando ser comprados.',
            metadata={'cart_id': cart.id}
        )
        send_notification_email.delay(notification.id)


@shared_task
def check_low_stock():
    """Verifica productos con bajo stock."""
    from apps.inventory.models import StockLevel
    from django.contrib.auth import get_user_model

    LOW_STOCK_THRESHOLD = 10
    User = get_user_model()

    low_stock_items = StockLevel.objects.filter(
        available__lt=LOW_STOCK_THRESHOLD,
        available__gt=0
    )

    admins = User.objects.filter(is_staff=True)

    for stock in low_stock_items:
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type='low_stock',
                title='Alerta: Stock bajo',
                message=f'{stock.product.name} tiene solo {stock.available} unidades disponibles',
                metadata={'product_id': stock.product.id, 'quantity': stock.available}
            )