"""
Order models for order management.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django_fsm import FSMField, transition
from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class Order(TimeStampedModel):
    """
    Order model with FSM for order status transitions.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('User')
    )
    number = models.CharField(max_length=50, unique=True, verbose_name=_('Order Number'))
    status = FSMField(default='pending', choices=STATUS_CHOICES, verbose_name=_('Status'))
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total Amount')
    )
    shipping_address = models.ForeignKey(
        'customer.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Shipping Address')
    )
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Order {self.number}"
    
    @transition(field=status, source='pending', target='processing')
    def mark_processing(self):
        pass
    
    @transition(field=status, source='processing', target='shipped')
    def mark_shipped(self):
        pass
    
    @transition(field=status, source=['pending', 'processing'], target='cancelled')
    def mark_cancelled(self):
        pass


class OrderItem(TimeStampedModel):
    """
    Individual order item model.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Unit Price')
    )
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
