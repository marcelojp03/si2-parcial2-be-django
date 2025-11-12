# 🚀 E-Commerce API - Guía Rápida

**Base URL:** `http://127.0.0.1:8000`  
**Swagger:** `http://127.0.0.1:8000/api/docs/`

---

## 📋 Endpoints por Módulo

### 🔧 SYSTEM
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/healthz/` | Estado del sistema |
| GET | `/api/docs/` | Documentación Swagger |
| GET | `/api/schema/` | Schema OpenAPI |

---

### 🔐 AUTHENTICATION - JWT (NUEVO)
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/token/` | 🔑 Obtener access + refresh tokens | ❌ Public |
| POST | `/api/auth/token/refresh/` | 🔄 Renovar access token | ❌ Public |
| POST | `/api/auth/token/verify/` | ✅ Validar token | ❌ Public |
| POST | `/api/auth/register/` | 👤 Registro de usuario | ❌ Public |
| GET | `/api/auth/me/` | 👤 Usuario actual | ✅ Required |
| GET | `/api/auth/menu/` | 📋 Menú dinámico | ✅ Required |
| POST | `/api/auth/logout/` | 🚪 Cerrar sesión | ✅ Required |

**Formato del token:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Respuesta de login:**
```json
{
  "access": "eyJ...",  // Válido por 1 hora
  "refresh": "eyJ..."  // Válido por 7 días
}
```

---

### 📦 CATALOG - Productos y Categorías
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/catalog/categories/` | Listar categorías |
| GET | `/api/catalog/categories/{id}/` | Detalle de categoría |
| GET | `/api/catalog/categories/root/` | Categorías raíz |
| POST | `/api/catalog/categories/` | Crear categoría |
| PUT/PATCH | `/api/catalog/categories/{id}/` | Actualizar categoría |
| DELETE | `/api/catalog/categories/{id}/` | Eliminar categoría |
| | |
| GET | `/api/catalog/attributes/` | Listar atributos |
| GET | `/api/catalog/attributes/{id}/` | Detalle de atributo |
| | |
| GET | `/api/catalog/products/` | Listar productos |
| GET | `/api/catalog/products/{id}/` | Detalle de producto |
| GET | `/api/catalog/products/featured/` | Productos destacados |
| POST | `/api/catalog/products/` | Crear producto |
| PUT/PATCH | `/api/catalog/products/{id}/` | Actualizar producto |
| DELETE | `/api/catalog/products/{id}/` | Eliminar producto |

**Filtros de productos:**
- `?category=1` - Por categoría
- `?search=camisa` - Búsqueda
- `?min_price=50&max_price=200` - Rango de precio
- `?featured=true` - Destacados

---

### 📊 INVENTORY - Almacenes e Inventario
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/inventory/warehouses/` | Listar almacenes |
| GET | `/api/inventory/warehouses/{id}/` | Detalle de almacén |
| GET | `/api/inventory/warehouses/{id}/inventory/` | Inventario del almacén |
| GET | `/api/inventory/warehouses/{id}/low_stock/` | Stock bajo del almacén |
| POST | `/api/inventory/warehouses/` | Crear almacén |
| | |
| GET | `/api/inventory/inventory/` | Listar inventario |
| GET | `/api/inventory/inventory/{id}/` | Detalle de inventario |
| POST | `/api/inventory/inventory/{id}/adjust_stock/` | ⚡ Ajustar stock |
| POST | `/api/inventory/inventory/{id}/reserve/` | ⚡ Reservar stock |
| POST | `/api/inventory/inventory/{id}/confirm_sale/` | ⚡ Confirmar venta |
| POST | `/api/inventory/inventory/{id}/release/` | ⚡ Liberar stock |

**Filtros de inventario:**
- `?warehouse=1` - Por almacén
- `?variant=5` - Por variante
- `?low_stock=true` - Stock bajo

---

### 🛒 SALES - Ventas y Pedidos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/sales/customers/` | Listar clientes |
| GET | `/api/sales/customers/{id}/` | Detalle de cliente |
| GET | `/api/sales/customers/{id}/orders/` | Pedidos del cliente |
| POST | `/api/sales/customers/` | Crear cliente |
| | |
| GET | `/api/sales/addresses/` | Listar direcciones |
| POST | `/api/sales/addresses/` | Crear dirección |
| | |
| GET | `/api/sales/carts/` | Listar carritos |
| GET | `/api/sales/carts/{id}/` | Detalle del carrito |
| POST | `/api/sales/carts/{id}/add_item/` | Agregar al carrito |
| POST | `/api/sales/carts/{id}/remove_item/{item_id}/` | Quitar del carrito |
| POST | `/api/sales/carts/{id}/clear/` | Vaciar carrito |
| POST | `/api/sales/carts/{id}/checkout/` | 🔥 Crear pedido |
| | |
| GET | `/api/sales/orders/` | Listar pedidos |
| GET | `/api/sales/orders/{id}/` | Detalle del pedido |
| POST | `/api/sales/orders/{id}/confirm_payment/` | 🔥 Confirmar pago |
| POST | `/api/sales/orders/{id}/cancel/` | ⚠️ Cancelar pedido |

**Estados de pedidos:**
- `CREATED` - Creado, pago pendiente
- `PAID` - Pagado
- `PROCESSING` - En proceso
- `SHIPPED` - Enviado
- `DELIVERED` - Entregado
- `CANCELLED` - Cancelado

**Filtros de pedidos:**
- `?customer=1` - Por cliente
- `?status=PAID` - Por estado

---

### 🔐 SECURITY - Usuarios y Permisos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Iniciar sesión |
| POST | `/api/auth/logout/` | Cerrar sesión |
| GET | `/api/auth/me/` | Usuario actual |
| GET | `/api/auth/menu/` | Menú dinámico |
| | |
| GET | `/api/auth/users/` | Listar usuarios |
| POST | `/api/auth/users/` | Crear usuario |
| POST | `/api/auth/users/{id}/change_password/` | Cambiar contraseña |
| | |
| GET | `/api/auth/roles/` | Listar roles |
| POST | `/api/auth/roles/` | Crear rol |
| | |
| GET | `/api/auth/resources/` | Listar recursos |
| GET | `/api/auth/permissions/` | Listar permisos |
| POST | `/api/auth/permissions/` | Asignar permiso |

---

### 📈 ANALYTICS - Reportes y Forecasting
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/analytics/sales/` | Listar hechos de ventas | ✅ Required |
| GET | `/api/analytics/sales/dashboard/` | 📊 Dashboard | ✅ Required |
| POST | `/api/analytics/sales/generate_report/` | Generar reporte | ✅ Required |
| | | |
| GET | `/api/analytics/forecasts/` | Listar forecasts | ✅ Required |
| POST | `/api/analytics/forecasts/` | Crear forecast | ✅ Required |
| POST | `/api/analytics/forecasts/{id}/predict/` | 🔮 Predecir ventas | ✅ Required |
| | | |
| GET | `/api/analytics/reports/` | Listar reportes | ✅ Required |
| POST | `/api/analytics/reports/` | Crear reporte | ✅ Required |
| **POST** | **`/api/analytics/reports/ai-report/`** | **🤖 Reporte con IA (NUEVO)** | **✅ Required** |

**🤖 AI Reports - Formatos disponibles:**
- `json` - Datos estructurados con interpretación IA
- `csv` - Archivo CSV descargable
- `excel` - Archivo .xlsx con estilos
- `pdf` - Documento PDF formateado

---

## � Flujo de Autenticación JWT

### 1️⃣ Login
```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."
}
```

### 2️⃣ Guardar Tokens
```javascript
// LocalStorage (React/Angular)
localStorage.setItem('access_token', response.access);
localStorage.setItem('refresh_token', response.refresh);

// O en memoria/state management (más seguro)
```

### 3️⃣ Usar en Requests
```javascript
// Axios Interceptor
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 4️⃣ Refresh Token (cuando expira)
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGc..."
}
```

**Respuesta:**
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc..."  // Nuevo refresh (rotación habilitada)
}
```

### 5️⃣ Verificar Token
```http
POST /api/auth/token/verify/
Content-Type: application/json

{
  "token": "eyJhbGc..."
}
```

---

## 🤖 Flujo de Reportes con IA

### 1️⃣ Generar Reporte JSON
```http
POST /api/analytics/reports/ai-report/
Authorization: Bearer <access_token>
Content-Type: application/json

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
    "sql": "SELECT date, SUM(revenue) as total FROM analytics_salefact...",
    "columns": ["date", "total"],
    "rows": [[...], [...]],
    "interpretation": "Las ventas de los últimos 7 días muestran...",
    "summary": {
      "total_rows": 7,
      "execution_time_ms": 234
    },
    "export_options": ["json", "csv", "excel", "pdf"]
  }
}
```

### 2️⃣ Exportar a Excel
```http
POST /api/analytics/reports/ai-report/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "query": "Top 10 productos más vendidos",
  "format": "excel",
  "limit": 10
}
```

**Respuesta:** Archivo `.xlsx` descargable

### 3️⃣ Dry Run (solo generar SQL)
```http
POST /api/analytics/reports/ai-report/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "query": "Total de ventas por categoría",
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
    "sql": "SELECT c.name, SUM(s.revenue) FROM..."
  }
}
```

---

## �🔥 Flujo de Compra Completo

### 1️⃣ Agregar al Carrito
```http
POST /api/sales/carts/1/add_item/
Content-Type: application/json

{
  "variant_id": 5,
  "quantity": 2
}
```

### 2️⃣ Ver Carrito
```http
GET /api/sales/carts/1/
```

### 3️⃣ Checkout (Crear Pedido)
```http
POST /api/sales/carts/1/checkout/
Content-Type: application/json

{
  "customer_id": 1,
  "shipping_address_id": 1,
  "payment_method": "CREDIT_CARD",
  "payment_provider": "MOCK"
}
```

**Resultado:** Pedido creado (CREATED), stock reservado

### 4️⃣ Confirmar Pago
```http
POST /api/sales/orders/1/confirm_payment/
Content-Type: application/json

{
  "idempotency_key": "unique-uuid-here",
  "provider": "STRIPE",
  "provider_ref": "ch_123456"
}
```

**Resultado:** 
- Pedido → PAID
- Stock decrementado
- SaleFact creado automáticamente

### 5️⃣ Ver en Analytics
```http
GET /api/analytics/sales/dashboard/?days=30
```

---

## ⚡ Características Avanzadas

### Concurrencia (Bloqueo Pesimista)
Los siguientes endpoints usan `select_for_update()`:
- `POST /api/sales/orders/{id}/confirm_payment/`
- `POST /api/sales/orders/{id}/cancel/`
- `POST /api/inventory/inventory/{id}/adjust_stock/`

### Idempotencia
El endpoint de confirmación de pago acepta `idempotency_key` para evitar duplicados.

### SaleFact Automático
Cuando un pedido cambia a `PAID`, se crea automáticamente un registro en `SaleFact` via signal.

### Validación de Estados
Máquina de estados estricta:
- Solo `CREATED` → `PAID`
- No cancelar si `SHIPPED` o `DELIVERED`

---

## 📊 Ejemplos de Respuestas

### Dashboard de Analytics
```json
{
  "period": "últimos 30 días",
  "metrics": {
    "total_revenue": 15847.50,
    "total_orders": 42,
    "avg_order_value": 377.32
  },
  "daily_sales": [...],
  "top_products": [...],
  "top_categories": [...]
}
```

### Detalle de Producto
```json
{
  "id": 1,
  "name": "Camisa Casual",
  "category": {...},
  "status": "ACTIVE",
  "is_featured": true,
  "variants": [
    {
      "id": 1,
      "code": "CAM-001-R-M",
      "price": 99.99,
      "stock_on_hand": 25,
      "attributes": [
        {"name": "Color", "value": "Rojo"},
        {"name": "Talla", "value": "M"}
      ]
    }
  ],
  "images": [...]
}
```

### Pedido Completo
```json
{
  "id": 1,
  "order_number": "ORD-2025110500001",
  "customer": {...},
  "status": "PAID",
  "payment_status": "PAID",
  "subtotal": 199.98,
  "total": 226.08,
  "items": [...],
  "payment": {
    "provider": "MOCK",
    "status": "SUCCESS",
    "paid_at": "2025-11-05T10:15:00Z"
  }
}
```

---

## 🛠️ Paginación

Todos los endpoints de listado soportan:
- `?page=2` - Número de página
- `?page_size=20` - Elementos por página (max: 100)

**Respuesta:**
```json
{
  "count": 150,
  "next": "http://...?page=3",
  "previous": "http://...?page=1",
  "results": [...]
}
```

---

## 🔍 Búsqueda y Filtros

### Productos
```http
GET /api/catalog/products/?search=camisa&category=1&min_price=50&max_price=200
```

### Pedidos
```http
GET /api/sales/orders/?customer=1&status=PAID&search=ORD-2025
```

### Inventario
```http
GET /api/inventory/inventory/?warehouse=1&low_stock=true
```

---

## 💾 Datos de Prueba

### Superusuario
```
Username: admin
Password: (configurado durante creación)
```

### Datos Precargados
- ✅ 6 categorías
- ✅ 4 atributos (Color, Talla, Material, Estilo)
- ✅ 19 valores de atributos
- ✅ 3 almacenes (Principal, Norte, Sur)

---

## 🚦 Códigos de Estado

- `200 OK` - Éxito
- `201 Created` - Creado
- `400 Bad Request` - Error en datos
- `404 Not Found` - No encontrado
- `500 Internal Server Error` - Error del servidor
- `503 Service Unavailable` - Servicio no disponible

---

## 📱 CORS

El backend acepta peticiones de:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://127.0.0.1:8000` (mismo origen)

---

## 💰 Configuración de Negocio

- **Moneda:** BOB (Bolivianos)
- **IVA:** 13%
- **Formatos de fecha:** ISO 8601 (`2025-11-05T10:30:00Z`)

---

## 🔗 Links Útiles

- **API Docs:** http://127.0.0.1:8000/api/docs/
- **ReDoc:** http://127.0.0.1:8000/api/redoc/
- **Admin:** http://127.0.0.1:8000/admin/
- **Healthcheck:** http://127.0.0.1:8000/api/healthz/

---

**Para documentación completa ver:** `API_DOCUMENTATION.md`
