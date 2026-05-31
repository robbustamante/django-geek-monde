from rest_framework import serializers
from .models import Payment
from apps.order.models import Order


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos."""
    order_number = serializers.CharField(source='order.number', read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'order_number', 'amount', 'method', 'status',
            'provider', 'stripe_payment_intent_id', 'transaction_id',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'stripe_payment_intent_id')


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer para crear un pago."""
    order_id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ])
    provider = serializers.ChoiceField(choices=[
        ('stripe', 'Stripe'),
        ('mercadopago', 'MercadoPago'),
    ], required=False)
    
    def create(self, validated_data):
        order_id = validated_data.get('order_id')
        method = validated_data.get('method')
        provider = validated_data.get('provider')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Orden no encontrada')
        
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method=method,
            provider=provider or 'stripe',
            status='pending'
        )
        
        return payment
