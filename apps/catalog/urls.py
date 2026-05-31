from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'catalog'

# Router para ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # ViewSets URLs
    path('', include(router.urls)),
    
    # URLs compatibles (mantener por backward compatibility)
    path('products/list/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('categories/list/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
]
