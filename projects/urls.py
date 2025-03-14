from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('create/', views.project_create, name='create'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
] 