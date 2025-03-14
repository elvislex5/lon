from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('kanban/', views.task_kanban, name='kanban'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/status/', views.task_change_status, name='change_status'),
    path('<int:pk>/documents/add/', views.task_add_document, name='add_document'),
    path('documents/<int:pk>/delete/', views.task_delete_document, name='delete_document'),
    path('<int:pk>/log-time/', views.log_time, name='log_time'),
] 