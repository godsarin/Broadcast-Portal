from django.contrib import admin
from .models import Team, TeamMembership, CodeRepository, Skill


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1


class CodeRepositoryInline(admin.TabularInline):
    model = CodeRepository
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'manager', 'status', 'member_count', 'created_at']
    list_filter = ['status', 'department']
    search_fields = ['name', 'description']
    filter_horizontal = ['skills', 'upstream_dependencies']
    inlines = [TeamMembershipInline, CodeRepositoryInline]

    def member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    member_count.short_description = 'Members'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active']


@admin.register(CodeRepository)
class CodeRepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'platform', 'is_active']
    list_filter = ['platform', 'is_active']
