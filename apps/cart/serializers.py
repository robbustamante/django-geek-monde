from rest_framework import serializers
from .models import Cart, CartItem
from apps.catalog.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Se asigna dinámicamente
        write_only=True,
        source='product'
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal', 'created_at')
        read_only_fields = ('created_at',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permite asignar products dinámicamente
        from apps.catalog.models import Product
        self.fields['product_id'].queryset = Product.objects.filter(is_active=True)
    
    def get_subtotal(self, obj):
        """Calcula el subtotal del item."""
        return float(obj.product.price * obj.quantity)


class CartSerializer(serializers.ModelSerializer):
    """Serializer para el carrito."""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'items_count', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_total(self, obj):
        """Calcula el total del carrito."""
        return sum(float(item.product.price * item.quantity) for item in obj.items.all())
    
    def get_items_count(self, obj):
        """Cuenta items en el carrito."""
        return obj.items.aggregate(
            total_qty=models.Sum('quantity')
        )['total_qty'] or 0


from django.db import models as models
