from django.db import models
from django.conf import settings
from projects.models import Project
from django.utils import timezone
import os
from django.core.exceptions import ValidationError
from datetime import timedelta
from datetime import datetime, time


class Task(models.Model):
    """
    Modèle représentant une tâche dans un projet.
    Une tâche est associée à un projet, peut être assignée à un utilisateur,
    et a un statut, une priorité, des dates de début et de fin.
    """
    # Choix pour le statut de la tâche
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('review', 'En révision'),
        ('done', 'Terminé')
    ]

    # Choix pour la priorité de la tâche
    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente')
    ]

    # Champ pour le titre de la tâche
    title = models.CharField(max_length=200, verbose_name="Titre")

    # Champ pour la description de la tâche (optionnel)
    description = models.TextField(blank=True, verbose_name="Description")

    # Clé étrangère vers le projet associé à la tâche
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Projet"
    )

    # Clé étrangère vers l'utilisateur qui a créé la tâche
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_tasks',
        verbose_name="Créé par",
        null=True,
        blank=True
    )

    # Clé étrangère vers l'utilisateur assigné à la tâche (optionnel)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name="Assigné à"
    )

    # Champ pour le statut de la tâche (parmi les choix définis)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="Statut"
    )

    # Champ pour la priorité de la tâche (parmi les choix définis)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priorité"
    )

    # Champ pour la date de début de la tâche (optionnel)
    start_date = models.DateField(
        verbose_name="Date de début",
        null=True,
        blank=True
    )

    # Champ pour la date de fin de la tâche (optionnel)
    end_date = models.DateField(
        verbose_name="Date de fin",
        null=True,
        blank=True
    )

    # Champ pour la date de création de la tâche (automatique)
    created_at = models.DateTimeField(auto_now_add=True)

    # Champ pour la date de dernière mise à jour de la tâche (automatique)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def elapsed_time(self):
        """
        Retourne le nombre d'heures écoulées depuis la création de la tâche.
        """
        elapsed = timezone.now() - self.created_at
        return round(elapsed.total_seconds() / 3600, 2)

    @property
    def duration_days(self):
        """
        Retourne la durée prévue en jours (entre la date de début et la date de fin).
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None

    @property
    def is_overdue(self):
        """
        Vérifie si la tâche est en retard (date de fin dépassée et statut non terminé).
        """
        if self.end_date and self.status != 'done':
            return timezone.now().date() > self.end_date
        return False

    @property
    def progress_days(self):
        """
        Retourne le nombre de jours écoulés depuis le début de la tâche.
        """
        if self.start_date:
            elapsed = timezone.now().date() - self.start_date
            return elapsed.days + 1
        return None

    @property
    def delay_days(self):
        """
        Retourne le nombre de jours de retard (si la tâche est en retard).
        """
        if self.is_overdue:
            return (timezone.now().date() - self.end_date).days
        return 0

    @property
    def time_difference(self):
        """
        Calcule la différence de temps de manière détaillée (jours, heures, minutes).
        """
        # Convertir end_date en datetime
        end_datetime = datetime.combine(self.end_date, time(23, 59, 59))
        end_datetime = timezone.make_aware(end_datetime)  # Rendre timezone-aware

        if self.status == 'done':
            # Pour les tâches terminées
            diff = self.updated_at - end_datetime
        else:
            # Pour les tâches en cours
            diff = timezone.now() - end_datetime

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        return {
            'days': abs(days),
            'hours': hours,
            'minutes': minutes,
            'is_late': diff.total_seconds() > 0
        }

    @property
    def delay_status(self):
        """
        Retourne un message formaté sur le retard ou le temps restant.
        """
        if self.status == 'done':
            return None

        diff = self.time_difference
        if diff['is_late']:
            msg = "En retard de "
            if diff['days'] > 0:
                msg += f"{diff['days']} jour{'s' if diff['days'] > 1 else ''}"
            if diff['hours'] > 0:
                msg += f" {diff['hours']}h"
            if diff['minutes'] > 0:
                msg += f" {diff['minutes']}min"
            return msg.strip()
        else:
            msg = "Plus que "
            if diff['days'] > 0:
                msg += f"{diff['days']} jour{'s' if diff['days'] > 1 else ''}"
            if diff['hours'] > 0:
                msg += f" {diff['hours']}h"
            if diff['minutes'] > 0:
                msg += f" {diff['minutes']}min"
            return msg.strip()

    @property
    def completion_status(self):
        """
        Retourne le statut de complétion de la tâche (avec retard ou avance).
        """
        if self.status != 'done':
            return None

        diff = self.time_difference
        completion_date = self.updated_at.strftime('%d/%m/%Y à %H:%M')

        if diff['is_late']:
            msg = f"Terminée le {completion_date}, avec "
            if diff['days'] > 0:
                msg += f"{diff['days']} jour{'s' if diff['days'] > 1 else ''}"
            if diff['hours'] > 0:
                msg += f" {diff['hours']}h"
            if diff['minutes'] > 0:
                msg += f" {diff['minutes']}min"
            return msg + " de retard"
        else:
            msg = f"Terminée le {completion_date}, avec "
            if diff['days'] > 0:
                msg += f"{diff['days']} jour{'s' if diff['days'] > 1 else ''}"
            if diff['hours'] > 0:
                msg += f" {diff['hours']}h"
            if diff['minutes'] > 0:
                msg += f" {diff['minutes']}min"
            return msg + " d'avance"

    def clean(self):
        """
        Validation personnalisée pour s'assurer que la date de début n'est pas postérieure à la date de fin
        et que les transitions de statut sont valides.
        """
        super().clean()
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({
                    'start_date': "La date de début ne peut pas être postérieure à la date de fin.",
                    'end_date': "La date de fin ne peut pas être antérieure à la date de début."
                })

        if self.pk:  # Si la tâche existe déjà
            old_task = Task.objects.get(pk=self.pk)
            if old_task.status != self.status:  # Si le statut a changé
                if self.status not in VALID_STATUS_TRANSITIONS.get(old_task.status, []):
                    raise ValidationError({
                        'status': f"Impossible de passer directement de '{old_task.get_status_display()}' à '{self.get_status_display()}'"
                    })

    class Meta:
        """
        Métadonnées pour le modèle Task.
        """
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['-priority', 'end_date', '-created_at']

    def __str__(self):
        """
        Représentation en chaîne de caractères de la tâche.
        """
        return f"{self.title} - {self.project.name}"


def validate_file_size(value):
    """
    Valide que la taille du fichier ne dépasse pas 10MB.
    """
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("La taille maximale du fichier est de 10MB")


class TaskDocument(models.Model):
    """
    Modèle représentant un document associé à une tâche.
    """
    # Clé étrangère vers la tâche associée
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Tâche"
    )

    # Champ pour le fichier (avec validation de taille)
    file = models.FileField(
        upload_to='task_documents/%Y/%m/',
        validators=[validate_file_size],
        verbose_name="Fichier"
    )

    # Champ pour le titre du document
    title = models.CharField(
        max_length=255,
        verbose_name="Titre"
    )

    # Clé étrangère vers l'utilisateur qui a téléchargé le document
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name="Téléchargé par"
    )

    # Champ pour la date d'ajout du document (automatique)
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )

    class Meta:
        """
        Métadonnées pour le modèle TaskDocument.
        """
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-uploaded_at']

    def __str__(self):
        """
        Représentation en chaîne de caractères du document.
        """
        return self.title

    def filename(self):
        """
        Retourne le nom du fichier (sans le chemin).
        """
        return os.path.basename(self.file.name)

    def extension(self):
        """
        Retourne l'extension du fichier.
        """
        name, extension = os.path.splitext(self.file.name)
        return extension[1:] if extension else ""

    def delete(self, *args, **kwargs):
        """
        Supprime le fichier physique avant de supprimer l'objet de la base de données.
        """
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


# Dictionnaire des transitions de statut valides
VALID_STATUS_TRANSITIONS = {
    'todo': ['in_progress'],
    'in_progress': ['review', 'todo'],
    'review': ['done', 'in_progress'],
    'done': ['review']
}
