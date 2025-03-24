from django.db import models
from django.conf import settings
from django.utils import timezone
from clients.models import Client

class Project(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Nouveau'),
        ('SIGNED', 'Signé'),
        ('IN_PROGRESS', 'En cours'),
        ('PAID', 'Payé'),
        ('LOST', 'Perdu')
    ]

    name = models.CharField(max_length=200, verbose_name="Nom du projet")
    description = models.TextField(blank=True, verbose_name="Description")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Client")
    location = models.CharField(max_length=200, verbose_name="Lieu")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin prévue")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='NEW',
        verbose_name="Statut"
    )
    budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Budget estimé"
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='managed_projects',
        verbose_name="Chef de projet"
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        verbose_name="Membres de l'équipe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def task_statistics(self):
        """Retourne les statistiques des tâches du projet"""
        stats = {
            'total': self.tasks.count(),
            'todo': self.tasks.filter(status='todo').count(),
            'in_progress': self.tasks.filter(status='in_progress').count(),
            'review': self.tasks.filter(status='review').count(),
            'done': self.tasks.filter(status='done').count()
        }
        stats['completion_rate'] = (stats['done'] / stats['total'] * 100) if stats['total'] > 0 else 0
        return stats

    @property
    def is_delayed(self):
        """Vérifie si le projet a des tâches en retard"""
        return self.tasks.filter(end_date__lt=timezone.now().date()).exclude(status='done').exists()

    @property
    def progress(self):
        """Calcule la progression globale du projet"""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        
        # Pondération des statuts
        weights = {
            'done': 1.0,
            'review': 0.75,
            'in_progress': 0.5,
            'todo': 0.0
        }
        
        weighted_sum = sum(
            self.tasks.filter(status=status).count() * weight
            for status, weight in weights.items()
        )
        
        progress = (weighted_sum / total_tasks) * 100
        return round(progress, 1)
