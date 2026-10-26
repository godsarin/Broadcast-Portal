from django import forms
from .models import Department, TeamType


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'specialisation', 'leader', 'email', 'slack_channel']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'specialisation': forms.TextInput(attrs={'class': 'form-control'}),
            'leader': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'slack_channel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#dept-channel'}),
        }


class TeamTypeForm(forms.ModelForm):
    class Meta:
        model = TeamType
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
