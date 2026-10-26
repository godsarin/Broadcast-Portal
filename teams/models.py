from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Team(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('restructured', 'Restructured'),
        ('disbanded', 'Disbanded'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(help_text="Team mission and responsibilities")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    department = models.ForeignKey(
        'organisation.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='teams'
    )
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_teams'
    )
    slack_channel = models.CharField(max_length=100, blank=True, help_text="e.g. #team-name")
    teams_channel = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    upstream_dependencies = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='downstream_dependents'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_members(self):
        return self.memberships.filter(is_active=True).select_related('user')

    def member_count(self):
        return self.memberships.filter(is_active=True).count()


class TeamMembership(models.Model):
    ROLE_CHOICES = [
        ('engineer', 'Engineer'),
        ('senior_engineer', 'Senior Engineer'),
        ('lead', 'Tech Lead'),
        ('manager', 'Manager'),
        ('qa', 'QA Engineer'),
        ('devops', 'DevOps Engineer'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='engineer')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.team.name}"


class CodeRepository(models.Model):
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('bitbucket', 'Bitbucket'),
        ('azure', 'Azure DevOps'),
        ('other', 'Other'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=200)
    url = models.URLField()
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='github')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Code Repositories"

    def __str__(self):
        return f"{self.name} ({self.team.name})"
