from django import forms
from .models import Team, TeamMembership, CodeRepository, Skill


class TeamForm(forms.ModelForm):
    """
    Form for creating and editing a Team.

    All widgets use Bootstrap CSS classes (form-control, form-select)
    for consistent styling.

    Skills and upstream_dependencies use CheckboxSelectMultiple so
    users can tick multiple options without holding Ctrl.

    The __init__ method filters upstream_dependencies to only show
    active teams, and excludes the current team when editing
    (a team cannot depend on itself).

    Author: Sarin Pradhan (Student 1)
    """
    class Meta:
        model = Team
        fields = [
            'name', 'description', 'status', 'department', 'manager',
            'slack_channel', 'teams_channel', 'email', 'skills',
            'upstream_dependencies'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'slack_channel': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '#team-channel'
            }),
            'teams_channel': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'skills': forms.CheckboxSelectMultiple(),
            'upstream_dependencies': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active teams as dependency options
        self.fields['upstream_dependencies'].queryset = Team.objects.filter(
            status='active'
        )
        # Exclude the current team from its own upstream options when editing
        if self.instance and self.instance.pk:
            self.fields['upstream_dependencies'].queryset = Team.objects.filter(
                status='active'
            ).exclude(pk=self.instance.pk)


class TeamMembershipForm(forms.ModelForm):
    """
    Form for adding a user to a team with a specific role.

    Author: Sarin Pradhan (Student 1)
    """
    class Meta:
        model = TeamMembership
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class CodeRepositoryForm(forms.ModelForm):
    """
    Form for adding a code repository to a team.
    Supports GitHub, GitLab, Bitbucket, Azure DevOps.

    Author: Sarin Pradhan (Student 1)
    """
    class Meta:
        model = CodeRepository
        fields = ['name', 'url', 'platform', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
