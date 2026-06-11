from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'email_sent', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Relación', {
            'fields': ('order',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_read', 'email_sent')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
