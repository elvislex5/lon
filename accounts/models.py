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
