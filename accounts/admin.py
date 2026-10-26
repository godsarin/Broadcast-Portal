from django.contrib import admin
from .models import UserProfile, AuditLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'job_title', 'department', 'phone']
    search_fields = ['user__username', 'user__email', 'job_title']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'description', 'timestamp']
    list_filter = ['action', 'model_name']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'description', 'timestamp']

from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']