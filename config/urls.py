"""
Main URL Configuration for Django Geek Monde project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema')),
    
    # Authentication
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Shop API
    path('api/v1/catalog/', include('apps.catalog.urls')),
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/order/', include('apps.order.urls')),
    path('api/v1/payment/', include('apps.payment.urls')),
    path('api/v1/shipping/', include('apps.shipping.urls')),
    path('api/v1/customer/', include('apps.customer.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/discounts/', include('apps.discounts.urls')),
    
    # Reviews
    path('api/v1/reviews/', include('apps.reviews.urls')),

    # Notifications
    path('api/v1/notifications/', include('apps.notifications.urls')),

]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
