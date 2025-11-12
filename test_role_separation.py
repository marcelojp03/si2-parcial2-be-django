"""
Script de prueba para verificar la separación de roles entre admins y clientes.

Este script prueba que:
1. Un usuario staff NO puede tener perfil de cliente
2. Un cliente NO puede ser promovido a staff
3. Las validaciones funcionan correctamente
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth import get_user_model
from customers.models import Customer
from django.core.exceptions import ValidationError

User = get_user_model()

def test_staff_cannot_be_customer():
    """Probar que un usuario staff no puede ser cliente"""
    print("\n" + "="*80)
    print("TEST 1: Usuario staff NO puede tener perfil de cliente")
    print("="*80)
    
    # Crear un usuario staff
    staff_user = User.objects.create_user(
        username='staff_test_user',
        email='staff@test.com',
        password='testpass123',
        is_staff=True
    )
    print(f"✓ Usuario staff creado: {staff_user.username} (is_staff={staff_user.is_staff})")
    
    try:
        # Intentar crear perfil de cliente para el usuario staff
        customer = Customer.objects.create(user=staff_user)
        print("❌ ERROR: Se permitió crear un cliente con usuario staff!")
        customer.delete()
        return False
    except ValidationError as e:
        print(f"✓ CORRECTO: Se bloqueó la creación del cliente")
        print(f"  Mensaje: {e.message_dict.get('user', ['Unknown'])[0]}")
        staff_user.delete()
        return True

def test_customer_cannot_be_staff():
    """Probar que un cliente no puede ser promovido a staff"""
    print("\n" + "="*80)
    print("TEST 2: Cliente NO puede ser promovido a staff")
    print("="*80)
    
    # Crear un usuario normal (cliente)
    user = User.objects.create_user(
        username='customer_test_user',
        email='customer@test.com',
        password='testpass123',
        is_staff=False
    )
    print(f"✓ Usuario creado: {user.username} (is_staff={user.is_staff})")
    
    # Crear perfil de cliente
    customer = Customer.objects.create(
        user=user,
        phone='1234567890',
        city='Santa Cruz'
    )
    print(f"✓ Perfil de cliente creado: {customer}")
    
    # Intentar promover a staff
    try:
        user.is_staff = True
        user.save()
        # Intentar re-guardar el customer (esto debería fallar)
        customer.save()
        print("❌ ERROR: Se permitió que un cliente sea staff!")
        customer.delete()
        user.delete()
        return False
    except ValidationError as e:
        print(f"✓ CORRECTO: Se bloqueó la promoción a staff")
        print(f"  Mensaje: {e.message_dict.get('user', ['Unknown'])[0]}")
        # Limpiar
        user.is_staff = False
        user.save()
        customer.delete()
        user.delete()
        return True

def test_superuser_cannot_be_customer():
    """Probar que un superuser no puede ser cliente"""
    print("\n" + "="*80)
    print("TEST 3: Superuser NO puede tener perfil de cliente")
    print("="*80)
    
    # Crear un superuser
    superuser = User.objects.create_superuser(
        username='super_test_user',
        email='super@test.com',
        password='testpass123'
    )
    print(f"✓ Superuser creado: {superuser.username} (is_superuser={superuser.is_superuser})")
    
    try:
        # Intentar crear perfil de cliente para el superuser
        customer = Customer.objects.create(user=superuser)
        print("❌ ERROR: Se permitió crear un cliente con superuser!")
        customer.delete()
        return False
    except ValidationError as e:
        print(f"✓ CORRECTO: Se bloqueó la creación del cliente")
        print(f"  Mensaje: {e.message_dict.get('user', ['Unknown'])[0]}")
        superuser.delete()
        return True

def test_normal_user_can_be_customer():
    """Probar que un usuario normal SÍ puede ser cliente"""
    print("\n" + "="*80)
    print("TEST 4: Usuario normal SÍ puede ser cliente")
    print("="*80)
    
    # Crear un usuario normal
    user = User.objects.create_user(
        username='normal_test_user',
        email='normal@test.com',
        password='testpass123',
        is_staff=False,
        is_superuser=False
    )
    print(f"✓ Usuario normal creado: {user.username} (is_staff={user.is_staff}, is_superuser={user.is_superuser})")
    
    try:
        # Crear perfil de cliente
        customer = Customer.objects.create(
            user=user,
            phone='9876543210',
            city='La Paz',
            country='Bolivia'
        )
        print(f"✓ CORRECTO: Perfil de cliente creado exitosamente")
        print(f"  Cliente: {customer.full_name} - {customer.email}")
        print(f"  Ciudad: {customer.city}, País: {customer.country}")
        
        # Limpiar
        customer.delete()
        user.delete()
        return True
    except ValidationError as e:
        print(f"❌ ERROR: No se pudo crear el cliente")
        print(f"  Mensaje: {e}")
        user.delete()
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "#"*80)
    print("# TESTS DE SEPARACIÓN DE ROLES: ADMINS vs CLIENTES")
    print("#"*80)
    
    results = []
    
    # Ejecutar tests
    results.append(("Staff cannot be customer", test_staff_cannot_be_customer()))
    results.append(("Customer cannot be staff", test_customer_cannot_be_staff()))
    results.append(("Superuser cannot be customer", test_superuser_cannot_be_customer()))
    results.append(("Normal user can be customer", test_normal_user_can_be_customer()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nResultado: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron! La separación de roles funciona correctamente.")
    else:
        print(f"\n⚠️ {total - passed} test(s) fallaron. Revisar implementación.")
    
    print("\n" + "#"*80)

if __name__ == '__main__':
    main()
