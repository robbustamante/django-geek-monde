from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """Modelo de notificaciones para usuarios."""

    class NotificationType(models.TextChoices):
        ORDER_CONFIRMED = 'order_confirmed', _('Orden confirmada')
        ORDER_SHIPPED = 'order_shipped', _('Orden enviada')
        ORDER_DELIVERED = 'order_delivered', _('Orden entregada')
        ORDER_CANCELLED = 'order_cancelled', _('Orden cancelada')
        PAYMENT_RECEIVED = 'payment_received', _('Pago recibido')
        PAYMENT_FAILED = 'payment_failed', _('Pago fallido')
        ABANDONED_CART = 'abandoned_cart', _('Carrito abandonado')
        LOW_STOCK = 'low_stock', _('Stock bajo')
        GENERAL = 'general', _('General')

    user = models.ForeignKey(
        'email_auth.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Usuario'),
    )
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Orden'),
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        verbose_name=_('Tipo'),
    )
    title = models.CharField(max_length=255, verbose_name=_('Título'))
    message = models.TextField(verbose_name=_('Mensaje'))
    is_read = models.BooleanField(default=False, verbose_name=_('Leída'))
    email_sent = models.BooleanField(default=False, verbose_name=_('Email enviado'))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_('Metadata'))

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ('-created_at',)

    def _str_(self):
        return f"[{self.notification_type}] {self.title} → {self.user}"

    def mark_as_read(self):
        """Marca la notificación como leída."""
        self.is_read = True
        self.save(update_fields=['is_read'])