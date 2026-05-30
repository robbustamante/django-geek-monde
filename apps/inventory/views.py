from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Stock
from .serializers import StockSerializer


class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [AllowAny]
