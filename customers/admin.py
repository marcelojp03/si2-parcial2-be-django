from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email', 'phone', 'city', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    list_filter = ['country', 'city', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',),
            'description': 'WARNING: Only non-staff users can be customers. Staff/superusers cannot have customer profiles.'
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'country', 'postal_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar para mostrar solo usuarios NO staff en el dropdown"""
        if db_field.name == "user":
            # Solo mostrar usuarios que NO sean staff ni superuser
            from django.contrib.auth import get_user_model
            User = get_user_model()
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Validar antes de guardar y mostrar mensaje de error amigable"""
        try:
            obj.save()
        except ValidationError as e:
            # Mostrar mensaje de error en el admin
            messages.error(request, f"Cannot save customer: {e.message_dict.get('user', ['Unknown error'])[0]}")
            return
        
        if not change:
            messages.success(request, f"Customer {obj} was created successfully.")
        else:
            messages.success(request, f"Customer {obj} was updated successfully.")
