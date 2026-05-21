from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# ==============================================================================
# CATEGORÍAS
# ==============================================================================
class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    
    # ForeignKey 'self' permite que una categoría tenga subcategorías (Relación Jerárquica)
    sub_category = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        related_name='sub_categories', null=True, blank=True,
        verbose_name="Subcategoría"
    )
    is_sub = models.BooleanField(default=False, verbose_name="Es Subcategoría")
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Evita sobrescribir el slug si ya existe (útil al editar)
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


# ==============================================================================
# ATRIBUTOS DE PRODUCTO (Talles y Colores)
# ==============================================================================
# Al separar Talle y Color en sus propios modelos, normalizamos la base de datos (1FN/2FN).
# Esto evita errores de tipeo y facilita agregar opciones globales.

class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name="Color")
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="Ej: #FF0000 para Rojo", verbose_name="Código Hex")

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50, verbose_name="Talle")

    class Meta:
        verbose_name = "Talle"
        verbose_name_plural = "Talles"

    def __str__(self):
        return self.name


# ==============================================================================
# PRODUCTO BASE
# ==============================================================================
class Product(models.Model):
    """
    Este modelo guarda la información general del producto (Catálogo).
    No guarda stock ni talla/color específicos para evitar DUPLICACIÓN de datos (como descripciones largas e imágenes).
    """
    # related_name='products' permite buscar Productos desde una Categoría: mi_categoria.products.all()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Categoría")
    title = models.CharField(max_length=250, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    
    # Usamos DecimalField para precios, es una mejor práctica que IntegerField para monedas (evita errores de precisión).
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base")
    image = models.ImageField(upload_to='products', verbose_name="Imagen Principal")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


# ==============================================================================
# VARIANTE DE PRODUCTO (El inventario real)
# ==============================================================================
class ProductVariant(models.Model):
    """
    Este modelo representa la versión física y específica del producto.
    Ejemplo: Remera "No es un bug" (Producto) -> Talle M (Size) -> Color Negro (Color)
    Aquí se maneja el stock real y precios dinámicos.
    """
    # Relación principal: Cada variante pertenece a un ÚNICO producto, pero un producto tiene MUCHAS variantes (1 a N).
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Producto")
    
    # null=True, blank=True permite que un producto no tenga color o no tenga talle (ej. una taza o una gorra "Talle Único")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Color")
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Talle")
    
    # PositiveIntegerField asegura que el stock no sea negativo
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    
    # Permite sobrescribir el precio base (ej. Un talle XXL puede ser más caro)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Específico", help_text="Dejar en blanco para usar el precio base del producto")
    
    # SKU (Stock Keeping Unit): Código único para control de inventario y código de barras.
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU")

    class Meta:
        # unique_together asegura que no puedan existir dos variantes exactamente iguales (ej. Dos remeras M, Negras del mismo producto)
        unique_together = ('product', 'color', 'size')
        verbose_name = "Variante de Producto"
        verbose_name_plural = "Variantes de Producto"

    def __str__(self):
        return f"{self.product.title} - Talle: {self.size.name if self.size else 'N/A'} - Color: {self.color.name if self.color else 'N/A'}"

    def get_price(self):
        # Método auxiliar para obtener el precio final a cobrar
        if self.price_override:
            return self.price_override
        return self.product.base_price

    def is_in_stock(self):
        # Método para revisar rápidamente si hay stock
        return self.stock > 0
