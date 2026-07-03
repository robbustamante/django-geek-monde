from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestionar notificaciones del usuario."""
    queryset = Notification.objects.none()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retorna notificaciones del usuario autenticado."""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Obtiene notificaciones no leídas."""
        unread = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread, many=True)
        return Response({
            'count': unread.count(),
            'notifications': serializer.data
        })

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marca una notificación como leída."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marca todas las notificaciones como leídas."""
        unread_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({
            'success': True,
            'marked_as_read': unread_count
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtiene estadísticas de notificaciones."""
        all_notifications = self.get_queryset()
        unread_count = all_notifications.filter(is_read=False).count()

        by_type = dict(
            all_notifications.values('notification_type')
            .annotate(count=models.Count('id'))
            .values_list('notification_type', 'count')
        )

        return Response({
            'total': all_notifications.count(),
            'unread': unread_count,
            'by_type': by_type
        })