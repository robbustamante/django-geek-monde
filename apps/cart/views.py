from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.catalog.models import Product


def get_or_create_cart(request):
    """
    Get or create a cart based on auth state.
    - Authenticated user: cart linked to user
    - Anonymous: cart linked to session_key
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    # Ensure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(
        session_key=session_key,
        user=None,
    )
    return cart


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet para el carrito principal.
    Mapeado típicamente a /api/v1/cart/
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """GET /api/v1/cart/ - Mi carrito"""
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='apply-coupon')
    def apply_coupon(self, request):
        """POST /api/v1/cart/apply-coupon/ - Apply a coupon to the cart."""
        cart = get_or_create_cart(request)
        code = request.data.get('code')
        
        if not code:
            return Response({'error': 'Se requiere el código del cupón.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Calculate subtotal using serializer logic
        cart_data = CartSerializer(cart).data
        subtotal = float(cart_data['subtotal'])
        
        from apps.discounts.services import CouponService
        is_valid, error_msg, coupon = CouponService.validate_coupon(
            coupon_code=code,
            user=request.user if request.user.is_authenticated else None,
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
        cart = get_or_create_cart(request)
        cart.applied_coupon = None
        cart.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='merge-cart')
    def merge_cart(self, request):
        """
        POST /api/v1/cart/merge-cart/ - Merge anonymous cart into user cart.
        Called after login to transfer anonymous cart items to the user's cart.
        """
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        session_key = request.session.session_key
        if not session_key:
            return Response({'detail': 'No anonymous cart to merge.'}, status=status.HTTP_200_OK)

        try:
            anonymous_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
        except Cart.DoesNotExist:
            return Response({'detail': 'No anonymous cart to merge.'}, status=status.HTTP_200_OK)

        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        # Merge items: add quantities if product already exists
        for anon_item in anonymous_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=anon_item.product,
                defaults={'quantity': anon_item.quantity}
            )
            if not created:
                user_item.quantity += anon_item.quantity
                user_item.save()

        # Delete the anonymous cart
        anonymous_cart.delete()

        serializer = CartSerializer(user_cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para los items del carrito.
    Mapeado a /api/v1/cart/items/
    """
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            import traceback
            with open('error_debug.txt', 'w') as f:
                f.write(traceback.format_exc())
            raise

    def get_queryset(self):
        cart = get_or_create_cart(self.request)
        return CartItem.objects.filter(cart=cart)
        
    def get_cart(self):
        return get_or_create_cart(self.request)

    def create(self, request, *args, **kwargs):
        """POST /api/v1/cart/items/ - Agregar item"""
        try:
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
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return Response({'error': str(e), 'traceback': error_details}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
