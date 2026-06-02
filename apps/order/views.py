from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.cart.models import Cart


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar órdenes del usuario."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'number'
    
    def get_queryset(self):
        """Retorna solo las órdenes del usuario autenticado."""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Crear una nueva orden desde el carrito."""
        cart = get_object_or_404(Cart, user=request.user)
        
        if not cart.items.exists():
            return Response(
                {'error': 'El carrito está vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderCreateSerializer(
            data={},
            context={'request': request}
        )
        
        if serializer.is_valid():
            order = serializer.save()
            output_serializer = OrderSerializer(order)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, number=None):
        """Cancelar una orden pendiente."""
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'error': f'No se puede cancelar una orden con estado {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.mark_cancelled()
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_processing(self, request, number=None):
        """Marcar orden como en procesamiento (solo admin)."""
        if not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para realizar esta acción'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        order.mark_processing()
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def items(self, request, number=None):
        """Obtener items de una orden específica."""
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='invoice/download')
    def download_invoice(self, request, number=None):
        """Descargar factura PDF."""
        from django.http import HttpResponse
        from .utils.invoice_generator import generate_invoice_pdf
        
        order = self.get_object()
        pdf_bytes = generate_invoice_pdf(order)
        
        if pdf_bytes:
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="factura_{order.number}.pdf"'
            return response
        
        return Response(
            {'error': 'No se pudo generar la factura'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=True, methods=['post'], url_path='invoice/send')
    def send_invoice(self, request, number=None):
        """Enviar factura PDF por email."""
        from django.core.mail import EmailMessage
        from .utils.invoice_generator import generate_invoice_pdf
        
        order = self.get_object()
        pdf_bytes = generate_invoice_pdf(order)
        
        if not pdf_bytes:
            return Response(
                {'error': 'No se pudo generar la factura'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        try:
            email = EmailMessage(
                subject=f'Factura de tu compra en Geek Monde (Orden #{order.number})',
                body=f'Hola {order.user.get_full_name()},\n\nAdjuntamos la factura de tu reciente compra.\n\nGracias por elegirnos.',
                from_email='noreply@geek-monde.com',
                to=[order.user.email],
            )
            email.attach(f'factura_{order.number}.pdf', pdf_bytes, 'application/pdf')
            email.send()
            
            return Response({'message': 'Factura enviada correctamente'})
        except Exception as e:
            return Response(
                {'error': f'Error enviando email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Imports para vistas legacy
from .serializers import OrderItemSerializer


class OrderListView(generics.ListCreateAPIView):
    """Listar órdenes del usuario."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Este método es manejado por OrderCreateSerializer en el ViewSet
        pass


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """Obtener detalle de una orden."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'number'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
