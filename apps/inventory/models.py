"""Inventory models for stock management."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.catalog.models import Product


class StockLevel(TimeStampedModel):
    """
    Stock level model for tracking product inventory.
    Manages quantity, reservations, and availability.
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_levels',
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Quantity')
    )
    reserved = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Reserved')
    )
    
    class Meta:
        verbose_name = _('Stock Level')
        verbose_name_plural = _('Stock Levels')
    
    def __str__(self):
        return f"Stock: {self.product.name}"
    
    @property
    def available(self):
        """Calcula el stock disponible."""
        return self.quantity - self.reserved
    
    def is_in_stock(self, quantity=1):
        """Verifica si hay stock disponible."""
        return self.available >= quantity


class StockMovement(TimeStampedModel):
    """
    Stock movement tracking for audit purposes.
    """
    MOVEMENT_TYPES = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('adjustment', _('Adjustment')),
        ('reservation', _('Reservation')),
        ('release', _('Release')),
    ]
    
    stock = models.ForeignKey(
        StockLevel,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_('Stock')
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name=_('Movement Type')
    )
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    reason = models.TextField(blank=True, verbose_name=_('Reason'))
    
    class Meta:
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.stock.product.name}"
