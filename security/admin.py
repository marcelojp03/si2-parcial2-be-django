from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Resource, Subresource, RoleResource


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('phone', 'avatar')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'description']
    search_fields = ['name']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'icon', 'description']
    list_editable = ['order']
    ordering = ['order', 'name']


@admin.register(Subresource)
class SubresourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'resource', 'url', 'order']
    list_filter = ['resource']
    list_editable = ['order']
    ordering = ['resource', 'order']


@admin.register(RoleResource)
class RoleResourceAdmin(admin.ModelAdmin):
    list_display = ['role', 'resource', 'subresource']
    list_filter = ['role', 'resource']
    search_fields = ['role__name', 'resource__name', 'subresource__name']

