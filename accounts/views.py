# ... existing imports ...
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, NotificationSerializer
from django.contrib.auth import get_user_model

User = get_user_model() 

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Pour la création/édition de projet, on permet de voir tous les utilisateurs
        if self.action == 'list':
            return User.objects.all()
        # Pour les autres actions, on garde la restriction
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Les utilisateurs ne voient que leurs propres notifications
        return Notification.objects.filter(user=self.request.user)