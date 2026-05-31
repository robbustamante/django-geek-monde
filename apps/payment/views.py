from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer
from apps.order.models import Order


class PaymentViewSet(viewsets.ViewSet):
    """ViewSet para gestionar pagos."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def available_methods(self, request):
        """Obtiene los métodos de pago disponibles."""
        methods = [
            {'id': 'credit_card', 'name': 'Tarjeta de Crédito'},
            {'id': 'debit_card', 'name': 'Tarjeta de Débito'},
            {'id': 'bank_transfer', 'name': 'Transferencia Bancaria'},
            {'id': 'cash', 'name': 'Efectivo'},
        ]
        return Response(methods)
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Crear un pago para una orden."""
        serializer = PaymentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            payment = serializer.save()
            output_serializer = PaymentSerializer(payment)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Obtiene los pagos del usuario autenticado."""
        # Filtrar pagos de órdenes del usuario
        payments = Payment.objects.filter(order__user=request.user).order_by('-created_at')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='payment-status/(?P<payment_id>[0-9]+)')
    def payment_status(self, request, payment_id=None):
        """Obtener estado de un pago específico."""
        payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class PaymentMethodListView(generics.GenericAPIView):
    """Lista métodos de pago disponibles."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        methods = [
            {'id': 'credit_card', 'name': 'Tarjeta de Crédito'},
            {'id': 'debit_card', 'name': 'Tarjeta de Débito'},
            {'id': 'bank_transfer', 'name': 'Transferencia Bancaria'},
            {'id': 'cash', 'name': 'Efectivo'},
        ]
        return Response(methods)
