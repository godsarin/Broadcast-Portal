from django import forms
from django.contrib.auth.models import User
from .models import Message


class ComposeForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Write your message...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['recipient'].label_from_instance = lambda u: f"{u.get_full_name() or u.username} ({u.email})"
