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
