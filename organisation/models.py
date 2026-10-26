from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    specialisation = models.CharField(max_length=200, blank=True)
    leader = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='led_departments'
    )
    email = models.EmailField(blank=True)
    slack_channel = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def team_count(self):
        return self.teams.filter(status='active').count()


class TeamType(models.Model):
    """Classifies team types e.g. Platform, Product, Enablement"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color code')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class OrganisationStructure(models.Model):
    """Captures the org structure for visualisation"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return self.name
