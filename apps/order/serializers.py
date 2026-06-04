from rest_framework import serializers
from .models import Order, OrderItem
from apps.catalog.models import Product
from apps.catalog.serializers import ProductSerializer
from apps.payment.serializers import PaymentSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para items de orden."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        write_only=True,
        source='product'
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'unit_price', 'subtotal', 'created_at')
        read_only_fields = ('unit_price', 'created_at')
    
    def get_subtotal(self, obj):
        """Calcula el subtotal del item."""
        return float(obj.unit_price * obj.quantity)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer para órdenes."""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'number', 'user', 'user_email', 'user_name', 'status',
            'total_amount', 'items', 'payment', 'shipping_address', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'number', 'created_at', 'updated_at')
    
    def get_payment(self, obj):
        """Obtiene info de pago si existe."""
        try:
            if hasattr(obj, 'payment'):
                return PaymentSerializer(obj.payment).data
        except:
            pass
        return None

    def get_shipping_address(self, obj):
        """Obtiene info de la dirección de envío si existe."""
        if obj.shipping_address:
            from apps.customer.serializers import AddressSerializer
            return AddressSerializer(obj.shipping_address).data
        return None


class OrderCreateSerializer(serializers.Serializer):
    """Serializer para crear una orden desde el carrito."""
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
    
    def create(self, validated_data):
        """Crea una orden a partir de los items."""
        from apps.cart.models import Cart
        from apps.customer.models import Address
        from django.utils.timezone import now
        from uuid import uuid4
        
        user = self.context['request'].user
        cart = Cart.objects.get(user=user)
        shipping_address_id = validated_data.get('shipping_address_id')
        
        if not cart.items.exists():
            raise serializers.ValidationError('El carrito está vacío')
            
        shipping_address = None
        if shipping_address_id:
            try:
                shipping_address = Address.objects.get(id=shipping_address_id, user=user)
            except Address.DoesNotExist:
                raise serializers.ValidationError({'shipping_address_id': 'Dirección no válida.'})
        
        # Crear número de orden único
        order_number = f"ORD-{int(now().timestamp())}-{str(uuid4())[:8].upper()}"
        
        # Calcular total
        total_amount = sum(
            float(item.product.price * item.quantity)
            for item in cart.items.all()
        )
        
        # Crear orden
        order = Order.objects.create(
            user=user,
            number=order_number,
            total_amount=total_amount,
            shipping_address=shipping_address
        )
        
        # Copiar items del carrito a la orden
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
        
        # Vaciar carrito
        cart.items.all().delete()
        
        return order
