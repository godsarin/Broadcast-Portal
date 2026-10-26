from django import forms
from django.utils import timezone
from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'team', 'attendees',
            'date_time', 'duration_minutes', 'platform',
            'meeting_link', 'location', 'message', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'date_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 480}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room/Location'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Agenda...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        from teams.models import Team

        self.fields['attendees'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['attendees'].label_from_instance = lambda u: u.get_full_name() or u.username
        self.fields['date_time'].input_formats = ['%Y-%m-%dT%H:%M']

        # Only show active teams in related team dropdown
        self.fields['team'].queryset = Team.objects.filter(status='active')

        if not self.is_edit:
            # Only when creating — hide status and set min date
            self.fields.pop('status')
            now = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
            self.fields['date_time'].widget.attrs['min'] = now

        # Pre-fill date when editing
        if self.instance and self.instance.pk and self.instance.date_time:
            self.initial['date_time'] = timezone.localtime(
                self.instance.date_time
            ).strftime('%Y-%m-%dT%H:%M')