"""
Catalog models for product management.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    Product category model.
    """
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('Parent category')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """
    Base product model.
    """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    description = models.TextField(verbose_name=_('Description'))
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Category')
    )
    sku = models.CharField(max_length=50, unique=True, verbose_name=_('SKU'))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Price')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        verbose_name=_('Image')
    )

    # --- Geek Clothing Fields ---

    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'XXL'),
    ]
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        blank=True,
        verbose_name=_('Size')
    )

    color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Color'),
        help_text=_('e.g. Black, White, Navy Blue')
    )

    material = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Material'),
        help_text=_('e.g. 100% Cotton, Cotton Blend')
    )

    GEEK_CATEGORY_CHOICES = [
        ('anime', _('Anime & Manga')),
        ('gaming', _('Gaming & Esports')),
        ('movies', _('Movies & TV')),
        ('tech', _('Tech & Science')),
        ('meme', _('Meme Culture')),
    ]
    geek_category = models.CharField(
        max_length=50,
        choices=GEEK_CATEGORY_CHOICES,
        blank=True,
        verbose_name=_('Geek Category')
    )

    character_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Character Name'),
        help_text=_('e.g. Naruto Uzumaki')
    )

    franchise = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Franchise'),
        help_text=_('e.g. Naruto, Star Wars, The Witcher')
    )

    CLOTHING_TYPE_CHOICES = [
        ('tshirt', _('T-Shirt')),
        ('hoodie', _('Hoodie')),
        ('sweatshirt', _('Sweatshirt')),
        ('hat', _('Hat/Cap')),
        ('accessory', _('Accessories')),
    ]
    clothing_type = models.CharField(
        max_length=50,
        choices=CLOTHING_TYPE_CHOICES,
        verbose_name=_('Clothing Type')
    )

    GENDER_FIT_CHOICES = [
        ('unisex', _('Unisex')),
        ('mens', _("Men's")),
        ('womens', _("Women's")),
        ('kids', _('Kids')),
    ]
    gender_fit = models.CharField(
        max_length=20,
        choices=GENDER_FIT_CHOICES,
        blank=True,
        verbose_name=_('Gender / Fit')
    )

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('name',)
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['clothing_type']),
            models.Index(fields=['geek_category']),
        ]

    def __str__(self):
        return self.name


class ProductVariant(TimeStampedModel):
    """
    A specific size/color combination of a product.
    e.g. "Naruto Uzumaki T-Shirt" in size M and color Black.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('Product')
    )
    size = models.CharField(
        max_length=10,
        choices=Product.SIZE_CHOICES,
        blank=True,
        verbose_name=_('Size')
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Color'),
        help_text=_('e.g. Black, White, Navy Blue')
    )
    # Variant-specific SKU — e.g. NARUTO-BLK-M (product-color-size)
    sku = models.CharField(max_length=100, unique=True, verbose_name=_('SKU'))
    # Extra cost for certain sizes/colors (can be negative for a discount)
    price_adjustment = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Price Adjustment')
    )
    image = models.ImageField(
        upload_to='variants/',
        blank=True,
        verbose_name=_('Variant Image')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        unique_together = ('product', 'size', 'color')
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'is_active']),
        ]

    def __str__(self):
        parts = [self.product.name]
        if self.color:
            parts.append(self.color)
        if self.size:
            parts.append(self.size)
        return ' - '.join(parts)

    @property
    def final_price(self):
        """Product base price plus any variant adjustment."""
        return self.product.price + self.price_adjustment
