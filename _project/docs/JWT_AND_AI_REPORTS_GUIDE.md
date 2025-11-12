# 🔐 Guía de JWT y Reportes con IA

## ✅ Implementación Completada

Se ha agregado exitosamente:
1. **JWT Authentication** con djangorestframework-simplejwt
2. **Sistema de respuestas personalizadas** (ApiResponse)
3. **Reportes con IA** usando OpenAI GPT-4o-mini
4. **Exportación a CSV, Excel y PDF**

---

## 🔑 Endpoints JWT

### 1. Obtener Token (Login)

```http
POST http://127.0.0.1:8000/api/auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Refrescar Token

```http
POST http://127.0.0.1:8000/api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  // Nuevo refresh token (ROTATE_REFRESH_TOKENS=True)
}
```

### 3. Verificar Token

```http
POST http://127.0.0.1:8000/api/auth/token/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta (Token válido):**
```json
{}
```

**Respuesta (Token inválido):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

### 4. Registro de Usuario

```http
POST http://127.0.0.1:8000/api/auth/register/
Content-Type: application/json

{
  "username": "nuevo_usuario",
  "email": "usuario@example.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "data": {
    "id": 2,
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "full_name": "Juan Pérez"
  }
}
```

---

## 🔐 Usar JWT en Requests

Una vez que tienes el `access` token, inclúyelo en el header de todas las peticiones:

```http
GET http://127.0.0.1:8000/api/catalog/products/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 🤖 Reportes con IA

### Endpoint Principal

```http
POST http://127.0.0.1:8000/api/analytics/reports/ai-report/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

### Ejemplos de Consultas

#### 1. Reporte en JSON (con interpretación)

```json
{
  "query": "Muéstrame las ventas de los últimos 7 días",
  "format": "json",
  "limit": 100
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "OK",
  "data": {
    "sql": "SELECT date, SUM(revenue) as total_revenue, COUNT(*) as orders FROM analytics_salefact WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date DESC LIMIT 100",
    "columns": ["date", "total_revenue", "orders"],
    "rows": [
      {"date": "2025-11-09", "total_revenue": 1234.56, "orders": 15},
      {"date": "2025-11-08", "total_revenue": 987.65, "orders": 12}
    ],
    "interpretation": "En los últimos 7 días, has registrado ventas diarias que van desde 987.65 BOB hasta 1,234.56 BOB, con un promedio de 12-15 órdenes por día. El día con mejores ventas fue el 9 de noviembre con 1,234.56 BOB.",
    "summary": {
      "total_rows": 7,
      "execution_time_ms": 245
    },
    "export_options": ["json", "csv", "excel", "pdf"]
  }
}
```

#### 2. Exportar a CSV

```json
{
  "query": "Lista de productos vendidos este mes",
  "format": "csv",
  "limit": 500
}
```

**Respuesta:** Archivo CSV descargable

#### 3. Exportar a Excel

```json
{
  "query": "Top 10 productos más vendidos",
  "format": "excel",
  "limit": 10
}
```

**Respuesta:** Archivo .xlsx descargable con formato profesional

#### 4. Exportar a PDF

```json
{
  "query": "Resumen de ventas por categoría",
  "format": "pdf"
}
```

**Respuesta:** Archivo PDF descargable con tabla formateada

#### 5. Dry Run (Solo generar SQL)

```json
{
  "query": "Cuántos clientes tengo registrados",
  "format": "json",
  "dry_run": true
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "SQL generado (dry-run)",
  "data": {
    "sql": "SELECT COUNT(*) as total_clientes FROM sales_customer LIMIT 100"
  }
}
```

---

## 📊 Ejemplos de Consultas en Lenguaje Natural

### Consultas Simples

```
"¿Cuántas ventas tengo hoy?"
"Muéstrame todos los productos"
"Lista de clientes activos"
"Total de pedidos de esta semana"
```

### Consultas con Filtros

```
"Ventas del mes de octubre"
"Productos de la categoría 'Ropa'"
"Pedidos con estado PAID"
"Clientes que compraron en noviembre"
```

### Consultas con Agregaciones

```
"Total de ingresos por día en los últimos 30 días"
"Top 5 productos más vendidos"
"Promedio de ventas por mes"
"Cantidad de órdenes por estado"
```

### Consultas Complejas con JOINs

```
"Muéstrame las ventas por categoría de producto"
"Lista de pedidos con nombre de cliente y productos"
"Inventario disponible por almacén"
"Productos con stock bajo de 10 unidades"
```

---

## ⚙️ Configuración JWT

**Archivo:** `ecommerce/settings.py`

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Token dura 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh dura 7 días
    'ROTATE_REFRESH_TOKENS': True,                    # Rota refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,                 # Invalida tokens anteriores
    'UPDATE_LAST_LOGIN': True,                        # Actualiza last_login
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ISSUER': 'ecommerce-api',
}
```

---

## 🔒 Permisos Actualizados

Por defecto, **todos los endpoints requieren autenticación JWT**:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Para admin
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Endpoints Públicos (No requieren JWT)

- `POST /api/auth/token/` - Obtener token
- `POST /api/auth/register/` - Registro de usuarios
- `POST /api/auth/login/` - Login con sesión (legacy)
- `GET /api/healthz/` - Healthcheck
- `GET /api/docs/` - Swagger UI
- `GET /api/schema/` - OpenAPI Schema

---

## 🧪 Probar en Swagger

1. Abre **Swagger UI**: http://127.0.0.1:8000/api/docs/
2. Haz clic en el botón **"Authorize"** (candado verde)
3. Ingresa tu token JWT en el formato:
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```
4. Haz clic en **"Authorize"**
5. Ahora puedes probar cualquier endpoint desde Swagger

---

## 🚀 Flujo Completo de Uso

### 1. Obtener Token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Guardar Access Token

```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 3. Usar Token en Requests

```bash
# Ver productos
curl -X GET http://127.0.0.1:8000/api/catalog/products/ \
  -H "Authorization: Bearer $TOKEN"

# Generar reporte con IA
curl -X POST http://127.0.0.1:8000/api/analytics/reports/ai-report/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Muéstrame las ventas de hoy","format":"json"}'
```

### 4. Refrescar Token cuando expire

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

---

## ⚠️ Manejo de Errores

### Token Expirado

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is expired"
    }
  ]
}
```

**Solución:** Usar el refresh token para obtener uno nuevo.

### Sin Token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solución:** Agregar header `Authorization: Bearer TOKEN`

### Reporte IA - OpenAI no configurado

```json
{
  "success": false,
  "message": "OpenAI no configurado en el servidor",
  "data": null
}
```

**Solución:** Agregar `OPENAI_API_KEY` en el archivo `.env`

---

## 📦 Dependencias Instaladas

```
djangorestframework-simplejwt==5.5.1
openai==2.7.1
openpyxl==3.1.5
reportlab==4.4.4
```

---

## 🎯 Siguiente Paso

Ahora el backend está **100% funcional** con:

- ✅ JWT Authentication
- ✅ Reportes con IA (OpenAI)
- ✅ Exportación CSV/Excel/PDF
- ✅ Sistema de respuestas consistente
- ✅ Todos los endpoints protegidos

**Estado final:** Backend producción-ready 🚀

---

## 📞 Testing Rápido

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 2. Usar el access token que te devuelve
# Reemplaza TOKEN_AQUI con tu token real
curl -X GET http://127.0.0.1:8000/api/catalog/products/ \
  -H "Authorization: Bearer TOKEN_AQUI"

# 3. Probar reporte con IA
curl -X POST http://127.0.0.1:8000/api/analytics/reports/ai-report/ \
  -H "Authorization: Bearer TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"query":"cuantos productos hay","format":"json"}'
```

---

**Última actualización:** 9 de noviembre de 2025
