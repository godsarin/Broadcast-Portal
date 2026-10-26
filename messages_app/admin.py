from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'status', 'is_read', 'created_at']
    list_filter = ['status', 'is_read']
    search_fields = ['subject', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'sent_at']
