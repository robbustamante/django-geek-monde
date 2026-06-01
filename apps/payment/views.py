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


class StripePaymentViewSet(viewsets.ViewSet):
    """ViewSet para la integración con Stripe."""
    
    def get_permissions(self):
        # El webhook de Stripe no usa autenticación porque es un POST desde Stripe
        if self.action == 'webhook':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='create-intent')
    def create_intent(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Opcional: chequear si la orden ya tiene pago completado
        if order.status != 'pending':
            return Response({'error': 'La orden no está en estado pending'}, status=status.HTTP_400_BAD_REQUEST)
            
        from .integrations.stripe_gateway import StripeGateway
        gateway = StripeGateway()
        
        try:
            # En la vida real, el total puede venir de `order.total_amount` o recalcularlo
            # Asumimos que `order` tiene un field `total_amount`
            result = gateway.create_intent(order, order.total_amount)
            
            # Crear o actualizar el Payment
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'amount': order.total_amount,
                    'provider': 'stripe',
                    'method': 'credit_card', # Default for Stripe
                    'status': 'pending',
                }
            )
            
            payment.stripe_payment_intent_id = result['intent_id']
            payment.save()
            
            return Response({
                'client_secret': result['client_secret'],
                'payment_id': payment.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        from .integrations.stripe_gateway import StripeGateway
        gateway = StripeGateway()
        
        try:
            event = gateway.process_webhook(payload, sig_header)
        except ValueError:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Invalid signature or other stripe error
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            intent_id = payment_intent['id']
            
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=intent_id)
                payment.status = 'completed'
                payment.transaction_id = intent_id
                payment.save()
                
                # Update Order status
                if payment.order.status == 'pending':
                    payment.order.mark_processing()
                    payment.order.save()
            except Payment.DoesNotExist:
                pass
                
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            intent_id = payment_intent['id']
            
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=intent_id)
                payment.status = 'failed'
                payment.save()
            except Payment.DoesNotExist:
                pass
                
        return Response(status=status.HTTP_200_OK)


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
