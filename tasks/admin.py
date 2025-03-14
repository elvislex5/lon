from django.contrib import admin
from django.utils.html import format_html
from .models import Task, TaskDocument

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'colored_status', 'colored_priority', 
                   'assigned_to', 'start_date', 'end_date', 'is_overdue_status')
    list_filter = ('status', 'priority', 'project', 'assigned_to')
    search_fields = ('title', 'description', 'project__name')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at', 'created_by')

    def colored_status(self, obj):
        colors = {
            'todo': '#6c757d',       # Gris
            'in_progress': '#0d6efd', # Bleu
            'review': '#ffc107',     # Jaune
            'done': '#198754',       # Vert
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )
    colored_status.short_description = 'Statut'

    def colored_priority(self, obj):
        colors = {
            'low': '#6c757d',      # Gris
            'medium': '#0d6efd',    # Bleu
            'high': '#ffc107',      # Jaune
            'urgent': '#dc3545',    # Rouge
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors[obj.priority],
            obj.get_priority_display()
        )
    colored_priority.short_description = 'Priorité'

    def is_overdue_status(self, obj):
        return obj.is_overdue
    is_overdue_status.boolean = True
    is_overdue_status.short_description = "En retard ?"

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle tâche
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TaskDocument)
class TaskDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'task__title')
