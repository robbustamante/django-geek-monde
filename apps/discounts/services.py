from decimal import Decimal
from django.utils import timezone
from .models import Coupon, CouponUsage

class CouponService:
    """
    Service class to handle coupon logic (validation, calculation).
    """

    @classmethod
    def validate_coupon(cls, coupon_code, user, subtotal):
        """
        Validates if a coupon can be used by the given user for the given subtotal.
        Returns: (is_valid, error_message, coupon_obj)
        """
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            return False, "Cupón inválido o inactivo.", None

        now = timezone.now()

        # 1. Date validation
        if now < coupon.valid_from:
            return False, "Este cupón aún no es válido.", None
        if now > coupon.valid_until:
            return False, "Este cupón ha expirado.", None

        # 2. Minimum purchase validation
        if subtotal < coupon.min_purchase_amount:
            return False, f"Se requiere una compra mínima de ${coupon.min_purchase_amount} para usar este cupón.", None

        # 3. Global usage limit
        if coupon.max_use is not None and coupon.current_use >= coupon.max_use:
            return False, "Este cupón ha alcanzado su límite de usos totales.", None

        # 4. Per-customer usage limit
        if user and user.is_authenticated:
            user_uses = CouponUsage.objects.filter(coupon=coupon, user=user).count()
            if user_uses >= coupon.usage_limit_per_customer:
                return False, f"Ya has usado este cupón el máximo de veces permitido ({coupon.usage_limit_per_customer}).", None

        return True, "", coupon

    @classmethod
    def calculate_discount(cls, coupon, subtotal):
        """
        Calculates the exact discount amount for a given subtotal.
        Returns the discount Decimal value.
        """
        if not coupon:
            return Decimal('0.00')

        discount_amount = Decimal('0.00')

        if coupon.discount_type == 'percentage':
            discount_amount = (subtotal * coupon.discount_value) / Decimal('100.0')
            # Apply max discount cap if set
            if coupon.max_discount_amount is not None:
                if discount_amount > coupon.max_discount_amount:
                    discount_amount = coupon.max_discount_amount
        else:
            # Fixed amount
            discount_amount = coupon.discount_value

        # Discount cannot be larger than the subtotal
        if discount_amount > subtotal:
            discount_amount = subtotal

        return discount_amount.quantize(Decimal('0.01'))
