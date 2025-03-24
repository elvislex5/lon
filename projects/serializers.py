from rest_framework import serializers
from .models import Project
from accounts.serializers import UserSerializer
from clients.serializers import ClientSerializer

class ProjectSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    team_members = UserSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_statistics = serializers.ReadOnlyField()
    progress = serializers.ReadOnlyField()
    is_delayed = serializers.ReadOnlyField()
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_details = ClientSerializer(source='client', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'location', 'start_date', 'end_date',
            'status', 'status_display', 'budget', 'manager', 'team_members',
            'created_at', 'updated_at', 'task_statistics', 'progress', 'is_delayed',
            'client', 'client_name', 'client_details'
        ]

class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'location', 'start_date', 'end_date',
            'status', 'budget', 'team_members'
        ]