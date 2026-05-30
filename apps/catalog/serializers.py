from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'description', 'price', 'image',
            'category', 'category_id', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
