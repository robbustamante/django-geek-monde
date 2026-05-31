from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

router = DefaultRouter()
# El basename cart mapeará a /api/v1/cart/
router.register(r'items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    # Mapeo manual para CartViewSet que maneja la raíz /api/v1/cart/
    path('', views.CartViewSet.as_view({'get': 'list'}), name='my-cart'),
    path('apply-coupon/', views.CartViewSet.as_view({'post': 'apply_coupon'}), name='apply-coupon'),
    
    # Rutas generadas para items/ (POST, PATCH, DELETE)
    path('', include(router.urls)),
]
