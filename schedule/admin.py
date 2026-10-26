from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'organiser', 'date_time', 'platform', 'status', 'attendee_count']
    list_filter = ['status', 'platform']
    search_fields = ['title', 'organiser__username']
    filter_horizontal = ['attendees']
