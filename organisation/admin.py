from django.contrib import admin
from .models import Department, TeamType, OrganisationStructure


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'specialisation', 'team_count', 'created_at']
    search_fields = ['name', 'specialisation']

    def team_count(self, obj):
        return obj.teams.filter(status='active').count()
    team_count.short_description = 'Active Teams'


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(OrganisationStructure)
class OrganisationStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_current', 'created_at']
