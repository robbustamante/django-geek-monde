from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('stock/', views.StockListView.as_view(), name='stock-list'),
]
