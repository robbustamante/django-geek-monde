from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'order'

router = DefaultRouter()
router.register(r'', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
