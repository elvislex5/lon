from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'function', 'company')
    list_filter = ('is_staff', 'is_active', 'function', 'company')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('phone', 'function', 'company')}),
    )
