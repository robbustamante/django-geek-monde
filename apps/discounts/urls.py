from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

app_name = 'discounts'

router = SimpleRouter()
router.register(r'', views.CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
]
