from django import forms
from .models import Task, TaskDocument

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assigned_to', 
                 'status', 'priority', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Filtrer les projets où l'utilisateur est membre ou manager
            self.fields['project'].queryset = user.projects.all() | user.managed_projects.all()
            # Filtrer les assignations aux membres des projets
            if self.instance and self.instance.pk and self.instance.project:
                self.fields['assigned_to'].queryset = self.instance.project.team_members.all()
            else:
                self.fields['assigned_to'].queryset = self.fields['assigned_to'].queryset.none()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        status = cleaned_data.get('status')
        old_status = self.instance.status if self.instance.pk else None

        # Validation des dates
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                "La date de début ne peut pas être postérieure à la date de fin."
            )

        # Validation du changement de statut
        if old_status and status != old_status:
            valid_transitions = Task.VALID_STATUS_TRANSITIONS.get(old_status, [])
            if status not in valid_transitions:
                raise forms.ValidationError(
                    f"Impossible de passer directement de '{self.instance.get_status_display()}' à '{dict(Task.STATUS_CHOICES)[status]}'"
                )

        return cleaned_data

class TaskDocumentForm(forms.ModelForm):
    class Meta:
        model = TaskDocument
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        } 