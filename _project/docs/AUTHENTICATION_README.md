# ================================================
# RESUMEN FINAL - AUTENTICACIÓN JWT IMPLEMENTADA
# ================================================

## ✅ SEPARACIÓN DE ROLES IMPLEMENTADA (Opción A)

### Usuarios Creados:
1. **ADMIN (Marcelo Jimenez)**
   - Username: `marcelojp03`
   - Password: `Admin123!`
   - Email: `marcelojp03@gmail.com`
   - Acceso: Django Admin Panel → http://127.0.0.1:8000/admin/
   - Permisos: is_staff=True, is_superuser=True
   - NO puede: Tener perfil de cliente, usar API de clientes

2. **CLIENTE (Trevor Calero)**
   - Username: `trevorcalero`
   - Password: `Cliente123!`
   - Email: `trevorfelixcalerosuyo@gmail.com`
   - Acceso: API REST → http://127.0.0.1:8000/api/customers/
   - Perfil ID: 4
   - Datos: Teléfono, Dirección, Ciudad (Santa Cruz), País (Bolivia)

---

## 🔐 ENDPOINTS DE AUTENTICACIÓN

### 1. Register (Crear cuenta)
```bash
POST http://127.0.0.1:8000/api/customers/register/
Content-Type: application/json

{
  "username": "nuevo_cliente",
  "email": "nuevo@ejemplo.com",
  "password": "Password123!",
  "password2": "Password123!",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "phone": "75512345",
  "city": "Santa Cruz",
  "country": "Bolivia"
}
```

### 2. Login (Obtener tokens)
```bash
POST http://127.0.0.1:8000/api/customers/login/
Content-Type: application/json

# Opción 1: Login con EMAIL (recomendado)
{
  "username": "trevorfelixcalerosuyo@gmail.com",
  "password": "Cliente123!"
}

# Opción 2: Login con USERNAME (también funciona)
{
  "username": "trevorcalero",
  "password": "Cliente123!"
}

# Respuesta:
{
  "user": {
    "id": 8,
    "username": "trevorcalero",
    "email": "trevorfelixcalerosuyo@gmail.com",
    "first_name": "Trevor",
    "last_name": "Calero"
  },
  "tokens": {
    "access": "eyJhbGci...",
    "refresh": "eyJhbGci..."
  },
  "message": "Login successful"
}
```

**Nota**: El campo `username` acepta tanto el username como el email para mayor flexibilidad.

### 3. Ver Perfil (Requiere token)
```bash
GET http://127.0.0.1:8000/api/customers/profile/
Authorization: Bearer <access_token>
```

### 4. Actualizar Perfil
```bash
PATCH http://127.0.0.1:8000/api/customers/profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "phone": "77788899",
  "address": "Nueva dirección",
  "city": "La Paz"
}
```

### 5. Cambiar Contraseña
```bash
PUT http://127.0.0.1:8000/api/customers/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "Cliente123!",
  "new_password": "NuevaPassword123!",
  "new_password2": "NuevaPassword123!"
}
```

### 6. Refresh Token
```bash
POST http://127.0.0.1:8000/api/customers/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

### 7. Logout (Blacklist token)
```bash
POST http://127.0.0.1:8000/api/customers/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

## 🛡️ VALIDACIONES IMPLEMENTADAS

### En RegisterSerializer (customers/serializers.py):
- ✅ Valida que username no pertenezca a usuario staff
- ✅ Valida que email no pertenezca a usuario staff
- ✅ Crea usuarios con `is_staff=False` y `is_superuser=False`

### En Customer Model (customers/models.py):
- ✅ Método `clean()` valida que user no sea staff ni superuser
- ✅ Método `save()` ejecuta validación antes de guardar
- ✅ Mensaje claro: "Staff users and superusers cannot be customers"

### En CustomerAdmin (customers/admin.py):
- ✅ Dropdown filtra solo usuarios NO staff
- ✅ Mensaje de advertencia en el formulario
- ✅ Validación al guardar con mensaje de error amigable

---

## ✅ TESTS REALIZADOS

### Test 1: Separación de Roles (test_role_separation.py)
- ✅ Usuario staff NO puede tener perfil de cliente
- ✅ Cliente NO puede ser promovido a staff
- ✅ Superuser NO puede tener perfil de cliente
- ✅ Usuario normal SÍ puede ser cliente
**Resultado: 4/4 tests pasados**

### Test 2: Endpoints con Usuarios Reales
- ✅ Login de cliente Trevor Calero funciona
- ✅ Se obtienen tokens JWT (access + refresh)
- ✅ Perfil del cliente se puede consultar
- ✅ Admin Marcelo NO puede hacer login en API de clientes
- ✅ No se puede registrar con email de admin

---

## 📝 CONFIGURACIÓN JWT

### Ubicación: ecommerce/settings.py
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ISSUER': 'ecommerce-api',
}
```

### Apps Instaladas:
- `rest_framework`
- `rest_framework_simplejwt`
- `rest_framework_simplejwt.token_blacklist`
- `customers`

---

## 📊 ESTRUCTURA DE BASE DE DATOS

### Tabla: customers_customer
```
id | user_id | phone | address | city | country | postal_code | created_at | updated_at
```

### Relación:
- Customer.user → OneToOneField → security.User
- Cada cliente tiene UN usuario asociado
- Un usuario puede tener CERO o UN cliente (si es staff = 0)

---

## 🔍 COMANDOS ÚTILES

### Ver usuarios en base de datos:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.all().values('id', 'username', 'email', 'is_staff', 'is_superuser')
```

### Ver clientes:
```python
from customers.models import Customer
Customer.objects.all().values('id', 'user__username', 'phone', 'city')
```

### Crear admin desde shell:
```python
User.objects.create_superuser('admin', 'admin@example.com', 'pass')
```

### Crear cliente desde shell:
```python
user = User.objects.create_user('cliente', 'cliente@example.com', 'pass', is_staff=False)
Customer.objects.create(user=user, phone='123456', city='Santa Cruz')
```

---

## 📚 DOCUMENTACIÓN API

Swagger/OpenAPI: http://127.0.0.1:8000/api/docs/
Cada endpoint tiene documentación completa con ejemplos

---

## ✨ RESUMEN TÉCNICO

**Tecnologías:**
- Django 5.2.7
- Django REST Framework
- djangorestframework-simplejwt 5.5.1
- PostgreSQL
- JWT Authentication

**Características:**
- ✅ Autenticación JWT para clientes
- ✅ Separación estricta: Admins ≠ Clientes
- ✅ Token blacklist para logout seguro
- ✅ Refresh tokens con rotación
- ✅ Validaciones en múltiples capas
- ✅ API RESTful completa
- ✅ Documentación Swagger

**Seguridad:**
- Passwords hasheados con PBKDF2
- Tokens firmados con HS256
- Blacklist de tokens en logout
- Validación de permisos en cada capa
- Protección de emails/usernames de staff

---

## 🎯 PRÓXIMOS PASOS SUGERIDOS

1. Crear endpoints de Carrito de Compras
2. Implementar proceso de Checkout
3. Agregar historial de Órdenes
4. Crear sistema de Wishlist
5. Agregar verificación de email
6. Implementar reset de contraseña
7. Agregar 2FA (opcional)
8. Crear endpoints de Reviews/Ratings

---

**Implementado por:** Sistema de Autenticación JWT
**Fecha:** 11 de Noviembre, 2025
**Estado:** ✅ Completado y Probado
