from rest_framework import generics, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestionar categorías de productos."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Obtiene productos de una categoría específica."""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestionar productos del catálogo."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filtra productos por precio si se proporciona rango."""
        queryset = super().get_queryset()
        
        # Filtro por rango de precio
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        return queryset


# Vistas basadas en clases para compatibilidad anterior
class CategoryListView(generics.ListAPIView):
    """Listar todas las categorías."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class CategoryDetailView(generics.RetrieveAPIView):
    """Obtener detalle de una categoría."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ProductListView(generics.ListAPIView):
    """Listar todos los productos."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'created_at']


class ProductDetailView(generics.RetrieveAPIView):
    """Obtener detalle de un producto."""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
