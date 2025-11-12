#!/usr/bin/env python
"""Script para crear usuario admin de prueba"""
from security.models import User

# Crear o actualizar usuario admin
username = 'admin'
email = 'admin@ecommerce.com'
password = 'admin123'

try:
    user = User.objects.get(username=username)
    print(f"✓ Usuario '{username}' ya existe")
    # Actualizar contraseña por si cambió
    user.set_password(password)
    user.save()
    print(f"✓ Contraseña actualizada para '{username}'")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Admin',
        last_name='Sistema'
    )
    print(f"✓ Usuario '{username}' creado exitosamente")

print(f"\nCredenciales:")
print(f"  Username: {username}")
print(f"  Password: {password}")
print(f"  Email: {email}")
