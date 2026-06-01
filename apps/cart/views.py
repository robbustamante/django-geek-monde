from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.catalog.models import Product


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet para el carrito principal.
    Mapeado típicamente a /api/v1/cart/
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """GET /api/v1/cart/ - Mi carrito"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='apply-coupon')
    def apply_coupon(self, request):
        """POST /api/v1/cart/apply-coupon/ - Apply a coupon to the cart."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        code = request.data.get('code')
        
        if not code:
            return Response({'error': 'Se requiere el código del cupón.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Calculate subtotal using serializer logic
        cart_data = CartSerializer(cart).data
        subtotal = float(cart_data['subtotal'])
        
        from apps.discounts.services import CouponService
        is_valid, error_msg, coupon = CouponService.validate_coupon(
            coupon_code=code,
            user=request.user,
            subtotal=subtotal
        )
        
        if not is_valid:
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
        cart.applied_coupon = coupon
        cart.save()
        
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='remove-coupon')
    def remove_coupon(self, request):
        """POST /api/v1/cart/remove-coupon/ - Remove applied coupon."""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.applied_coupon = None
        cart.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para los items del carrito.
    Mapeado a /api/v1/cart/items/
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
        
    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def create(self, request, *args, **kwargs):
        """POST /api/v1/cart/items/ - Agregar item"""
        cart = self.get_cart()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id or quantity < 1:
            return Response({'error': 'product_id y quantity válida son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
            
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/v1/cart/items/{id}/ - Actualizar cantidad"""
        cart_item = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        
        if quantity <= 0:
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        cart_item.quantity = quantity
        cart_item.save()
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/v1/cart/items/{id}/ - Eliminar item"""
        cart_item = self.get_object()
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
