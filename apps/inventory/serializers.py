from rest_framework import serializers
from .models import StockLevel, StockMovement


class StockLevelSerializer(serializers.ModelSerializer):
    available = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockLevel
        fields = ('id', 'product', 'quantity', 'reserved', 'available')


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ('id', 'stock', 'movement_type', 'quantity', 'reason', 'created_at')
        read_only_fields = ('created_at',)
