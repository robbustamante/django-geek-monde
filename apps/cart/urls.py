from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart-detail'),
    path('items/', views.CartItemListCreateView.as_view(), name='cart-item-list'),
    path('items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
]
