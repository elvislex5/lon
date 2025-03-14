from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'status', 'manager', 'start_date', 'end_date')
    list_filter = ('status', 'manager')
    search_fields = ('name', 'location', 'description')
    date_hierarchy = 'start_date'
    filter_horizontal = ('team_members',)
