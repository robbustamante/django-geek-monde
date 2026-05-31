from rest_framework import serializers
from .models import Category, Product
from apps.inventory.models import StockLevel


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías de productos."""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'is_active', 'children', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
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


class ProductSerializer(serializers.ModelSerializer):
    """Serializer para productos."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'description', 'price', 'image',
            'category', 'category_id', 'is_active', 'stock', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'slug')
    
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
