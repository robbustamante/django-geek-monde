"""
Inventory models for stock management.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class Stock(TimeStampedModel):
    """
    Product stock model.
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
