from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from apps.reviews.views import ProductReviewViewSet

app_name = 'catalog'

# Router para ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

# Router para reviews anidadas bajo productos
review_router = DefaultRouter()
review_router.register(r'', ProductReviewViewSet, basename='product-review')

urlpatterns = [
    # ViewSets URLs
    path('', include(router.urls)),
    
    # Reviews anidadas: /api/v1/catalog/products/{slug}/reviews/
    path('products/<slug:product_slug>/reviews/', include(review_router.urls)),
    
    # URLs compatibles (mantener por backward compatibility)
    path('products/list/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('categories/list/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
]
