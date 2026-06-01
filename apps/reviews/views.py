"""
Views for the reviews app.
"""
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.catalog.models import Product
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from .permissions import IsOwnerOrAdmin


class ProductReviewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for reviews nested under a product.

    GET  /api/v1/catalog/products/{product_slug}/reviews/  → List reviews
    POST /api/v1/catalog/products/{product_slug}/reviews/  → Create review
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self):
        return get_object_or_404(Product, slug=self.kwargs['product_slug'])

    def get_queryset(self):
        return Review.objects.filter(
            product=self.get_product()
        ).select_related('author').prefetch_related('images')

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(
            product=self.get_product(),
            author=self.request.user,
        )


class ReviewViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for individual review operations.

    GET    /api/v1/reviews/{id}/          → Retrieve review detail
    PATCH  /api/v1/reviews/{id}/          → Edit own review
    DELETE /api/v1/reviews/{id}/          → Delete own review
    POST   /api/v1/reviews/{id}/helpful/  → Mark as helpful
    """
    queryset = Review.objects.select_related('author', 'product').prefetch_related('images')
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return ReviewCreateSerializer
        return ReviewSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def helpful(self, request, pk=None):
        """Mark a review as helpful. Increments the helpful_count by 1."""
        review = self.get_object()

        # Prevent authors from marking their own reviews as helpful
        if review.author == request.user:
            return Response(
                {'detail': 'No podés marcar tu propia reseña como útil.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])

        return Response(
            {'helpful_count': review.helpful_count},
            status=status.HTTP_200_OK,
        )
