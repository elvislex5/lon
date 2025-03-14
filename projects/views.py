from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from django.db import models
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

# Create your views here.

@login_required
def project_list(request):
    # Voir les projets où l'utilisateur est manager OU membre
    projects = Project.objects.filter(
        models.Q(manager=request.user) |
        models.Q(team_members=request.user)
    ).distinct().order_by('-created_at')
    
    return render(request, 'projects/project_list.html', {
        'projects': projects
    })

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Vérifier l'accès
        if self.request.user not in project.team_members.all() and self.request.user != project.manager:
            raise PermissionDenied("Vous n'avez pas accès à ce projet.")
        
        # Filtrer les tâches
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        search_query = self.request.GET.get('q')
        
        tasks = project.tasks.all().order_by('end_date')  # Tri par défaut
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        if search_query:
            tasks = tasks.filter(title__icontains=search_query)
            
        context['tasks'] = tasks
        context['task_statistics'] = project.task_statistics
        return context

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            form.save_m2m()  # Pour sauvegarder les relations ManyToMany
            messages.success(request, 'Projet créé avec succès.')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Nouveau Projet'
    })

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.manager:
        messages.error(request, "Vous n'avez pas la permission de modifier ce projet.")
        return redirect('projects:detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projet modifié avec succès.')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/project_form.html', {
        'form': form,
        'project': project,
        'title': 'Modifier le Projet'
    })
