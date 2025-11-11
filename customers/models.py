"""
Modelos para la app de customers
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Customer(models.Model):
    """
    Modelo de Cliente extendido desde User.
    Almacena información adicional del cliente del ecommerce.
    
    IMPORTANTE: Los clientes NO pueden ser usuarios staff ni superusers.
    Esta es una separación estricta entre clientes del ecommerce y administradores.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers_customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"
    
    def clean(self):
        """Validar que el usuario no sea staff ni superuser"""
        if self.user.is_staff or self.user.is_superuser:
            raise ValidationError({
                'user': 'Staff users and superusers cannot be customers. Customers and admins must be separate.'
            })
    
    def save(self, *args, **kwargs):
        """Validar antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Nombre completo del cliente"""
        return self.user.get_full_name()
    
    @property
    def email(self):
        """Email del cliente"""
        return self.user.email
