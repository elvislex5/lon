from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Task, TaskDocument
from .forms import TaskForm, TaskDocumentForm
from django.db import models


# Vue pour afficher le tableau Kanban des tâches
@login_required
def task_kanban(request):
    """
    Affiche un tableau Kanban des tâches pour l'utilisateur connecté.
    Les tâches sont filtrées pour inclure celles assignées à l'utilisateur ou dans ses projets.
    Les tâches sont organisées par statut (todo, in_progress, review, done).
    """
    # Récupérer les tâches de l'utilisateur (assignées ou dans ses projets)
    tasks = Task.objects.filter(
        models.Q(assigned_to=request.user) |
        models.Q(project__team_members=request.user) |
        models.Q(project__manager=request.user)
    ).distinct()

    # Organiser les tâches par statut
    tasks_by_status = {
        'todo': tasks.filter(status='todo'),
        'in_progress': tasks.filter(status='in_progress'),
        'review': tasks.filter(status='review'),
        'done': tasks.filter(status='done')
    }

    return render(request, 'tasks/task_kanban.html', {
        'tasks_by_status': tasks_by_status,
        'status_choices': Task.STATUS_CHOICES
    })


@login_required
def task_change_status(request, pk):
    """
    Permet de changer le statut d'une tâche via une requête AJAX.
    Seuls le manager du projet ou l'utilisateur assigné à la tâche peuvent modifier son statut.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        task = get_object_or_404(Task, pk=pk)
        if request.user != task.project.manager and request.user != task.assigned_to:
            return JsonResponse({'status': 'error', 'message': 'Permission refusée'}, status=403)

        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def task_create(request):
    """
    Permet de créer une nouvelle tâche.
    Seuls les managers de projet peuvent créer des tâches.
    """
    # Vérifier si l'utilisateur est manager d'au moins un projet
    if not request.user.managed_projects.exists():
        messages.error(request, "Seuls les managers de projet peuvent créer des tâches.")
        return redirect('tasks:list')

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Tâche créée avec succès.')
            return redirect('tasks:kanban')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Nouvelle Tâche'
    })


@login_required
def task_list(request):
    """
    Affiche la liste des tâches de l'utilisateur connecté.
    Les tâches incluent celles assignées à l'utilisateur ou dans ses projets.
    """
    tasks = Task.objects.filter(
        models.Q(assigned_to=request.user) |
        models.Q(project__team_members=request.user) |
        models.Q(project__manager=request.user)
    ).distinct()
    return render(request, 'tasks/task_list.html', {
        'tasks': tasks
    })


@login_required
def task_detail(request, pk):
    """
    Affiche les détails d'une tâche spécifique.
    Seuls l'utilisateur assigné, le manager du projet ou les membres de l'équipe peuvent accéder à cette vue.
    """
    task = get_object_or_404(Task, pk=pk)
    if request.user not in [task.assigned_to, task.project.manager] and \
            request.user not in task.project.team_members.all():
        messages.error(request, "Vous n'avez pas accès à cette tâche.")
        return redirect('tasks:list')
    return render(request, 'tasks/task_detail.html', {
        'task': task
    })


@login_required
def task_edit(request, pk):
    """
    Permet de modifier une tâche existante.
    Seul le manager du projet peut modifier la tâche.
    """
    task = get_object_or_404(Task, pk=pk)
    # Seul le manager peut modifier
    if request.user != task.project.manager:
        messages.error(request, "Vous n'avez pas la permission de modifier cette tâche.")
        return redirect('tasks:detail', pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tâche modifiée avec succès.')
            return redirect('tasks:detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Modifier la tâche'
    })


@login_required
def task_add_document(request, pk):
    """
    Permet d'ajouter un document à une tâche.
    Seuls les membres de l'équipe ou le manager du projet peuvent ajouter des documents.
    """
    task = get_object_or_404(Task, pk=pk)
    # Vérifier si l'utilisateur est membre du projet
    if request.user not in task.project.team_members.all() and request.user != task.project.manager:
        messages.error(request, "Vous devez être membre du projet pour ajouter des documents.")
        return redirect('tasks:detail', pk=pk)

    if request.method == 'POST':
        form = TaskDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.task = task
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document ajouté avec succès.')
            return redirect('tasks:detail', pk=task.pk)
    else:
        form = TaskDocumentForm()

    return render(request, 'tasks/task_document_form.html', {
        'form': form,
        'task': task
    })


@login_required
def task_delete_document(request, pk):
    """
    Permet de supprimer un document associé à une tâche.
    Seul l'utilisateur qui a uploadé le document ou le manager du projet peut le supprimer.
    """
    document = get_object_or_404(TaskDocument, pk=pk)
    task = document.task

    if request.user != document.uploaded_by and request.user != task.project.manager:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce document.")
        return redirect('tasks:detail', pk=task.pk)

    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document supprimé avec succès.')
        return redirect('tasks:detail', pk=task.pk)

    return render(request, 'tasks/task_document_confirm_delete.html', {
        'document': document,
        'task': task
    })


@login_required
def log_time(request, pk):
    """
    Permet d'ajouter du temps passé sur une tâche.
    Seul l'utilisateur assigné à la tâche peut ajouter du temps.
    """
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST' and request.user == task.assigned_to:
        hours = float(request.POST.get('hours', 0))
        comment = request.POST.get('comment', '')

        # Mettre à jour le temps passé
        task.time_spent = (task.time_spent or 0) + hours
        task.save()

        messages.success(request, f'{hours} heures ajoutées à la tâche.')
    return redirect('tasks:detail', pk=pk)

# ... autres vues à venir ...
