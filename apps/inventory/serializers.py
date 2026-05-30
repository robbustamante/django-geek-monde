from rest_framework import serializers
from .models import Stock


class StockSerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()

    class Meta:
        model = Stock
        fields = ('id', 'product', 'quantity', 'reserved', 'available')
