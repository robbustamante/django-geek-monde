from django.contrib import admin


class TimeStampedAdmin(admin.ModelAdmin):
    """Admin class for TimeStampedModel."""
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('created_at', 'updated_at')
