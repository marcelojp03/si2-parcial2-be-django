# 🎯 FLUJO SIMPLIFICADO DE CHECKOUT

## ✅ FLUJO CORRECTO (AUTO-CONFIRMACIÓN)

```
┌─────────────────────────────────────────────────────┐
│ 1. Cliente llena formulario                        │
│    - Dirección                                      │
│    - Método de pago (CASH/CARD/QR/TRANSFER)        │
│    - Notas                                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 2. POST /api/sales/carts/{id}/checkout/            │
│                                                     │
│    ✅ Crea Order                                    │
│    ✅ Crea Payment                                  │
│    ✅ Reserva stock                                 │
│    ✅ Simula pago (provider=MOCK)                   │
│    ✅ AUTO-CONFIRMA pago                            │
│    ✅ Confirma venta (decrementa stock)             │
│    ✅ Vacía carrito                                 │
│                                                     │
│    TODO EN UNA SOLA OPERACIÓN ATÓMICA              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 3. Frontend recibe respuesta                       │
│                                                     │
│    {                                                │
│      "order_number": "ORD-20251112-001",            │
│      "status": "CONFIRMED",                         │
│      "payment_status": "PAID",                      │
│      "payment": {                                   │
│        "status": "SUCCESS",                         │
│        "paid_at": "2025-11-12T14:30:00Z"            │
│      }                                              │
│    }                                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 4. Frontend muestra confirmación                   │
│                                                     │
│    ✅ Toast/Notificación de éxito                   │
│    ✅ Número de pedido                              │
│    ✅ (Opcional) Enviar email de confirmación       │
│    ✅ Redirige a "Mis Pedidos" o página de gracias  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 UN SOLO ENDPOINT, TODO RESUELTO

### Request:
```http
POST /api/sales/carts/5/checkout/
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 5,
  "shipping_address": {
    "line1": "Av. Principal 123",
    "city": "Santa Cruz",
    "state": "Santa Cruz",
    "zip": "0000"
  },
  "payment_method": "CASH",
  "payment_provider": "MOCK",
  "notes": "Tocar el timbre"
}
```

### Response (201 Created):
```json
{
  "id": 123,
  "order_number": "ORD-20251112-001",
  "customer": 5,
  "customer_name": "Marcelo Jimenez Bonilla",
  "shipping_address": 2,
  "status": "CONFIRMED",          ← ✅ YA CONFIRMADO
  "payment_status": "PAID",        ← ✅ YA PAGADO
  "currency": "BOB",
  "subtotal": "297.35",
  "discount_total": "0.00",
  "shipping_total": "0.00",
  "total": "336.01",
  "items": [
    {
      "id": 1,
      "product_name": "Ladies Colorblock Wind Jacket",
      "qty": 1,
      "unit_price": "45.90",
      "subtotal": "45.90"
    }
    // ... más items
  ],
  "payment": {
    "id": 1,
    "method": "CASH",
    "provider": "MOCK",
    "amount": "336.01",
    "status": "SUCCESS",           ← ✅ PAGO EXITOSO
    "paid_at": "2025-11-12T14:30:00Z",
    "created_at": "2025-11-12T14:30:00Z"
  },
  "total_items": 6,
  "created_at": "2025-11-12T14:30:00Z",
  "updated_at": "2025-11-12T14:30:00Z"
}
```

---

## 🎨 Frontend: Implementación Simplificada

### Angular Component

```typescript
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html'
})
export class CheckoutComponent {
  isProcessing = false;
  
  constructor(
    private http: HttpClient,
    private router: Router,
    private toastr: ToastrService
  ) {}
  
  async onCheckout() {
    if (this.isProcessing) return;
    this.isProcessing = true;
    
    const checkoutData = {
      customer_id: this.authService.getCurrentUser().customer_id,
      shipping_address: {
        line1: this.addressForm.value.street,
        city: this.addressForm.value.city,
        state: this.addressForm.value.state,
        zip: this.addressForm.value.postalCode
      },
      payment_method: this.checkoutForm.value.paymentMethod,
      payment_provider: 'MOCK',
      notes: this.checkoutForm.value.notes
    };
    
    try {
      const order = await this.http.post<Order>(
        `/api/sales/carts/${this.cartId}/checkout/`,
        checkoutData
      ).toPromise();
      
      // ✅ El pedido YA está confirmado y pagado
      
      // Mostrar toast de éxito
      this.toastr.success(
        `Pedido ${order.order_number} confirmado exitosamente`,
        '¡Compra exitosa!',
        { duration: 5000 }
      );
      
      // (Opcional) Enviar email de confirmación
      // await this.sendConfirmationEmail(order);
      
      // Limpiar carrito local
      this.cartService.clearCart();
      
      // Redirigir a página de éxito o mis pedidos
      this.router.navigate(['/order-success', order.id]);
      
    } catch (error) {
      this.toastr.error(
        error.error?.error || 'Error al procesar el pedido',
        'Error en checkout'
      );
    } finally {
      this.isProcessing = false;
    }
  }
}
```

### Template (No necesita pantalla de confirmación adicional)

```html
<div class="checkout-container">
  <h2>Finalizar Compra</h2>
  
  <!-- Formulario de dirección y pago -->
  <form [formGroup]="checkoutForm">
    <!-- ... campos del formulario ... -->
    
    <button (click)="onCheckout()" 
            [disabled]="!checkoutForm.valid || isProcessing"
            class="btn-primary btn-block">
      <span *ngIf="!isProcessing">Confirmar Pedido</span>
      <span *ngIf="isProcessing">
        <i class="spinner"></i> Procesando...
      </span>
    </button>
  </form>
</div>
```

### Página de Éxito (order-success.component.html)

```html
<div class="success-container">
  <div class="success-icon">✓</div>
  <h1>¡Pedido Confirmado!</h1>
  
  <div class="order-details">
    <p>Número de pedido: <strong>{{ order.order_number }}</strong></p>
    <p>Total pagado: <strong>Bs. {{ order.total }}</strong></p>
    <p>Estado: <span class="badge-success">{{ order.status }}</span></p>
  </div>
  
  <div class="next-steps">
    <h3>¿Qué sigue?</h3>
    <ul>
      <li>✅ Recibirás un correo de confirmación</li>
      <li>📦 Tu pedido será procesado en las próximas 24 horas</li>
      <li>🚚 Te notificaremos cuando sea enviado</li>
    </ul>
  </div>
  
  <div class="actions">
    <button (click)="router.navigate(['/orders'])" class="btn-primary">
      Ver Mis Pedidos
    </button>
    <button (click)="router.navigate(['/'])" class="btn-secondary">
      Seguir Comprando
    </button>
  </div>
</div>
```

---

## 📧 Email de Confirmación (Opcional)

Puedes implementar un servicio de email para enviar la confirmación:

```python
# En sales/signals.py o services/email.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
    """Envía email de confirmación de pedido"""
    customer_email = order.customer.user.email
    customer_name = order.customer.user.get_full_name()
    
    # Renderizar template HTML
    html_message = render_to_string('emails/order_confirmation.html', {
        'customer_name': customer_name,
        'order_number': order.order_number,
        'order': order,
        'total': order.total,
        'items': order.items.all()
    })
    
    send_mail(
        subject=f'Confirmación de Pedido - {order.order_number}',
        message=f'Gracias por tu compra. Número de pedido: {order.order_number}',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        fail_silently=False
    )
```

Luego en `views.py`, después de auto-confirmar:

```python
# Al final del bloque if payment_provider == 'MOCK':
from .services import send_order_confirmation_email

try:
    send_order_confirmation_email(order)
except Exception as e:
    logger.warning(f"Error enviando email de confirmación: {e}")
    # No falla el checkout si el email falla
```

---

## 🔄 Para Pasarelas Reales (Futuro)

Si en el futuro implementas **pasarelas de pago reales** (Stripe, PayPal, etc.):

```python
# En checkout()
if payment_provider == 'MOCK':
    # Auto-confirmar (código actual)
    payment.status = 'SUCCESS'
    # ...
elif payment_provider == 'STRIPE':
    # Redirigir a Stripe Checkout
    stripe_session = create_stripe_checkout_session(order)
    return Response({
        'redirect_url': stripe_session.url,
        'order_id': order.id
    })
elif payment_provider == 'PAYPAL':
    # Redirigir a PayPal
    paypal_url = create_paypal_payment(order)
    return Response({
        'redirect_url': paypal_url,
        'order_id': order.id
    })
```

En ese caso:
1. Frontend redirige a la pasarela
2. Usuario paga en la pasarela
3. Pasarela redirige de vuelta con webhook
4. Webhook llama a `confirm_payment()`

---

## ✅ Ventajas de Auto-Confirmación

1. ✅ **UX mejorada** - Un solo paso, no dos pantallas
2. ✅ **Menos errores** - No puede quedar pendiente por olvido
3. ✅ **Código más simple** - No necesitas endpoint separado para MOCK
4. ✅ **Transacción atómica** - Todo o nada
5. ✅ **Realista** - Simula exactamente una pasarela real que auto-confirma
6. ✅ **Flexible** - Fácil agregar pasarelas reales después

---

## 🎯 Resumen

### ❌ ANTES (Incorrecto):
```
Checkout → PENDING → Pantalla manual → Confirmar → SUCCESS
```

### ✅ AHORA (Correcto):
```
Checkout → AUTO-CONFIRMA → SUCCESS → Toast + Email
```

---

## 📝 Checklist Frontend

- [ ] Formulario de checkout con dirección y pago
- [ ] Llamada a `/checkout/` con `payment_provider: 'MOCK'`
- [ ] Mostrar spinner mientras procesa
- [ ] Verificar respuesta: `order.status === 'CONFIRMED'`
- [ ] Mostrar toast de éxito con número de pedido
- [ ] Limpiar carrito del estado local
- [ ] Redirigir a página de éxito o "Mis Pedidos"
- [ ] (Opcional) Página de éxito con detalles del pedido
- [ ] NO crear pantalla de confirmación manual

---

## 🚫 YA NO NECESITAS

- ❌ Endpoint separado `confirm_payment()` para MOCK
- ❌ Pantalla de "Confirmar Pago" después del checkout
- ❌ Botón manual de confirmación
- ❌ Lógica de idempotencia para MOCK
- ❌ Segundo request HTTP después del checkout

El endpoint `confirm_payment()` **solo** se usará para webhooks de pasarelas reales en el futuro.
