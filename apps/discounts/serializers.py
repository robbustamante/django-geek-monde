from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    """Serializer to display coupon information."""
    class Meta:
        model = Coupon
        fields = (
            'code', 'description', 'discount_type', 'discount_value',
            'min_purchase_amount', 'max_discount_amount'
        )

class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating a coupon code via POST."""
    code = serializers.CharField(max_length=50, required=True)
    # Subtotal is optional in the validation endpoint (it's checked against cart usually, 
    # but allowing it here for UI preview)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
