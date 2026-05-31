from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Coupon, CouponUsage
from .serializers import CouponSerializer, CouponUsageSerializer
from apps.cart.models import Cart


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestionar cupones de descuento."""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    queryset = Coupon.objects.filter(is_active=True)
    lookup_field = 'code'
    
    @action(detail=False, methods=['post'])
    def validate_coupon(self, request):
        """Valida un cupón sin aplicarlo."""
        code = request.data.get('code', '').upper()
        
        if not code:
            return Response(
                {'error': 'El código del cupón es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Cupón no válido'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not coupon.is_valid():
            return Response(
                {'error': 'El cupón no es válido o ha expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar uso por cliente
        user_usage_count = coupon.usages.filter(user=request.user).count()
        if user_usage_count >= coupon.usage_limit_per_customer:
            return Response(
                {'error': f'Ya has usado este cupón el máximo de veces ({coupon.usage_limit_per_customer})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CouponSerializer(coupon)
        return Response({
            'valid': True,
            'coupon': serializer.data,
            'message': f'Cupón válido: {coupon.description}'
        })
    
    @action(detail=False, methods=['post'])
    def apply_to_cart(self, request):
        """Aplica un cupón al carrito del usuario."""
        code = request.data.get('code', '').upper()
        
        if not code:
            return Response(
                {'error': 'El código del cupón es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Cupón no válido'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not coupon.is_valid():
            return Response(
                {'error': 'El cupón no es válido o ha expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar uso por cliente
        user_usage_count = coupon.usages.filter(user=request.user).count()
        if user_usage_count >= coupon.usage_limit_per_customer:
            return Response(
                {'error': f'Ya has usado este cupón el máximo de veces ({coupon.usage_limit_per_customer})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = get_object_or_404(Cart, user=request.user)
        
        # Calcular total del carrito
        cart_total = sum(
            float(item.product.price * item.quantity) for item in cart.items.all()
        )
        
        # Validar compra mínima
        if cart_total < coupon.min_purchase_amount:
            return Response(
                {'error': f'Compra mínima requerida: ${coupon.min_purchase_amount}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcular descuento
        discount = coupon.calculate_discount(cart_total)
        final_total = cart_total - discount
        
        return Response({
            'success': True,
            'coupon': CouponSerializer(coupon).data,
            'cart_total': cart_total,
            'discount_amount': float(discount),
            'final_total': final_total,
            'message': f'Cupón aplicado: ${discount} de descuento'
        })
    
    @action(detail=False, methods=['get'])
    def my_coupons(self, request):
        """Obtiene cupones disponibles para el usuario."""
        coupons = Coupon.objects.filter(is_active=True)
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_usage(self, request):
        """Obtiene el historial de cupones usados por el usuario."""
        usages = CouponUsage.objects.filter(user=request.user).order_by('-created_at')
        serializer = CouponUsageSerializer(usages, many=True)
        return Response(serializer.data)
