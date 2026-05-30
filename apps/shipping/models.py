"""
Shipping models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.order.models import Order


class Shipping(TimeStampedModel):
    """
    Shipping model for order shipments.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_transit', _('In Transit')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
    ]
    
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='shipping',
        verbose_name=_('Order')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Tracking Number')
    )
    
    class Meta:
        verbose_name = _('Shipping')
        verbose_name_plural = _('Shippings')
    
    def __str__(self):
        return f"Shipping for {self.order.number}"
