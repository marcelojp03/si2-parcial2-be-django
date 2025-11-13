from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """
    Usuario extendido del sistema.
    Permite agregar campos personalizados como foto, teléfono, etc.
    """
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.CharField(max_length=400, blank=True)  # URL pública de la imagen
    avatar_s3_key = models.CharField(max_length=500, blank=True, null=True)
    avatar_s3_bucket = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'administration_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username


class Role(models.Model):
    """
    Rol del sistema vinculado a un Group de Django.
    Ejemplo: Admin, Vendedor, Almacenero, Reportes
    """
    name = models.CharField(max_length=50, unique=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    description = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'administration_role'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class Resource(models.Model):
    """
    Recurso principal del menú.
    Ejemplo: Catálogo, Ventas, Inventario, Reportes
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'administration_resource'
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Subresource(models.Model):
    """
    Subrecurso o página específica dentro de un recurso.
    Ejemplo: Productos, Categorías (bajo Catálogo)
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="subs")
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    url = models.CharField(max_length=120, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'administration_subresource'
        verbose_name = 'Subrecurso'
        verbose_name_plural = 'Subrecursos'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.resource.name} > {self.name}"


class RoleResource(models.Model):
    """
    Asignación de permisos: qué subrecursos puede ver cada rol.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    subresource = models.ForeignKey(Subresource, on_delete=models.CASCADE)

    class Meta:
        db_table = 'administration_role_resource'
        unique_together = ("role", "resource", "subresource")
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'

    def __str__(self):
        return f"{self.role.name} -> {self.subresource}"
