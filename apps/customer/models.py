"""
Customer models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.models import TimeStampedModel


class Address(TimeStampedModel):
    """
    Customer address model.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('User')
    )
    name = models.CharField(max_length=100, verbose_name=_('Full Name'))
    street_address = models.CharField(max_length=255, verbose_name=_('Street Address'))
    city = models.CharField(max_length=100, verbose_name=_('City'))
    state = models.CharField(max_length=100, verbose_name=_('State/Province'))
    postal_code = models.CharField(max_length=20, verbose_name=_('Postal Code'))
    country = models.CharField(max_length=100, verbose_name=_('Country'))
    is_default = models.BooleanField(default=False, verbose_name=_('Default Address'))
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
    
    def __str__(self):
        return f"{self.name} - {self.city}"
