from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    """
    Represents a technical skill that a team can possess.
    e.g. Python, Docker, Kubernetes, React
    Author: Sarin Pradhan (Student 1)
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    Core model representing an engineering team at Broadcast company.

    Key design decisions:
    - status uses soft-delete pattern (disbanded instead of delete)
    - upstream_dependencies is a self-referencing ManyToMany with symmetrical=False
      so that A depends on B does NOT mean B depends on A
    - downstream_dependents is the auto-generated reverse relation

    Author: Sarin Pradhan (Student 1)
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('restructured', 'Restructured'),
        ('disbanded', 'Disbanded'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(help_text="Team mission and responsibilities")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Links to Bigyan's (Student 2) organisation app
    department = models.ForeignKey(
        'organisation.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='teams'
    )

    # The manager is a registered Django user
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_teams'
    )

    # Contact channels
    slack_channel = models.CharField(max_length=100, blank=True, help_text="e.g. #team-name")
    teams_channel = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)

    # Skills and dependencies
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
        """Return all active memberships with user data pre-loaded."""
        return self.memberships.filter(is_active=True).select_related('user')

    def member_count(self):
        """Return count of active members."""
        return self.memberships.filter(is_active=True).count()


class TeamMembership(models.Model):
    """
    Junction table linking Users to Teams with a role.

    Uses is_active for soft-delete so membership history is preserved.
    unique_together prevents a user being in the same team twice.

    Author: Sarin Pradhan (Student 1)
    """
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
    """
    A code repository linked to a team.
    Supports GitHub, GitLab, Bitbucket, Azure DevOps.
    Uses is_active for soft-delete.

    Author: Sarin Pradhan (Student 1)
    """
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
