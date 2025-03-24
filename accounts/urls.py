from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

app_name = 'accounts'

urlpatterns = [
    path('api/', include(router.urls)),
] 