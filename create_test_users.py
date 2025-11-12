"""
Script para crear usuarios de prueba:
1. Admin: Marcelo Jimenez (marcelojp03@gmail.com)
2. Cliente: Trevor Calero (trevorfelixcalerosuyo@gmail.com)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth import get_user_model
from customers.models import Customer

User = get_user_model()

def create_admin():
    """Crear usuario administrador"""
    print("\n" + "="*80)
    print("Creando usuario ADMIN...")
    print("="*80)
    
    # Verificar si ya existe
    if User.objects.filter(username='marcelojp03').exists():
        print("⚠️ El usuario 'marcelojp03' ya existe. Eliminando...")
        User.objects.get(username='marcelojp03').delete()
    
    # Crear superuser
    admin = User.objects.create_superuser(
        username='marcelojp03',
        email='marcelojp03@gmail.com',
        password='Admin123!',
        first_name='Marcelo',
        last_name='Jimenez'
    )
    
    print(f"✅ Admin creado exitosamente:")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Nombre: {admin.get_full_name()}")
    print(f"   is_staff: {admin.is_staff}")
    print(f"   is_superuser: {admin.is_superuser}")
    print(f"   Password: Admin123!")
    
    # Verificar que NO tenga perfil de cliente
    has_customer = hasattr(admin, 'customer')
    print(f"   Tiene perfil de cliente: {has_customer}")
    
    return admin

def create_customer():
    """Crear usuario cliente"""
    print("\n" + "="*80)
    print("Creando usuario CLIENTE...")
    print("="*80)
    
    # Verificar si ya existe
    if User.objects.filter(username='trevorcalero').exists():
        print("⚠️ El usuario 'trevorcalero' ya existe. Eliminando...")
        user = User.objects.get(username='trevorcalero')
        if hasattr(user, 'customer'):
            user.customer.delete()
        user.delete()
    
    # Crear usuario normal (NO staff)
    user = User.objects.create_user(
        username='trevorcalero',
        email='trevorfelixcalerosuyo@gmail.com',
        password='Cliente123!',
        first_name='Trevor',
        last_name='Calero',
        is_staff=False,
        is_superuser=False
    )
    
    print(f"✅ Usuario creado exitosamente:")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Nombre: {user.get_full_name()}")
    print(f"   is_staff: {user.is_staff}")
    print(f"   is_superuser: {user.is_superuser}")
    print(f"   Password: Cliente123!")
    
    # Crear perfil de cliente
    customer = Customer.objects.create(
        user=user,
        phone='75599887',
        address='Av. Banzer #1234',
        city='Santa Cruz',
        country='Bolivia',
        postal_code='0000'
    )
    
    print(f"\n✅ Perfil de cliente creado:")
    print(f"   ID: {customer.id}")
    print(f"   Teléfono: {customer.phone}")
    print(f"   Dirección: {customer.address}")
    print(f"   Ciudad: {customer.city}")
    print(f"   País: {customer.country}")
    
    return user, customer

def main():
    print("\n" + "#"*80)
    print("# CREACIÓN DE USUARIOS DE PRUEBA")
    print("#"*80)
    
    admin = create_admin()
    user, customer = create_customer()
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"\n👨‍💼 ADMIN:")
    print(f"   Username: marcelojp03")
    print(f"   Password: Admin123!")
    print(f"   Email: marcelojp03@gmail.com")
    print(f"   Login: http://127.0.0.1:8000/admin/")
    
    print(f"\n👤 CLIENTE:")
    print(f"   Username: trevorcalero")
    print(f"   Password: Cliente123!")
    print(f"   Email: trevorfelixcalerosuyo@gmail.com")
    print(f"   API Login: POST http://127.0.0.1:8000/api/customers/login/")
    
    print("\n" + "#"*80)
    print("✅ Usuarios creados exitosamente!")
    print("#"*80 + "\n")

if __name__ == '__main__':
    main()
