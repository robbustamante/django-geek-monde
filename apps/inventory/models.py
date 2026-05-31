"""
Inventory models for stock management.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.catalog.models import Product, ProductVariant


class Stock(TimeStampedModel):
    """
    General product stock model (base level).
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    reserved = models.PositiveIntegerField(default=0, verbose_name=_('Reserved'))
    
    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')
    
    def __str__(self):
        return f"Stock for {self.product.name}"
    
    @property
    def available(self):
        return self.quantity - self.reserved


class StockLevel(TimeStampedModel):
    """
    Track inventory for each specific product variant (size/color combination).
    """
    variant = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name=_('Variant')
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    reorder_level = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Reorder Level'),
        help_text=_('Send a low-stock alert when quantity drops below this value')
    )
    last_restocked = models.DateTimeField(auto_now=True, verbose_name=_('Last Restocked'))

    class Meta:
        verbose_name = _('Stock Level')
        verbose_name_plural = _('Stock Levels')

    def __str__(self):
        return f"Stock for {self.variant}"

    def is_low_stock(self):
        """Returns True when quantity is below the reorder threshold."""
        return self.quantity < self.reorder_level

    @property
    def is_out_of_stock(self):
        """Returns True when there are no units left."""
        return self.quantity == 0
