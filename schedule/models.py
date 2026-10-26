from django.db import models
from django.contrib.auth.models import User


class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('meet', 'Google Meet'),
        ('slack', 'Slack Huddle'),
        ('in_person', 'In Person'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    organiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organised_meetings')
    attendees = models.ManyToManyField(User, related_name='meetings', blank=True)
    team = models.ForeignKey(
        'teams.Team', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='meetings'
    )
    date_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='teams')
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=300, blank=True)
    message = models.TextField(blank=True, help_text="Agenda or additional notes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']

    def __str__(self):
        return f"{self.title} - {self.date_time.strftime('%d %b %Y %H:%M')}"

    def attendee_count(self):
        return self.attendees.count()
