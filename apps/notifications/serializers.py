from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones."""

    class Meta:
        model = Notification
        fields = (
            'id', 'notification_type', 'title', 'message',
            'is_read', 'email_sent', 'created_at'
        )
        read_only_fields = ('id', 'created_at')