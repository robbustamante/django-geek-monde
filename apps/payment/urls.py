from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
]
