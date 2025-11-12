# Guía de Endpoints de Shopping

## Flujo Completo de Compra

```
1. Productos → 2. Carrito → 3. Checkout → 4. Pago → 5. Orden
```

---

## 📦 1. PRODUCTOS (Catálogo)

### Listar Productos
**URL:** `GET /api/catalog/products/`  
**Autenticación:** No requerida  
**Descripción:** Lista todos los productos activos con paginación.

**Query Parameters:**
- `search`: Buscar por nombre, descripción o SKU
- `category`: Filtrar por slug de categoría
- `min_price`: Precio mínimo
- `max_price`: Precio máximo
- `ordering`: Ordenar por campo (`name`, `-created_at`)

**Respuesta:**
```json
{
  "count": 81,
  "next": "http://127.0.0.1:8000/api/catalog/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Google Pixel 6",
      "sku": "GP-001",
      "description": "Smartphone con cámara avanzada",
      "categories": ["Electronics", "Phones"],
      "images": [
        {
          "id": 1,
          "image_url": "https://...",
          "is_primary": true
        }
      ],
      "variants": [
        {
          "id": 1,
          "code": "GP-001-128GB-BLACK",
          "price": "599.00",
          "stock_available": 15,
          "attributes": {
            "Storage": "128GB",
            "Color": "Black"
          }
        }
      ]
    }
  ]
}
```

### Detalle de Producto
**URL:** `GET /api/catalog/products/{id}/`  
**Autenticación:** No requerida

**Respuesta:**
```json
{
  "id": 1,
  "name": "Google Pixel 6",
  "sku": "GP-001",
  "description": "Descripción detallada...",
  "status": "ACTIVE",
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics"
    }
  ],
  "images": [...],
  "variants": [
    {
      "id": 1,
      "code": "GP-001-128GB-BLACK",
      "price": "599.00",
      "compare_price": "699.00",
      "stock_available": 15,
      "attributes": {
        "Storage": "128GB",
        "Color": "Black"
      }
    }
  ]
}
```

---

## 🛒 2. CARRITO

### Obtener Carrito
**URL:** `GET /api/sales/carts/{cart_id}/`  
**Autenticación:** No requerida  
**Descripción:** Obtiene el carrito con todos sus items.

**Respuesta:**
```json
{
  "id": 1,
  "customer": {
    "id": 4,
    "first_name": "Trevor",
    "last_name": "Calero"
  },
  "items": [
    {
      "id": 1,
      "variant": {
        "id": 1,
        "code": "GP-001-128GB-BLACK",
        "product_name": "Google Pixel 6",
        "price": "599.00",
        "attributes": {
          "Storage": "128GB",
          "Color": "Black"
        }
      },
      "quantity": 2,
      "price": "599.00",
      "subtotal": "1198.00"
    }
  ],
  "total_items": 2,
  "subtotal": "1198.00",
  "created_at": "2025-11-11T10:30:00Z",
  "updated_at": "2025-11-11T14:45:00Z"
}
```

### Agregar Item al Carrito
**URL:** `POST /api/sales/carts/{cart_id}/add_item/`  
**Autenticación:** No requerida  
**Descripción:** Agrega un producto (variante) al carrito. Si ya existe, incrementa la cantidad.

**Body:**
```json
{
  "variant_id": 1,
  "quantity": 2
}
```

**Respuesta:** Carrito completo actualizado (igual que GET)

### Eliminar Item del Carrito
**URL:** `POST /api/sales/carts/{cart_id}/remove-item/{item_id}/`  
**Autenticación:** No requerida  
**Descripción:** Elimina un item específico del carrito.

**Respuesta:** Carrito completo actualizado

### Vaciar Carrito
**URL:** `POST /api/sales/carts/{cart_id}/clear/`  
**Autenticación:** No requerida  
**Descripción:** Elimina todos los items del carrito.

**Respuesta:** Carrito vacío

---

## 💳 3. CHECKOUT (Crear Orden)

### Crear Orden desde Carrito
**URL:** `POST /api/sales/carts/{cart_id}/checkout/`  
**Autenticación:** No requerida (pero requiere customer_id)  
**Descripción:** Convierte el carrito en una orden, reserva stock y vacía el carrito.

**Body:**
```json
{
  "customer_id": 4,
  "shipping_address_id": 1,
  "payment_method": "CREDIT_CARD",
  "payment_provider": "STRIPE",
  "notes": "Entregar en horario de oficina"
}
```

**Campos:**
- `customer_id` (requerido): ID del cliente
- `shipping_address_id` (requerido): ID de la dirección de envío
- `payment_method` (requerido): `CREDIT_CARD`, `DEBIT_CARD`, `CASH`, `BANK_TRANSFER`, `QR`
- `payment_provider` (opcional): `STRIPE`, `PAYPAL`, `MOCK` (default: `MOCK`)
- `notes` (opcional): Notas adicionales del pedido

**Respuesta:**
```json
{
  "id": 10,
  "order_number": "ORD-20251111-0010",
  "customer": {
    "id": 4,
    "first_name": "Trevor",
    "last_name": "Calero",
    "email": "trevorfelixcalerosuyo@gmail.com"
  },
  "items": [
    {
      "id": 1,
      "variant": {
        "code": "GP-001-128GB-BLACK",
        "product_name": "Google Pixel 6",
        "price": "599.00"
      },
      "quantity": 2,
      "price": "599.00",
      "subtotal": "1198.00"
    }
  ],
  "shipping_address": {
    "id": 1,
    "street": "Av. Banzer #1234",
    "city": "Santa Cruz",
    "state": "Santa Cruz",
    "country": "Bolivia",
    "postal_code": "0000"
  },
  "subtotal": "1198.00",
  "tax": "155.74",
  "shipping_cost": "0.00",
  "discount": "0.00",
  "total": "1353.74",
  "status": "CREATED",
  "payment_status": "PENDING",
  "payment": {
    "id": 1,
    "method": "CREDIT_CARD",
    "provider": "STRIPE",
    "status": "PENDING",
    "amount": "1353.74"
  },
  "notes": "Entregar en horario de oficina",
  "created_at": "2025-11-11T15:30:00Z"
}
```

**Estados de Orden:**
- `CREATED`: Orden creada, stock reservado
- `PAID`: Pago confirmado
- `PROCESSING`: En proceso de preparación
- `SHIPPED`: Enviado
- `DELIVERED`: Entregado
- `CANCELLED`: Cancelado

**Estados de Pago:**
- `PENDING`: Pendiente de pago
- `PAID`: Pagado
- `FAILED`: Pago fallido
- `REFUNDED`: Reembolsado

---

## 💰 4. PAGO

### Confirmar Pago de Orden
**URL:** `POST /api/sales/orders/{order_id}/confirm_payment/`  
**Autenticación:** No requerida (pero requiere autorización del payment provider)  
**Descripción:** Confirma el pago de una orden, actualiza stock y cambia estados. **Incluye idempotencia** para evitar cargos duplicados.

**Body:**
```json
{
  "idempotency_key": "unique-transaction-id-12345",
  "provider": "STRIPE",
  "provider_ref": "ch_3NKhJ2KvE7F8..."
}
```

**Campos:**
- `idempotency_key` (recomendado): Clave única para evitar procesamiento duplicado
- `provider` (opcional): Proveedor de pago (`STRIPE`, `PAYPAL`, `MOCK`)
- `provider_ref` (opcional): Referencia del proveedor (transaction ID)

**Respuesta:**
```json
{
  "message": "Pago confirmado exitosamente",
  "order": {
    "id": 10,
    "order_number": "ORD-20251111-0010",
    "status": "PAID",
    "payment_status": "PAID",
    "payment": {
      "id": 1,
      "status": "SUCCESS",
      "paid_at": "2025-11-11T15:35:00Z",
      "provider_ref": "ch_3NKhJ2KvE7F8..."
    },
    "total": "1353.74"
  }
}
```

**Errores:**
```json
{
  "error": "Estado inválido para confirmar pago. Estado actual: PAID"
}
```

```json
{
  "error": "Stock insuficiente para GP-001-128GB-BLACK. Disponible: 5, Reservado: 0"
}
```

**Idempotencia:**
Si se envía el mismo `idempotency_key` dos veces, la segunda llamada retornará:
```json
{
  "message": "Pago ya confirmado previamente",
  "order": { ... }
}
```

---

## 📋 5. ÓRDENES

### Listar Órdenes
**URL:** `GET /api/sales/orders/`  
**Autenticación:** No requerida

**Query Parameters:**
- `customer`: Filtrar por customer_id
- `status`: Filtrar por estado (`CREATED`, `PAID`, `PROCESSING`, etc.)
- `search`: Buscar por order_number o nombre de cliente

**Ejemplo:**
```
GET /api/sales/orders/?customer=4
GET /api/sales/orders/?status=PAID
GET /api/sales/orders/?search=ORD-2025
```

**Respuesta:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 10,
      "order_number": "ORD-20251111-0010",
      "customer": {...},
      "status": "PAID",
      "payment_status": "PAID",
      "total": "1353.74",
      "created_at": "2025-11-11T15:30:00Z"
    }
  ]
}
```

### Detalle de Orden
**URL:** `GET /api/sales/orders/{order_id}/`  
**Autenticación:** No requerida

**Respuesta:** Orden completa con items, dirección y pago

### Cancelar Orden
**URL:** `POST /api/sales/orders/{order_id}/cancel/`  
**Autenticación:** No requerida  
**Descripción:** Cancela una orden y libera el stock reservado. Solo permite cancelar órdenes que no estén enviadas o entregadas.

**Respuesta:**
```json
{
  "message": "Pedido cancelado exitosamente",
  "order": {
    "id": 10,
    "order_number": "ORD-20251111-0010",
    "status": "CANCELLED",
    "payment": {
      "status": "CANCELLED"
    }
  }
}
```

**Errores:**
```json
{
  "error": "No se puede cancelar un pedido enviado o entregado"
}
```

```json
{
  "error": "El pedido ya fue cancelado"
}
```

---

## 📍 DIRECCIONES

### Listar Direcciones del Cliente
**URL:** `GET /api/sales/addresses/?customer={customer_id}`  
**Autenticación:** No requerida

**Respuesta:**
```json
[
  {
    "id": 1,
    "customer": 4,
    "street": "Av. Banzer #1234",
    "city": "Santa Cruz",
    "state": "Santa Cruz",
    "country": "Bolivia",
    "postal_code": "0000",
    "is_default": true
  }
]
```

### Crear Dirección
**URL:** `POST /api/sales/addresses/`  
**Autenticación:** No requerida

**Body:**
```json
{
  "customer": 4,
  "street": "Calle Libertad #567",
  "city": "Santa Cruz",
  "state": "Santa Cruz",
  "country": "Bolivia",
  "postal_code": "0000",
  "is_default": false
}
```

---

## 🔄 Flujo Completo de Compra (Ejemplo)

### 1. El usuario navega y agrega productos al carrito

```javascript
// 1. Ver producto
const product = await fetch('http://127.0.0.1:8000/api/catalog/products/1/')
  .then(r => r.json());

// 2. Agregar al carrito
const cart = await fetch('http://127.0.0.1:8000/api/sales/carts/1/add_item/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    variant_id: product.variants[0].id,
    quantity: 2
  })
}).then(r => r.json());
```

### 2. El usuario hace checkout

```javascript
// 3. Crear orden desde carrito
const order = await fetch('http://127.0.0.1:8000/api/sales/carts/1/checkout/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer_id: 4,
    shipping_address_id: 1,
    payment_method: 'CREDIT_CARD',
    payment_provider: 'STRIPE',
    notes: 'Entregar en horario de oficina'
  })
}).then(r => r.json());

console.log('Orden creada:', order.order_number);
console.log('Total a pagar:', order.total);
console.log('Payment ID:', order.payment.id);
```

### 3. El usuario paga (integración con Stripe/PayPal)

```javascript
// 4. Procesar pago con Stripe (ejemplo simplificado)
const stripe = Stripe('pk_test_...');
const paymentIntent = await stripe.createPaymentIntent({
  amount: order.total * 100, // en centavos
  currency: 'usd'
});

// Cuando el pago es exitoso en Stripe:
const confirmation = await fetch(`http://127.0.0.1:8000/api/sales/orders/${order.id}/confirm_payment/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    idempotency_key: paymentIntent.id,
    provider: 'STRIPE',
    provider_ref: paymentIntent.id
  })
}).then(r => r.json());

console.log('Pago confirmado:', confirmation.message);
console.log('Orden actualizada:', confirmation.order.status); // "PAID"
```

### 4. Ver historial de órdenes

```javascript
// 5. Ver órdenes del cliente
const orders = await fetch(`http://127.0.0.1:8000/api/sales/orders/?customer=4`, {
  headers: { 'Authorization': `Bearer ${accessToken}` }
}).then(r => r.json());

console.log('Mis órdenes:', orders.results);
```

---

## 🔐 Autenticación

La mayoría de endpoints de **sales** no requieren autenticación, pero en producción deberías:

1. Proteger endpoints con JWT:
   - Checkout
   - Confirmar pago
   - Ver órdenes

2. Validar que el customer_id pertenece al usuario autenticado

3. Implementar rate limiting para evitar abuso

---

## ⚠️ Notas Importantes

1. **Stock Management:**
   - Al hacer checkout, el stock se **reserva** (no se decrementa)
   - Al confirmar pago, el stock se **decrementa** y se quita de reservado
   - Al cancelar, el stock se **libera** de reservado

2. **Idempotencia en Pagos:**
   - Siempre envía `idempotency_key` para evitar cargos duplicados
   - El sistema detecta peticiones duplicadas y retorna el resultado previo

3. **Estados de Orden:**
   - `CREATED`: Stock reservado, esperando pago
   - `PAID`: Pago confirmado, stock deducido
   - `CANCELLED`: Stock liberado, no se puede revertir

4. **Cálculo de Precios:**
   - `subtotal`: Suma de (precio × cantidad) de todos los items
   - `tax`: 13% del subtotal (IVA Bolivia)
   - `total`: subtotal + tax + shipping_cost - discount

5. **Carrito:**
   - El carrito se vacía automáticamente después del checkout
   - No hay límite de items en el carrito
   - Los precios en CartItem se guardan al agregar (no cambian si el producto se actualiza)

---

## 📊 Resumen de Endpoints

| Acción | Método | Endpoint | Auth |
|--------|--------|----------|------|
| **Productos** |
| Listar productos | GET | `/api/catalog/products/` | No |
| Detalle producto | GET | `/api/catalog/products/{id}/` | No |
| **Carrito** |
| Ver carrito | GET | `/api/sales/carts/{id}/` | No |
| Agregar item | POST | `/api/sales/carts/{id}/add_item/` | No |
| Eliminar item | POST | `/api/sales/carts/{id}/remove-item/{item_id}/` | No |
| Vaciar carrito | POST | `/api/sales/carts/{id}/clear/` | No |
| **Checkout** |
| Crear orden | POST | `/api/sales/carts/{id}/checkout/` | No* |
| **Órdenes** |
| Listar órdenes | GET | `/api/sales/orders/` | No* |
| Detalle orden | GET | `/api/sales/orders/{id}/` | No* |
| Confirmar pago | POST | `/api/sales/orders/{id}/confirm_payment/` | No* |
| Cancelar orden | POST | `/api/sales/orders/{id}/cancel/` | No* |
| **Direcciones** |
| Listar direcciones | GET | `/api/sales/addresses/?customer={id}` | No* |
| Crear dirección | POST | `/api/sales/addresses/` | No* |

*Recomendado agregar autenticación JWT en producción
