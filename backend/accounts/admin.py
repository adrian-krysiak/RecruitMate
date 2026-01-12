from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with additional fields."""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_premium', 'is_active', 'date_joined'
    )
    list_filter = (
        'is_premium', 'is_active', 'is_staff', 'date_joined'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('birth_date', 'is_premium')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'birth_date', 'is_premium')
        }),
    )
