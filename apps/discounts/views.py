from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from django.utils import timezone
from .models import Coupon
from .serializers import CouponSerializer, CouponValidateSerializer
from .services import CouponService

class CouponViewSet(viewsets.ViewSet):
    """
    ViewSet for handling coupon logic.
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='validate-coupon')
    def validate_coupon(self, request):
        """
        POST /api/v1/discounts/validate-coupon/
        Validates a coupon without applying it to the cart.
        """
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        subtotal = serializer.validated_data['subtotal']

        is_valid, error_msg, coupon = CouponService.validate_coupon(
            coupon_code=code, 
            user=request.user, 
            subtotal=subtotal
        )

        if not is_valid:
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        discount_amount = CouponService.calculate_discount(coupon, subtotal)
        
        return Response({
            'message': 'Cupón válido.',
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': discount_amount,
            'final_total': max(Decimal('0.00'), subtotal - discount_amount)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-coupons')
    def my_coupons(self, request):
        """
        GET /api/v1/discounts/my-coupons/
        Returns active coupons that are globally available or assigned to the user.
        (For now, just returns globally active coupons within date range).
        """
        now = timezone.now()
        coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )
        # Here we could filter out coupons the user has already used up to the limit
        
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
