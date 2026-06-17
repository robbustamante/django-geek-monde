from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import StockLevel
from .serializers import StockLevelSerializer


class StockListView(generics.ListAPIView):
    queryset = StockLevel.objects.all()
    serializer_class = StockLevelSerializer
    permission_classes = [AllowAny]
