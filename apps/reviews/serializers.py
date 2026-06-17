"""
Serializers for the reviews app.
"""
from rest_framework import serializers
from .models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for review images."""

    class Meta:
        model = ReviewImage
        fields = ('id', 'image', 'caption')
        read_only_fields = ('id',)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reading reviews (list/detail)."""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'product', 'author', 'author_name', 'author_email',
            'rating', 'title', 'body', 'verified_purchase',
            'helpful_count', 'images', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'author', 'verified_purchase',
            'helpful_count', 'created_at', 'updated_at',
        )


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating reviews.
    Accepts uploaded images as multipart form data.
    """
    images = serializers.ListField(
        child=serializers.ImageField(),
        max_length=5,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'rating', 'title', 'body', 'images')
        read_only_fields = ('id',)

    def validate_images(self, value):
        """Ensure no more than 5 images per review."""
        if len(value) > 5:
            raise serializers.ValidationError(
                "No se pueden adjuntar más de 5 imágenes por reseña."
            )
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        review = Review.objects.create(**validated_data)
        for image in images_data:
            ReviewImage.objects.create(review=review, image=image)
        return review

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If new images were uploaded, replace the existing ones
        if images_data is not None:
            instance.images.all().delete()
            for image in images_data:
                ReviewImage.objects.create(review=instance, image=image)

        return instance
