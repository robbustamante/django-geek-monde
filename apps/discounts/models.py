"""
Models for the discounts app (coupons, promotions).
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel

class Coupon(TimeStampedModel):
    """
    Coupon model for cart discounts.
    """
    DISCOUNT_TYPES = (
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    )

    code = models.CharField(max_length=50, unique=True, verbose_name=_('Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    discount_type = models.CharField(
        max_length=15, 
        choices=DISCOUNT_TYPES,
        verbose_name=_('Discount Type')
    )
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Discount Value')
    )
    
    max_use = models.PositiveIntegerField(
        null=True, blank=True,
        help_text=_('Maximum total uses for this coupon (leave empty for unlimited)'),
        verbose_name=_('Max Uses')
    )
    current_use = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Current Uses')
    )
    
    valid_from = models.DateTimeField(verbose_name=_('Valid From'))
    valid_until = models.DateTimeField(verbose_name=_('Valid Until'))
    
    min_purchase_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('Minimum Purchase Amount')
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, blank=True,
        help_text=_('Maximum discount amount allowed for percentage coupons'),
        verbose_name=_('Max Discount Amount')
    )
    
    usage_limit_per_customer = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Usage Limit per Customer')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()} - {self.discount_value})"


class CouponUsage(TimeStampedModel):
    """
    Tracks when a user has actually applied a coupon to an order.
    """
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name=_('Coupon')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name=_('User')
    )
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='coupon_usages',
        verbose_name=_('Order')
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Used At')
    )

    class Meta:
        verbose_name = _('Coupon Usage')
        verbose_name_plural = _('Coupon Usages')

    def __str__(self):
        return f"{self.user} used {self.coupon.code}"
