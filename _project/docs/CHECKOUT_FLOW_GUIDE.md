# 🛒 GUÍA COMPLETA: FLUJO DE CHECKOUT Y CONFIRMACIÓN

## 📍 ENDPOINTS DISPONIBLES

### **Direcciones**
- `GET /api/sales/addresses/` - Listar direcciones del cliente
- `POST /api/sales/addresses/` - Crear nueva dirección
- `GET /api/sales/addresses/{id}/` - Obtener dirección específica
- `PUT /api/sales/addresses/{id}/` - Actualizar dirección
- `DELETE /api/sales/addresses/{id}/` - Eliminar dirección

### **Carrito**
- `GET /api/sales/carts/{id}/` - Obtener carrito
- `POST /api/sales/carts/{id}/add-item/` - Añadir item
- `POST /api/sales/carts/{id}/remove-item/{item_id}/` - Eliminar item
- `POST /api/sales/carts/{id}/clear/` - Vaciar carrito
- `POST /api/sales/carts/{id}/checkout/` - **CREAR PEDIDO**

### **Órdenes**
- `GET /api/sales/orders/` - Listar órdenes
- `GET /api/sales/orders/{id}/` - Obtener orden específica
- `POST /api/sales/orders/{id}/confirm_payment/` - **CONFIRMAR PAGO**

---

## 🎯 FLUJO COMPLETO (FRONTEND → BACKEND)

### **PASO 1: OBTENER/CREAR DIRECCIÓN DE ENVÍO**

#### 1.1 Listar direcciones del cliente
```http
GET /api/sales/addresses/?customer={customer_id}
Authorization: Bearer {token}
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "customer": 5,
    "customer_name": "Marcelo Jimenez Bonilla",
    "line1": "Av. Principal 123",
    "city": "Santa Cruz",
    "state": "Santa Cruz",
    "zip": "0000",
    "notes": "",
    "is_default": true
  }
]
```

#### 1.2 Crear nueva dirección (si es necesaria)
```http
POST /api/sales/addresses/
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer": 5,
  "line1": "Calle Sucre #456",
  "city": "Santa Cruz",
  "state": "Santa Cruz",
  "zip": "0000",
  "notes": "Tocar el timbre",
  "is_default": false
}
```

**Respuesta:**
```json
{
  "id": 2,
  "customer": 5,
  "customer_name": "Marcelo Jimenez Bonilla",
  "line1": "Calle Sucre #456",
  "city": "Santa Cruz",
  "state": "Santa Cruz",
  "zip": "0000",
  "notes": "Tocar el timbre",
  "is_default": false
}
```

---

### **PASO 2: CHECKOUT (CREAR PEDIDO)**

#### Frontend muestra el formulario con:
- ✅ Dirección de envío (seleccionada o recién creada)
- ✅ Método de pago
- ✅ Notas opcionales
- ✅ Resumen del carrito (items, total)

#### Request:
```http
POST /api/sales/carts/{cart_id}/checkout/
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 5,
  "shipping_address_id": 2,
  "payment_method": "CASH",
  "payment_provider": "MOCK",
  "notes": "Tocar el timbre, entregar en portería"
}
```

**Campos:**
- `customer_id` (int) - ID del cliente autenticado
- `shipping_address_id` (int) - ID de la dirección de envío
- `payment_method` (string) - Opciones: `"CARD"`, `"CASH"`, `"TRANSFER"`, `"QR"`
- `payment_provider` (string, opcional) - Opciones: `"STRIPE"`, `"PAYPAL"`, `"MOCK"`, `"QR"` (default: `"MOCK"`)
- `notes` (string, opcional) - Máximo 500 caracteres

#### Response (201 Created):
```json
{
  "id": 123,
  "order_number": "ORD-20251112-001",
  "customer": 5,
  "customer_name": "Marcelo Jimenez Bonilla",
  "shipping_address": 2,
  "status": "CREATED",
  "payment_status": "PENDING",
  "currency": "BOB",
  "subtotal": "297.35",
  "discount_total": "0.00",
  "shipping_total": "0.00",
  "total": "336.01",
  "items": [
    {
      "id": 1,
      "variant": 3103,
      "variant_code": "ladiescolorblockwindjacket-default",
      "product_name": "Ladies Colorblock Wind Jacket",
      "qty": 1,
      "unit_price": "45.90",
      "discount": "0.00",
      "subtotal": "45.90"
    },
    {
      "id": 2,
      "variant": 3104,
      "variant_code": "ladiesvoyagefleecejacket-default",
      "product_name": "Ladies Voyage Fleece Jacket",
      "qty": 1,
      "unit_price": "48.00",
      "discount": "0.00",
      "subtotal": "48.00"
    }
    // ... más items (total 6)
  ],
  "payment": {
    "id": 1,
    "order": 123,
    "method": "CASH",
    "provider": "MOCK",
    "provider_transaction_id": null,
    "amount": "336.01",
    "status": "PENDING",
    "paid_at": null,
    "created_at": "2025-11-12T14:30:00.000Z"
  },
  "total_items": 6,
  "created_at": "2025-11-12T14:30:00.000Z",
  "updated_at": "2025-11-12T14:30:00.000Z"
}
```

**Lo que hace el backend automáticamente:**
1. ✅ Crea el `Order` con estado `CREATED`
2. ✅ Copia los items del carrito a `OrderItem`
3. ✅ **RESERVA el stock** (stock_reserved += quantity)
4. ✅ Calcula IVA (13%): `tax = subtotal * 0.13`
5. ✅ Calcula total: `total = subtotal + tax + shipping_cost - discount`
6. ✅ Crea `Payment` con estado `PENDING`
7. ✅ **VACÍA el carrito** (cart.items.all().delete())

---

### **PASO 3: MOSTRAR RESUMEN Y CONFIRMAR PAGO**

El frontend muestra:
- ✅ Número de orden: `ORD-20251112-001`
- ✅ Estado: `CREATED` / `PENDING`
- ✅ Items del pedido
- ✅ Total a pagar: Bs. 336.01
- ✅ Método de pago seleccionado
- ✅ Botón "Confirmar Pedido" o "Pagar Ahora"

---

### **PASO 4: CONFIRMAR PAGO**

#### Request:
```http
POST /api/sales/orders/123/confirm_payment/
Authorization: Bearer {token}
Content-Type: application/json

{
  "provider": "MOCK",
  "idempotency_key": "checkout-20251112-143000-abc123"
}
```

**Campos:**
- `provider` (string) - Proveedor de pago: `"MOCK"`, `"STRIPE"`, `"PAYPAL"`, `"QR"`
- `idempotency_key` (string) - Clave única para evitar doble confirmación (ejemplo: timestamp + random)

#### Response (200 OK):
```json
{
  "message": "Pago confirmado exitosamente",
  "order": {
    "id": 123,
    "order_number": "ORD-20251112-001",
    "customer": 5,
    "customer_name": "Marcelo Jimenez Bonilla",
    "shipping_address": 2,
    "status": "CONFIRMED",
    "payment_status": "PAID",
    "currency": "BOB",
    "subtotal": "297.35",
    "discount_total": "0.00",
    "shipping_total": "0.00",
    "total": "336.01",
    "items": [
      // ... mismos items que antes
    ],
    "payment": {
      "id": 1,
      "order": 123,
      "method": "CASH",
      "provider": "MOCK",
      "provider_transaction_id": null,
      "amount": "336.01",
      "status": "SUCCESS",
      "paid_at": "2025-11-12T14:35:00.000Z",
      "created_at": "2025-11-12T14:30:00.000Z"
    },
    "total_items": 6,
    "created_at": "2025-11-12T14:30:00.000Z",
    "updated_at": "2025-11-12T14:35:00.000Z"
  }
}
```

**Lo que hace el backend:**
1. ✅ **Bloqueo pesimista** del pedido (SELECT FOR UPDATE) - evita confirmaciones concurrentes
2. ✅ Valida que `order.status == "CREATED"`
3. ✅ Actualiza `payment.status` → `"SUCCESS"`
4. ✅ Guarda `payment.paid_at` → timestamp actual
5. ✅ **CONFIRMA LA VENTA:** 
   - Decrementa `stock_on_hand` (stock real)
   - Decrementa `stock_reserved` (stock reservado)
6. ✅ Actualiza `order.status` → `"CONFIRMED"`
7. ✅ Actualiza `order.payment_status` → `"PAID"`
8. ✅ **Idempotencia:** Si se llama 2 veces con el mismo `idempotency_key`, retorna el resultado anterior

---

## 🔄 DIAGRAMA DE FLUJO

```
┌─────────────────────────────────────────────────────┐
│ 1. Cliente llena formulario de checkout            │
│    - Dirección de envío                            │
│    - Método de pago                                │
│    - Notas opcionales                              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 2. POST /api/sales/carts/{id}/checkout/            │
│    ✅ Crea Order (CREATED)                          │
│    ✅ Crea Payment (PENDING)                        │
│    ✅ Reserva stock                                 │
│    ✅ Vacía carrito                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 3. Frontend muestra resumen del pedido             │
│    - Order Number: ORD-20251112-001                │
│    - Total: Bs. 336.01                             │
│    - Botón: "Confirmar Pedido"                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 4. POST /api/sales/orders/{id}/confirm_payment/    │
│    ✅ Payment → SUCCESS                             │
│    ✅ Order → CONFIRMED                             │
│    ✅ Confirma venta (decrementa stock)             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 5. Frontend muestra confirmación                   │
│    ✅ "Pedido confirmado exitosamente"              │
│    ✅ Número de orden para seguimiento              │
│    ✅ Redirige a "Mis Pedidos" o página de gracias  │
└─────────────────────────────────────────────────────┘
```

---

## 📊 ESTADOS DEL PEDIDO Y PAGO

### **Order.status:**
- `CREATED` - Pedido creado, stock reservado
- `CONFIRMED` - Pago confirmado, venta finalizada
- `SHIPPED` - Pedido enviado
- `DELIVERED` - Pedido entregado
- `CANCELLED` - Pedido cancelado

### **Payment.status:**
- `PENDING` - Esperando confirmación
- `SUCCESS` - Pago confirmado exitosamente
- `FAILED` - Pago fallido
- `REFUNDED` - Reembolsado

### **Order.payment_status:**
- `PENDING` - Pendiente de pago
- `PAID` - Pagado
- `REFUNDED` - Reembolsado

---

## 🛡️ VALIDACIONES Y MANEJO DE ERRORES

### **Errores comunes en checkout:**

#### Carrito vacío:
```json
{
  "error": "El carrito está vacío"
}
```
**Status:** 400 Bad Request

#### Dirección inválida:
```json
{
  "shipping_address_id": ["Invalid pk \"999\" - object does not exist."]
}
```
**Status:** 400 Bad Request

#### Stock insuficiente (en confirm_payment):
```json
{
  "error": "Stock insuficiente para: Ladies Colorblock Wind Jacket"
}
```
**Status:** 400 Bad Request

#### Estado inválido para confirmar:
```json
{
  "error": "Estado inválido para confirmar pago. Estado actual: CONFIRMED"
}
```
**Status:** 400 Bad Request

### **Idempotencia:**
Si se intenta confirmar 2 veces con el mismo `idempotency_key`:
```json
{
  "message": "Pago ya confirmado previamente",
  "order": { /* datos del pedido */ }
}
```
**Status:** 200 OK

---

## 💡 RECOMENDACIONES PARA EL FRONTEND

### **1. Antes de mostrar el checkout:**
```typescript
// Verificar que el carrito no esté vacío
if (cart.items.length === 0) {
  this.router.navigate(['/cart']);
  return;
}
```

### **2. Generar idempotency_key único:**
```typescript
const idempotencyKey = `checkout-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
// Ejemplo: "checkout-1699800000000-abc123xyz"
```

### **3. Guardar order_id después del checkout:**
```typescript
const checkoutResponse = await this.checkoutService.createOrder(data);
localStorage.setItem('pending_order_id', checkoutResponse.id);
this.router.navigate(['/checkout/confirm', checkoutResponse.id]);
```

### **4. Manejar confirmación de pago:**
```typescript
async confirmPayment(orderId: number) {
  try {
    const response = await this.orderService.confirmPayment(orderId, {
      provider: 'MOCK',
      idempotency_key: this.generateIdempotencyKey()
    });
    
    if (response.message.includes('exitosamente')) {
      // Éxito - mostrar mensaje y redirigir
      this.showSuccess('¡Pedido confirmado!');
      localStorage.removeItem('pending_order_id');
      this.router.navigate(['/orders', response.order.id]);
    }
  } catch (error) {
    // Manejar error
    this.showError(error.message);
  }
}
```

### **5. Botón de confirmación (evitar doble click):**
```typescript
isConfirming = false;

async onConfirmClick() {
  if (this.isConfirming) return; // Ya está procesando
  
  this.isConfirming = true;
  try {
    await this.confirmPayment(this.orderId);
  } finally {
    this.isConfirming = false;
  }
}
```

---

## 📝 ESTRUCTURA DE DATOS COMPLETA

### **Address:**
```typescript
interface Address {
  id: number;
  customer: number;
  customer_name: string;
  line1: string;        // Calle/Dirección
  city: string;         // Ciudad
  state: string;        // Departamento
  zip: string;          // Código Postal
  notes: string;        // Referencia/Notas
  is_default: boolean;
}
```

### **Order:**
```typescript
interface Order {
  id: number;
  order_number: string;
  customer: number;
  customer_name: string;
  shipping_address: number;
  status: 'CREATED' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
  payment_status: 'PENDING' | 'PAID' | 'REFUNDED';
  currency: string;
  subtotal: string;
  discount_total: string;
  shipping_total: string;
  total: string;
  items: OrderItem[];
  payment: Payment;
  total_items: number;
  created_at: string;
  updated_at: string;
}
```

### **OrderItem:**
```typescript
interface OrderItem {
  id: number;
  variant: number;
  variant_code: string;
  product_name: string;
  qty: number;
  unit_price: string;
  discount: string;
  subtotal: string;
}
```

### **Payment:**
```typescript
interface Payment {
  id: number;
  order: number;
  method: 'CARD' | 'CASH' | 'TRANSFER' | 'QR';
  provider: 'STRIPE' | 'PAYPAL' | 'MOCK' | 'QR';
  provider_transaction_id: string | null;
  amount: string;
  status: 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';
  paid_at: string | null;
  created_at: string;
}
```

---

## ✅ CHECKLIST PARA EL FRONTEND

- [ ] Endpoint para listar direcciones del cliente
- [ ] Endpoint para crear nueva dirección
- [ ] Formulario de checkout con todos los campos
- [ ] Validación de carrito no vacío antes de checkout
- [ ] Llamada a `/checkout/` con datos correctos
- [ ] Guardar `order_id` después del checkout
- [ ] Página de confirmación mostrando resumen
- [ ] Botón "Confirmar Pago" con protección de doble click
- [ ] Generación de `idempotency_key` único
- [ ] Llamada a `/confirm_payment/` con idempotency
- [ ] Manejo de errores (stock insuficiente, etc.)
- [ ] Página de éxito con número de orden
- [ ] Redirección a "Mis Pedidos" después de confirmar
- [ ] Limpiar localStorage después de confirmación exitosa

---

## 🎉 RESULTADO FINAL

Después de completar este flujo:
1. ✅ El carrito queda vacío
2. ✅ El pedido está creado y confirmado
3. ✅ El stock está reservado y confirmado
4. ✅ El pago está registrado como exitoso
5. ✅ El cliente puede ver su pedido en "Mis Pedidos"
6. ✅ El sistema tiene registro completo de la transacción
