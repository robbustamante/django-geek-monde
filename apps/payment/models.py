"""
Payment models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.order.models import Order


class Payment(TimeStampedModel):
    """
    Payment model for order payments.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    
    METHOD_CHOICES = [
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('cash', _('Cash')),
    ]
    
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='payment',
        verbose_name=_('Order')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Amount')
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name=_('Payment Method')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Transaction ID')
    )
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
    
    def __str__(self):
        return f"Payment for {self.order.number}"
