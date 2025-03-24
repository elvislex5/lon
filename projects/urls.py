from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.ProjectViewSet, basename='project')

app_name = 'projects'

urlpatterns = [
    path('', include(router.urls)),
]