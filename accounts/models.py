from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
import secrets
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Téléphone")
    function = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fonction")
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Entreprise")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lue")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"Notification pour {self.user.username}"

