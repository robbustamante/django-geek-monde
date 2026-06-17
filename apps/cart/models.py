"""
Cart models for shopping cart management.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class Cart(TimeStampedModel):
    """
    Shopping cart model.
    Supports both authenticated users and anonymous sessions.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('User'),
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Session Key'),
    )
    applied_coupon = models.ForeignKey(
        'discounts.Coupon',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='carts',
        verbose_name=_('Applied Coupon')
    )
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user}"
        return f"Anonymous cart ({self.session_key})"


class CartItem(TimeStampedModel):
    """
    Individual cart item model.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Cart')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='cart_items',
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
