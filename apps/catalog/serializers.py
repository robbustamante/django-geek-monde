from rest_framework import serializers
from django.db.models import Avg
from .models import Category, Product, ProductVariant
from apps.inventory.models import StockLevel
from drf_spectacular.utils import extend_schema_field

class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías de productos."""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'is_active', 'children', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        """Obtiene subcategorías si existen."""
        children = obj.children.filter(is_active=True)
        if children.exists():
            return CategorySerializer(children, many=True).data
        return []


class StockLevelSerializer(serializers.ModelSerializer):
    """Serializer para niveles de stock."""
    class Meta:
        model = StockLevel
        fields = ('id', 'quantity', 'reserved', 'available')
        read_only_fields = ('available',)
    
    def get_available(self, obj):
        """Calcula stock disponible."""
        return obj.quantity - obj.reserved


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer para variantes de productos."""
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ('id', 'size', 'color', 'sku', 'price_adjustment', 'final_price', 'image', 'is_active')


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    stock = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'description', 'price', 'image',
            'category', 'category_id', 'is_active',
            # Geek-specific fields
            'clothing_type', 'geek_category', 'franchise', 'character_name',
            'size', 'color', 'material', 'gender_fit',
            'stock', 'variants',
            'average_rating', 'review_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'slug')
    
    @extend_schema_field(serializers.DictField())
    def get_stock(self, obj):
        """Obtiene info de stock si existe."""
        try:
            stock = obj.stock_levels.first()
            if stock:
                return {
                    'quantity': stock.quantity,
                    'reserved': stock.reserved,
                    'available': stock.quantity - stock.reserved
                }
        except:
            pass
        return {'quantity': 0, 'reserved': 0, 'available': 0}

    @extend_schema_field(serializers.FloatField())
    def get_average_rating(self, obj):
        """Obtiene el promedio de calificaciones (desde apps.reviews)."""
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    @extend_schema_field(serializers.IntegerField())
    def get_review_count(self, obj):
        """Obtiene la cantidad total de reseñas."""
        return obj.reviews.count()
