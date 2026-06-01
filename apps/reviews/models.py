"""
Review models for product reviews with image attachments.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Review(TimeStampedModel):
    """
    Product review with rating, title, body, and optional image attachments.
    Each user can only leave one review per product.
    """
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Product')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Author')
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    body = models.TextField(
        verbose_name=_('Body')
    )
    verified_purchase = models.BooleanField(
        default=False,
        verbose_name=_('Verified Purchase')
    )
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Helpful Count')
    )

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ('-created_at',)
        unique_together = ('product', 'author')

    def __str__(self):
        return f"{self.author} - {self.product.name} ({self.rating}★)"


class ReviewImage(TimeStampedModel):
    """
    Image attachment for a review. Maximum 5 images per review.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Review')
    )
    image = models.ImageField(
        upload_to='reviews/%Y/%m/',
        verbose_name=_('Image')
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Caption')
    )

    class Meta:
        verbose_name = _('Review Image')
        verbose_name_plural = _('Review Images')

    def __str__(self):
        return f"Image for review by {self.review.author} on {self.review.product.name}"
