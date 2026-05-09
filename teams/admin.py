from django.contrib import admin
from .models import Team, TeamMembership, CodeRepository, Skill


class TeamMembershipInline(admin.TabularInline):
    """
    Allows editing team memberships directly on the Team admin page.
    Shows as a table beneath the team form.
    """
    model = TeamMembership
    extra = 1


class CodeRepositoryInline(admin.TabularInline):
    """
    Allows adding code repositories directly on the Team admin page.
    """
    model = CodeRepository
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Team model.

    - list_display: columns shown in the team list view
    - list_filter: right-side filter panel
    - search_fields: search box at the top
    - filter_horizontal: nice dual-panel widget for ManyToMany fields
    - inlines: edit members and repos directly on the team page

    Author: Sarin Pradhan (Student 1)
    """
    list_display = ['name', 'department', 'manager', 'status', 'member_count', 'created_at']
    list_filter = ['status', 'department']
    search_fields = ['name', 'description']
    filter_horizontal = ['skills', 'upstream_dependencies']
    inlines = [TeamMembershipInline, CodeRepositoryInline]

    def member_count(self, obj):
        """Custom column showing number of active members."""
        return obj.memberships.filter(is_active=True).count()
    member_count.short_description = 'Members'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin for Skill lookup table. Author: Sarin Pradhan (Student 1)"""
    list_display = ['name']
    search_fields = ['name']


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """Admin for TeamMembership. Author: Sarin Pradhan (Student 1)"""
    list_display = ['user', 'team', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active']


@admin.register(CodeRepository)
class CodeRepositoryAdmin(admin.ModelAdmin):
    """Admin for CodeRepository. Author: Sarin Pradhan (Student 1)"""
    list_display = ['name', 'team', 'platform', 'is_active']
    list_filter = ['platform', 'is_active']
