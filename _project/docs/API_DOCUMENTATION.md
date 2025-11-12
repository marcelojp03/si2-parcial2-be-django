# 📚 Documentación API - E-Commerce Backend

**Versión:** 2.0 (Con JWT y AI Reports)  
**Base URL:** `http://127.0.0.1:8000`  
**Swagger UI:** `http://127.0.0.1:8000/api/docs/`  
**Fecha:** 9 de Noviembre, 2025

---

## 🔐 Autenticación JWT

**✅ Sistema JWT completamente implementado**

La API utiliza JWT (JSON Web Tokens) para autenticación segura.  
**Todos los endpoints requieren autenticación excepto:** login, register, catálogo público y healthcheck.

### Endpoints de Autenticación

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Respuesta:**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@ecommerce.com",
    "full_name": "Administrador"
  },
  "message": "Login exitoso"
}
```

#### Logout
```http
POST /api/auth/logout/
```

#### Usuario Actual
```http
GET /api/auth/me/
```

#### Menú Dinámico
```http
GET /api/auth/menu/
```

Retorna el menú basado en los permisos del rol del usuario.

---

## 📦 Módulo: CATALOG

Gestión de categorías, atributos y productos.

### Categorías

#### Listar Categorías
```http
GET /api/catalog/categories/
```

**Query Parameters:**
- `page` - Número de página
- `page_size` - Elementos por página

**Respuesta:**
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Ropa",
      "description": "Ropa y accesorios",
      "parent": null,
      "children": [
        {
          "id": 2,
          "name": "Ropa de Hombre",
          "parent": 1
        }
      ]
    }
  ]
}
```

#### Detalle de Categoría
```http
GET /api/catalog/categories/{id}/
```

#### Crear Categoría
```http
POST /api/catalog/categories/
Content-Type: application/json

{
  "name": "Nueva Categoría",
  "description": "Descripción",
  "parent": null
}
```

#### Actualizar Categoría
```http
PUT /api/catalog/categories/{id}/
PATCH /api/catalog/categories/{id}/
```

#### Eliminar Categoría
```http
DELETE /api/catalog/categories/{id}/
```

#### Categorías Raíz
```http
GET /api/catalog/categories/root/
```

Retorna solo las categorías de nivel superior.

---

### Atributos

#### Listar Atributos
```http
GET /api/catalog/attributes/
```

**Respuesta:**
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "name": "Color",
      "display_name": "Color",
      "values": [
        {
          "id": 1,
          "value": "Rojo",
          "display_value": "Rojo"
        },
        {
          "id": 2,
          "value": "Azul",
          "display_value": "Azul"
        }
      ]
    }
  ]
}
```

#### Detalle de Atributo
```http
GET /api/catalog/attributes/{id}/
```

---

### Productos

#### Listar Productos
```http
GET /api/catalog/products/
```

**Query Parameters:**
- `category` - ID de categoría para filtrar
- `search` - Búsqueda por nombre o descripción
- `min_price` - Precio mínimo
- `max_price` - Precio máximo
- `featured` - `true` para productos destacados
- `page` - Número de página
- `page_size` - Elementos por página

**Ejemplos:**
```http
GET /api/catalog/products/?category=1
GET /api/catalog/products/?search=camisa
GET /api/catalog/products/?min_price=50&max_price=200
GET /api/catalog/products/?featured=true
```

**Respuesta (Lista):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Camisa Casual",
      "slug": "camisa-casual",
      "description": "Camisa de algodón",
      "status": "ACTIVE",
      "is_featured": true,
      "category_names": ["Ropa", "Ropa de Hombre"],
      "main_image": "https://example.com/image.jpg",
      "price_range": {
        "min": 89.99,
        "max": 129.99
      }
    }
  ]
}
```

#### Detalle de Producto
```http
GET /api/catalog/products/{id}/
```

**Respuesta (Detalle):**
```json
{
  "id": 1,
  "name": "Camisa Casual",
  "slug": "camisa-casual",
  "description": "Camisa de algodón de alta calidad",
  "category": {
    "id": 2,
    "name": "Ropa de Hombre"
  },
  "status": "ACTIVE",
  "is_featured": true,
  "variants": [
    {
      "id": 1,
      "code": "CAM-001-R-M",
      "sku": "CAM001RM",
      "price": 99.99,
      "compare_at_price": 129.99,
      "cost": 50.00,
      "stock_on_hand": 25,
      "attributes": [
        {"name": "Color", "value": "Rojo"},
        {"name": "Talla", "value": "M"}
      ]
    }
  ],
  "images": [
    {
      "id": 1,
      "url": "https://example.com/image1.jpg",
      "alt_text": "Vista frontal",
      "is_primary": true,
      "sort_order": 0
    }
  ],
  "created_at": "2025-11-04T10:00:00Z"
}
```

#### Crear Producto
```http
POST /api/catalog/products/
Content-Type: application/json

{
  "name": "Nuevo Producto",
  "description": "Descripción del producto",
  "category": 1,
  "status": "ACTIVE",
  "is_featured": false
}
```

#### Actualizar Producto
```http
PUT /api/catalog/products/{id}/
PATCH /api/catalog/products/{id}/
```

#### Eliminar Producto
```http
DELETE /api/catalog/products/{id}/
```

#### Productos Destacados
```http
GET /api/catalog/products/featured/
```

---

## 📊 Módulo: INVENTORY

Gestión de almacenes e inventario.

### Almacenes

#### Listar Almacenes
```http
GET /api/inventory/warehouses/
```

**Respuesta:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "code": "WH-MAIN",
      "name": "Almacén Principal",
      "location": "Av. Principal 123",
      "is_active": true,
      "total_products": 150,
      "created_at": "2025-11-04T10:00:00Z"
    }
  ]
}
```

#### Detalle de Almacén
```http
GET /api/inventory/warehouses/{id}/
```

#### Crear Almacén
```http
POST /api/inventory/warehouses/
Content-Type: application/json

{
  "code": "WH-NORTE",
  "name": "Almacén Norte",
  "location": "Zona Norte",
  "is_active": true
}
```

#### Inventario de Almacén
```http
GET /api/inventory/warehouses/{id}/inventory/
```

Retorna todo el inventario de un almacén específico.

#### Stock Bajo en Almacén
```http
GET /api/inventory/warehouses/{id}/low_stock/
```

Retorna productos con stock por debajo del mínimo.

---

### Inventario

#### Listar Inventario
```http
GET /api/inventory/inventory/
```

**Query Parameters:**
- `warehouse` - ID del almacén
- `variant` - ID de la variante
- `low_stock` - `true` para stock bajo
- `page` - Número de página

**Ejemplos:**
```http
GET /api/inventory/inventory/?warehouse=1
GET /api/inventory/inventory/?low_stock=true
GET /api/inventory/inventory/?variant=5
```

**Respuesta:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "variant": 1,
      "variant_code": "CAM-001-R-M",
      "warehouse": 1,
      "warehouse_name": "Almacén Principal",
      "stock_on_hand": 25,
      "stock_reserved": 5,
      "stock_available": 20,
      "min_stock": 10,
      "updated_at": "2025-11-05T08:00:00Z"
    }
  ]
}
```

#### Detalle de Inventario
```http
GET /api/inventory/inventory/{id}/
```

#### Ajustar Stock
```http
POST /api/inventory/inventory/{id}/adjust_stock/
Content-Type: application/json

{
  "quantity": 10,
  "reason": "Recepción de mercancía"
}
```

**Respuesta:**
```json
{
  "message": "Stock ajustado exitosamente",
  "inventory": {
    "id": 1,
    "stock_on_hand": 35,
    "stock_available": 30
  }
}
```

#### Reservar Stock
```http
POST /api/inventory/inventory/{id}/reserve/
Content-Type: application/json

{
  "quantity": 3
}
```

Reserva stock para un pedido pendiente.

#### Confirmar Venta
```http
POST /api/inventory/inventory/{id}/confirm_sale/
Content-Type: application/json

{
  "quantity": 3
}
```

Confirma una venta y descuenta del stock físico y reservado.

#### Liberar Stock
```http
POST /api/inventory/inventory/{id}/release/
Content-Type: application/json

{
  "quantity": 2
}
```

Libera stock reservado (por cancelación de pedido).

---

## 🛒 Módulo: SALES

Gestión de clientes, carritos y pedidos.

### Clientes

#### Listar Clientes
```http
GET /api/sales/customers/
```

**Query Parameters:**
- `search` - Buscar por nombre, email, CI/NIT
- `page` - Número de página

**Respuesta:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "full_name": "Juan Pérez",
      "email": "juan@example.com",
      "phone": "70123456",
      "ci_nit": "1234567",
      "is_active": true,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

#### Detalle de Cliente
```http
GET /api/sales/customers/{id}/
```

#### Crear Cliente
```http
POST /api/sales/customers/
Content-Type: application/json

{
  "full_name": "María López",
  "email": "maria@example.com",
  "phone": "71234567",
  "ci_nit": "7654321"
}
```

#### Actualizar Cliente
```http
PUT /api/sales/customers/{id}/
PATCH /api/sales/customers/{id}/
```

#### Pedidos del Cliente
```http
GET /api/sales/customers/{id}/orders/
```

---

### Direcciones

#### Listar Direcciones
```http
GET /api/sales/addresses/
```

**Query Parameters:**
- `customer` - ID del cliente

**Ejemplo:**
```http
GET /api/sales/addresses/?customer=1
```

**Respuesta:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "customer": 1,
      "line1": "Av. Busch #123",
      "city": "Santa Cruz",
      "state": "Santa Cruz",
      "zip": "0000",
      "notes": "Casa blanca",
      "is_default": true
    }
  ]
}
```

#### Crear Dirección
```http
POST /api/sales/addresses/
Content-Type: application/json

{
  "customer": 1,
  "line1": "Calle Falsa 123",
  "city": "La Paz",
  "state": "La Paz",
  "zip": "0000",
  "notes": "Edificio azul, piso 3",
  "is_default": false
}
```

---

### Carritos

#### Listar Carritos
```http
GET /api/sales/carts/
```

#### Detalle del Carrito
```http
GET /api/sales/carts/{id}/
```

**Respuesta:**
```json
{
  "id": 1,
  "customer": {
    "id": 1,
    "full_name": "Juan Pérez"
  },
  "items": [
    {
      "id": 1,
      "variant": {
        "id": 1,
        "code": "CAM-001-R-M",
        "name": "Camisa Casual - Rojo - M",
        "price": 99.99
      },
      "qty": 2,
      "unit_price": 99.99,
      "subtotal": 199.98
    }
  ],
  "total_items": 2,
  "total_amount": 199.98,
  "created_at": "2025-11-05T08:00:00Z",
  "updated_at": "2025-11-05T09:30:00Z"
}
```

#### Agregar Item al Carrito
```http
POST /api/sales/carts/{id}/add_item/
Content-Type: application/json

{
  "variant_id": 1,
  "quantity": 2
}
```

**Respuesta:**
```json
{
  "id": 1,
  "items": [...],
  "total_items": 4,
  "total_amount": 399.96
}
```

#### Eliminar Item del Carrito
```http
POST /api/sales/carts/{id}/remove_item/{item_id}/
```

#### Vaciar Carrito
```http
POST /api/sales/carts/{id}/clear/
```

#### Checkout (Crear Pedido)
```http
POST /api/sales/carts/{id}/checkout/
Content-Type: application/json

{
  "customer_id": 1,
  "shipping_address_id": 1,
  "payment_method": "CREDIT_CARD",
  "payment_provider": "MOCK",
  "notes": "Entregar en horario de oficina"
}
```

**Respuesta:**
```json
{
  "id": 1,
  "order_number": "ORD-2025110500001",
  "customer": {...},
  "status": "CREATED",
  "payment_status": "PENDING",
  "items": [...],
  "subtotal": 199.98,
  "total": 226.08,
  "shipping_address": {...},
  "payment": {
    "id": 1,
    "provider": "MOCK",
    "status": "INIT",
    "amount": 226.08
  },
  "created_at": "2025-11-05T10:00:00Z"
}
```

**Proceso del Checkout:**
1. Crea el pedido con estado `CREATED`
2. Convierte items del carrito en items del pedido
3. Reserva stock en inventario
4. Calcula totales (subtotal + IVA 13%)
5. Crea registro de pago
6. Vacía el carrito

---

### Pedidos

#### Listar Pedidos
```http
GET /api/sales/orders/
```

**Query Parameters:**
- `customer` - ID del cliente
- `status` - Estado del pedido (CREATED, PAID, SHIPPED, DELIVERED, CANCELLED)
- `search` - Buscar por número de orden
- `page` - Número de página

**Ejemplos:**
```http
GET /api/sales/orders/?status=PAID
GET /api/sales/orders/?customer=1
GET /api/sales/orders/?search=ORD-2025
```

**Estados del Pedido:**
- `CREATED` - Pedido creado, pago pendiente
- `PAID` - Pago confirmado
- `PROCESSING` - En proceso de preparación
- `SHIPPED` - Enviado
- `DELIVERED` - Entregado
- `CANCELLED` - Cancelado

**Respuesta:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "order_number": "ORD-2025110500001",
      "customer": {
        "id": 1,
        "full_name": "Juan Pérez"
      },
      "status": "PAID",
      "payment_status": "PAID",
      "currency": "BOB",
      "subtotal": 199.98,
      "discount_total": 0.00,
      "shipping_total": 0.00,
      "total": 226.08,
      "items": [
        {
          "id": 1,
          "variant": {
            "id": 1,
            "code": "CAM-001-R-M"
          },
          "qty": 2,
          "unit_price": 99.99,
          "discount": 0.00,
          "subtotal": 199.98
        }
      ],
      "payment": {
        "id": 1,
        "provider": "MOCK",
        "status": "SUCCESS",
        "amount": 226.08,
        "paid_at": "2025-11-05T10:15:00Z"
      },
      "created_at": "2025-11-05T10:00:00Z",
      "updated_at": "2025-11-05T10:15:00Z"
    }
  ]
}
```

#### Detalle del Pedido
```http
GET /api/sales/orders/{id}/
```

#### Confirmar Pago ⚡ (Con Idempotencia)
```http
POST /api/sales/orders/{id}/confirm_payment/
Content-Type: application/json

{
  "idempotency_key": "uuid-v4-here",
  "provider": "STRIPE",
  "provider_ref": "ch_1234567890"
}
```

**Características:**
- ✅ **Bloqueo pesimista** con `select_for_update()`
- ✅ **Idempotencia** - Múltiples llamadas con la misma key no duplican la confirmación
- ✅ **Validación de estado** - Solo permite confirmar pedidos en estado `CREATED`
- ✅ **Bloqueo de inventario** - Bloquea todos los inventarios involucrados
- ✅ **Validación de stock** - Verifica stock suficiente antes de confirmar
- ✅ **Actualización atómica** - Descuenta `stock_on_hand` y `stock_reserved`

**Respuesta:**
```json
{
  "message": "Pago confirmado exitosamente",
  "order": {
    "id": 1,
    "status": "PAID",
    "payment_status": "PAID",
    "payment": {
      "status": "SUCCESS",
      "paid_at": "2025-11-05T10:15:00Z",
      "idempotency_key": "uuid-v4-here"
    }
  }
}
```

**Errores posibles:**
```json
{
  "error": "Estado inválido para confirmar pago. Estado actual: PAID"
}
```

```json
{
  "error": "Stock insuficiente para CAM-001-R-M. Disponible: 5, Reservado: 2"
}
```

#### Cancelar Pedido
```http
POST /api/sales/orders/{id}/cancel/
```

**Características:**
- ✅ **Bloqueo pesimista** para evitar cancelaciones concurrentes
- ✅ **Validación de estado** - No permite cancelar pedidos `SHIPPED` o `DELIVERED`
- ✅ **Liberación de stock** - Devuelve el stock reservado al inventario
- ✅ **Cancelación de pago** - Marca el pago como cancelado

**Respuesta:**
```json
{
  "message": "Pedido cancelado exitosamente",
  "order": {
    "id": 1,
    "status": "CANCELLED",
    "payment": {
      "status": "CANCELLED"
    }
  }
}
```

---

## 🔐 Módulo: SECURITY

Gestión de usuarios, roles y permisos (RBAC).

### Usuarios

#### Listar Usuarios
```http
GET /api/auth/users/
```

#### Detalle de Usuario
```http
GET /api/auth/users/{id}/
```

#### Crear Usuario
```http
POST /api/auth/users/
Content-Type: application/json

{
  "username": "nuevo_usuario",
  "email": "usuario@example.com",
  "password": "password123",
  "full_name": "Nuevo Usuario",
  "role": 1
}
```

#### Cambiar Contraseña
```http
POST /api/auth/users/{id}/change_password/
Content-Type: application/json

{
  "old_password": "password123",
  "new_password": "newpassword456"
}
```

---

### Roles

#### Listar Roles
```http
GET /api/auth/roles/
```

**Respuesta:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Administrador",
      "description": "Acceso completo al sistema",
      "is_active": true,
      "permissions": [
        {
          "id": 1,
          "resource": "Productos",
          "can_view": true,
          "can_create": true,
          "can_update": true,
          "can_delete": true
        }
      ]
    }
  ]
}
```

#### Crear Rol
```http
POST /api/auth/roles/
Content-Type: application/json

{
  "name": "Vendedor",
  "description": "Gestión de ventas",
  "is_active": true
}
```

---

### Recursos

#### Listar Recursos
```http
GET /api/auth/resources/
```

**Respuesta:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "Productos",
      "description": "Gestión de productos",
      "path": "/api/catalog/products/",
      "icon": "box",
      "subresources": [
        {
          "id": 1,
          "name": "Listar Productos",
          "path": "/api/catalog/products/",
          "http_method": "GET"
        }
      ]
    }
  ]
}
```

---

### Permisos (RoleResource)

#### Listar Permisos
```http
GET /api/auth/permissions/
```

#### Asignar Permiso
```http
POST /api/auth/permissions/
Content-Type: application/json

{
  "role": 2,
  "resource": 1,
  "can_view": true,
  "can_create": true,
  "can_update": false,
  "can_delete": false
}
```

---

## 📈 Módulo: ANALYTICS

Reportes y forecasting de ventas.

### Hechos de Ventas (SaleFact)

#### Listar Hechos de Ventas
```http
GET /api/analytics/sales/
```

**Query Parameters:**
- `date_from` - Fecha desde (YYYY-MM-DD)
- `date_to` - Fecha hasta (YYYY-MM-DD)
- `product` - ID del producto
- `category` - ID de categoría

**Respuesta:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "date": "2025-11-05",
      "order": 1,
      "product": 1,
      "product_name": "Camisa Casual",
      "variant": 1,
      "category": 2,
      "category_name": "Ropa de Hombre",
      "qty": 2,
      "unit_price": 99.99,
      "revenue": 199.98,
      "discount": 0.00
    }
  ]
}
```

**Nota:** Los registros en `SaleFact` se crean automáticamente mediante un **signal** cuando un pedido cambia a estado `PAID`.

#### Dashboard de Ventas
```http
GET /api/analytics/sales/dashboard/
```

**Query Parameters:**
- `days` - Número de días a analizar (default: 30)

**Respuesta:**
```json
{
  "period": "últimos 30 días",
  "date_from": "2025-10-06",
  "date_to": "2025-11-05",
  "metrics": {
    "total_revenue": 15847.50,
    "total_orders": 42,
    "avg_order_value": 377.32,
    "total_items_sold": 156
  },
  "daily_sales": [
    {
      "date": "2025-11-05",
      "revenue": 452.16,
      "orders": 2,
      "items": 5
    },
    {
      "date": "2025-11-04",
      "revenue": 1203.84,
      "orders": 5,
      "items": 18
    }
  ],
  "top_products": [
    {
      "product_id": 1,
      "product_name": "Camisa Casual",
      "total_revenue": 2499.75,
      "total_qty": 25,
      "order_count": 12
    }
  ],
  "top_categories": [
    {
      "category_id": 2,
      "category_name": "Ropa de Hombre",
      "total_revenue": 8934.50,
      "total_qty": 89
    }
  ]
}
```

#### Generar Reporte
```http
POST /api/analytics/sales/generate_report/
Content-Type: application/json

{
  "date_from": "2025-11-01",
  "date_to": "2025-11-05",
  "category": 2,
  "product": null,
  "format": "json"
}
```

**Formatos disponibles:** `json`, `csv`, `pdf`, `excel`

**Respuesta (JSON):**
```json
{
  "report_type": "sales_report",
  "period": {
    "from": "2025-11-01",
    "to": "2025-11-05"
  },
  "filters": {
    "category": 2,
    "product": null
  },
  "summary": {
    "total_revenue": 5432.16,
    "total_orders": 18,
    "total_items": 67,
    "avg_order_value": 301.79
  },
  "details": [
    {
      "date": "2025-11-05",
      "product_name": "Camisa Casual",
      "qty": 5,
      "revenue": 499.95
    }
  ]
}
```

---

### Forecasting

#### Listar Modelos de Forecast
```http
GET /api/analytics/forecasts/
```

#### Crear Modelo de Forecast
```http
POST /api/analytics/forecasts/
Content-Type: application/json

{
  "name": "Forecast Diciembre 2025",
  "model_type": "LINEAR_REGRESSION",
  "parameters": {}
}
```

#### Predecir Ventas
```http
POST /api/analytics/forecasts/{id}/predict/
Content-Type: application/json

{
  "product_id": 1,
  "periods": 30,
  "model_type": "LINEAR_REGRESSION"
}
```

**Respuesta:**
```json
{
  "product_id": 1,
  "product_name": "Camisa Casual",
  "model_type": "LINEAR_REGRESSION",
  "periods": 30,
  "historical_data": {
    "avg_daily_sales": 2.5,
    "days_with_sales": 28,
    "total_qty": 70
  },
  "forecast": [
    {
      "date": "2025-11-06",
      "predicted_qty": 2.8,
      "confidence": "medium"
    },
    {
      "date": "2025-11-07",
      "predicted_qty": 2.3,
      "confidence": "medium"
    }
  ]
}
```

**Nota:** Actualmente el forecasting está **simulado** con variación aleatoria. Está listo para integrar modelos ML reales (sklearn, statsmodels, etc.).

---

### Reportes

#### Listar Reportes
```http
GET /api/analytics/reports/
```

#### Crear Reporte
```http
POST /api/analytics/reports/
Content-Type: application/json

{
  "name": "Reporte Mensual Noviembre",
  "report_type": "SALES",
  "parameters": {
    "date_from": "2025-11-01",
    "date_to": "2025-11-30",
    "category": null
  },
  "format": "pdf"
}
```

---

## 🔧 Sistema

### Healthcheck

#### Verificar Estado del Sistema
```http
GET /api/healthz/
```

**Respuesta (Healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00Z",
  "checks": {
    "database": {
      "status": "ok",
      "message": "Database connection successful"
    },
    "models": {
      "status": "ok",
      "message": "34 models loaded"
    },
    "tables": {
      "status": "ok",
      "message": "Critical tables accessible"
    }
  }
}
```

**Respuesta (Unhealthy):**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-11-05T10:30:00Z",
  "checks": {
    "database": {
      "status": "error",
      "message": "Database error: Connection refused"
    }
  }
}
```

**Status Codes:**
- `200 OK` - Sistema saludable
- `503 Service Unavailable` - Sistema con problemas

---

## 📄 Swagger/OpenAPI

### Schema OpenAPI
```http
GET /api/schema/
```

Retorna el esquema completo OpenAPI 3.0 en JSON.

### Swagger UI (Interfaz Interactiva)
```http
GET /api/docs/
```

Abre la interfaz interactiva de Swagger para probar todos los endpoints.

### ReDoc (Documentación Alternativa)
```http
GET /api/redoc/
```

Documentación estática alternativa más legible.

---

## 🚀 Características Avanzadas

### Paginación

Todos los endpoints de listado soportan paginación:

**Query Parameters:**
- `page` - Número de página (default: 1)
- `page_size` - Elementos por página (default: 10, max: 100)

**Respuesta:**
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/catalog/products/?page=2",
  "previous": null,
  "results": [...]
}
```

---

### Búsqueda y Filtrado

Muchos endpoints soportan búsqueda y filtrado:

```http
GET /api/catalog/products/?search=camisa&category=1&min_price=50
GET /api/sales/orders/?customer=1&status=PAID
GET /api/inventory/inventory/?warehouse=1&low_stock=true
```

---

### Ordenamiento

Usa el parámetro `ordering`:

```http
GET /api/catalog/products/?ordering=-created_at
GET /api/sales/orders/?ordering=total
```

Prefijo `-` para orden descendente.

---

### Concurrencia y Seguridad

#### Bloqueo Pesimista
Los endpoints críticos usan `select_for_update()`:
- `POST /api/sales/orders/{id}/confirm_payment/`
- `POST /api/sales/orders/{id}/cancel/`
- `POST /api/inventory/inventory/{id}/adjust_stock/`

#### Idempotencia
El endpoint de confirmación de pago acepta `idempotency_key` para evitar procesamiento duplicado.

#### Validación de Estados
Máquina de estados estricta en pedidos:
- Solo `CREATED` → `PAID`
- No permite cancelar `SHIPPED` o `DELIVERED`

---

## 💾 Base de Datos

**Motor:** PostgreSQL 15+  
**Schema:** `si2-ecommmerce`  
**Tablas:** 34 tablas en total

**Principales tablas:**
- `catalog_*` - 7 tablas (categorías, productos, variantes, etc.)
- `inventory_*` - 2 tablas (almacenes, inventario)
- `sales_*` - 6 tablas (clientes, carritos, pedidos, pagos)
- `security_*` - 4 tablas (usuarios, roles, recursos, permisos)
- `analytics_*` - 3 tablas (hechos de ventas, forecasts, reportes)

---

## 🔄 Flujo Completo de Compra

### 1. Cliente agrega productos al carrito
```http
POST /api/sales/carts/1/add_item/
{"variant_id": 5, "quantity": 2}
```

### 2. Cliente revisa su carrito
```http
GET /api/sales/carts/1/
```

### 3. Cliente hace checkout
```http
POST /api/sales/carts/1/checkout/
{
  "customer_id": 1,
  "shipping_address_id": 1,
  "payment_method": "CREDIT_CARD"
}
```

**Resultado:** Pedido creado con estado `CREATED`, stock reservado en inventario.

### 4. Sistema confirma el pago
```http
POST /api/sales/orders/1/confirm_payment/
{
  "idempotency_key": "unique-key-123",
  "provider": "STRIPE",
  "provider_ref": "ch_1234567890"
}
```

**Resultado:** 
- Pedido cambia a `PAID`
- Stock decrementado en inventario
- Registro creado automáticamente en `SaleFact` (via signal)

### 5. Analytics automático
```http
GET /api/analytics/sales/dashboard/
```

Muestra la venta recién confirmada en métricas y reportes.

---

## 📊 Códigos de Estado HTTP

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado exitosamente
- `204 No Content` - Eliminación exitosa
- `400 Bad Request` - Error en los datos enviados
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permisos
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor
- `503 Service Unavailable` - Servicio no disponible

---

## 🛠️ Configuración de Desarrollo

### Variables de Entorno (.env)

```env
# Database
DB_NAME=vpayDB
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=dbvpay.cfiek6gqkqd5.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_SCHEMA=si2-ecommmerce

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Iniciar Servidor

```bash
# Activar entorno virtual
.\venv\Scripts\activate

# Ejecutar migraciones (si hay cambios)
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

### Crear Superusuario

```bash
python manage.py createsuperuser --username admin --email admin@ecommerce.com
```

---

## 📝 Notas para Desarrollo Frontend/Móvil

### CORS
El backend acepta peticiones de:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://127.0.0.1:8000` (mismo origen)

### Autenticación
Actualmente configurado con `AllowAny` para desarrollo.  
**Para producción:** Se implementará JWT con tokens Bearer.

### Formatos de Fecha
Todas las fechas están en formato ISO 8601:
- `2025-11-05T10:30:00Z` (con hora)
- `2025-11-05` (solo fecha)

### Moneda
Todos los precios están en **BOB (Bolivianos)**.  
IVA: **13%**

---

## 🎯 Próximos Pasos (Opcional)

1. **JWT Authentication** - Para Angular/Flutter
2. **Datos de Demo** - Fixtures con productos/clientes/órdenes
3. **ML Real en Forecasting** - Integrar sklearn/statsmodels
4. **WebSockets** - Notificaciones en tiempo real
5. **Rate Limiting** - Throttling en producción
6. **Cache** - Redis para mejorar performance

---

## 📞 Soporte

- **Swagger UI:** http://127.0.0.1:8000/api/docs/
- **Healthcheck:** http://127.0.0.1:8000/api/healthz/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

**Última actualización:** Noviembre 5, 2025  
**Versión del Backend:** 1.0  
**Django:** 5.2.7  
**DRF:** 3.16.1  
**Python:** 3.12.9
