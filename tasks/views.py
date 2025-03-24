import logging
from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            logger.info(f"User requesting tasks: {user.username}")
            
            # Log des projets de l'utilisateur
            user_projects = user.projects.all()
            managed_projects = user.managed_projects.all()
            logger.info(f"User projects: {[p.name for p in user_projects]}")
            logger.info(f"User managed projects: {[p.name for p in managed_projects]}")
            
            queryset = Task.objects.filter(
                models.Q(assigned_to=user) |
                models.Q(project__team_members=user) |
                models.Q(project__manager=user)
            ).distinct()
            
            # Log des tâches trouvées
            tasks_found = list(queryset.values_list('title', flat=True))
            logger.info(f"Found {queryset.count()} tasks: {tasks_found}")
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            raise

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=400)
            
        task.status = new_status
        task.save()
        return Response(TaskSerializer(task).data)