from django.db import models
from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem
from apps.catalog.models import Product
from apps.catalog.serializers import ProductSerializer
from apps.discounts.serializers import CouponSerializer
from apps.discounts.services import CouponService

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        write_only=True,
        source='product'
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal', 'created_at')
        read_only_fields = ('created_at',)
    
    def get_subtotal(self, obj):
        """Calcula el subtotal del item."""
        return float(obj.product.price * obj.quantity)


class CartSerializer(serializers.ModelSerializer):
    """Serializer para el carrito."""
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    applied_coupon = CouponSerializer(read_only=True)
    discount_amount = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'items_count', 'subtotal', 'applied_coupon', 'discount_amount', 'total', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_subtotal(self, obj):
        """Calcula el subtotal sin descuento."""
        return sum((item.product.price * item.quantity for item in obj.items.all()), Decimal('0.0'))

    def get_discount_amount(self, obj):
        """Calcula el monto del descuento si hay un cupón."""
        subtotal = self.get_subtotal(obj)
        if obj.applied_coupon:
            # Re-validate first to ensure it's still valid
            is_valid, _, coupon = CouponService.validate_coupon(
                obj.applied_coupon.code, obj.user, subtotal
            )
            if is_valid:
                return float(CouponService.calculate_discount(coupon, subtotal))
        return 0.0

    def get_total(self, obj):
        """Calcula el total final (subtotal - descuento)."""
        subtotal = float(self.get_subtotal(obj))
        discount = self.get_discount_amount(obj)
        return max(0.0, subtotal - discount)
    
    def get_items_count(self, obj):
        """Cuenta items en el carrito."""
        return obj.items.aggregate(
            total_qty=models.Sum('quantity')
        )['total_qty'] or 0
