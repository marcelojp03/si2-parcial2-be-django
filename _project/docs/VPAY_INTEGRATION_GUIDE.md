# 🚀 VPAY INTEGRATION - FLUJO COMPLETO

## 📋 Resumen

VPAY es una pasarela de pagos QR de Bolivia que requiere:
1. **Generar QR** → API de VPAY
2. **Mostrar QR** → Frontend
3. **Polling** → Consultar estado cada 3-5 segundos
4. **Auto-confirmar** → Cuando status = "PAG"

---

## 🔄 Flujo Completo

```
┌─────────────────────────────────────────────────────┐
│ 1. Cliente selecciona "Pagar con VPAY"             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 2. POST /api/sales/carts/{id}/checkout/            │
│                                                     │
│    Request:                                         │
│    {                                                │
│      "customer_id": 1,                              │
│      "shipping_address_id": 2,                      │
│      "payment_method": "QR",                        │
│      "payment_provider": "VPAY",                    │
│      "notes": "Pago con QR VPAY"                    │
│    }                                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 3. Backend llama a VPAY API                        │
│                                                     │
│    PUT https://vpay.com.bo:7778/pro/api/           │
│        transactions/doPayment                       │
│                                                     │
│    ✅ Genera QR                                     │
│    ✅ Obtiene qr_id: "50526979"                     │
│    ✅ Obtiene qr_image: "data:image/png;base64..." │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 4. Backend guarda y responde                       │
│                                                     │
│    - Crea Order (status: CREATED)                  │
│    - Crea Payment (status: PENDING)                │
│    - Payment.provider_ref = qr_id                  │
│    - Reserva stock                                 │
│    - NO auto-confirma (espera pago)                │
│                                                     │
│    Response:                                        │
│    {                                                │
│      "id": 123,                                     │
│      "order_number": "ORD-20251112-001",            │
│      "status": "CREATED",                           │
│      "payment_status": "PENDING",                   │
│      "vpay_qr": {                                   │
│        "qr_id": "50526979",                         │
│        "qr_image": "iVBORw0KGgoAAAANS...",          │
│        "expiration_date": "2025-11-13"              │
│      }                                              │
│    }                                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 5. Frontend muestra QR                             │
│                                                     │
│    - Decodifica base64 y muestra imagen QR         │
│    - Inicia polling cada 3 segundos                │
│    - Muestra mensaje: "Escanea el QR para pagar"   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 6. Polling: Frontend consulta estado               │
│                                                     │
│    GET /api/sales/orders/123/check-vpay-payment/   │
│                                                     │
│    Cada 3-5 segundos hasta que status = PAID       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 7. Backend verifica estado en VPAY                 │
│                                                     │
│    POST https://vpay.com.bo:7778/pro/api/          │
│         operations/statusQr                         │
│                                                     │
│    Body: {"operation": "50526979"}                 │
│                                                     │
│    Response:                                        │
│    {                                                │
│      "responseList": [{                             │
│        "response": [{                               │
│          "code": "statusQr",                        │
│          "identificator": "PEN"  ← o "PAG"          │
│        }]                                           │
│      }]                                             │
│    }                                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 8a. Si status = "PEN" (Pendiente)                  │
│                                                     │
│    Response:                                        │
│    {                                                │
│      "payment_status": "PENDING",                   │
│      "vpay_status": "PEN",                          │
│      "message": "Esperando confirmación de pago"    │
│    }                                                │
│                                                     │
│    → Frontend sigue haciendo polling               │
└─────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 8b. Si status = "PAG" (Pagado) ✅                  │
│                                                     │
│    Backend AUTO-CONFIRMA:                           │
│    - payment.status = 'SUCCESS'                     │
│    - order.status = 'CONFIRMED'                     │
│    - order.payment_status = 'PAID'                  │
│    - inventory.confirm_sale(qty)                    │
│    - Envía email de confirmación                    │
│                                                     │
│    Response:                                        │
│    {                                                │
│      "payment_status": "PAID",                      │
│      "order_status": "CONFIRMED",                   │
│      "paid_at": "2025-11-12T14:30:00Z",             │
│      "message": "¡Pago confirmado exitosamente!"    │
│    }                                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 9. Frontend muestra éxito                          │
│                                                     │
│    ✅ Detiene polling                               │
│    ✅ Toast: "¡Pago confirmado!"                    │
│    ✅ Redirige a página de éxito                    │
└─────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend: Implementación Angular

### 1. Checkout Component

```typescript
import { Component, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html'
})
export class CheckoutComponent implements OnDestroy {
  isProcessing = false;
  showQR = false;
  qrImage: string | null = null;
  orderId: number | null = null;
  pollingSubscription: Subscription | null = null;
  
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
      shipping_address_id: this.selectedAddressId,
      payment_method: 'QR',
      payment_provider: 'VPAY',
      notes: this.notes
    };
    
    try {
      const response = await this.http.post<any>(
        `/api/sales/carts/${this.cartId}/checkout/`,
        checkoutData
      ).toPromise();
      
      // Verificar si es VPAY
      if (response.vpay_qr) {
        // Mostrar QR al usuario
        this.orderId = response.id;
        this.qrImage = `data:image/png;base64,${response.vpay_qr.qr_image}`;
        this.showQR = true;
        
        // Iniciar polling del estado
        this.startPaymentPolling();
        
        this.toastr.info('Escanea el código QR para completar el pago', 'Pago pendiente');
      } else {
        // Otros métodos de pago (auto-confirmados)
        this.handlePaymentSuccess(response);
      }
      
    } catch (error) {
      this.toastr.error(error.error?.error || 'Error al procesar el pedido');
      this.isProcessing = false;
    }
  }
  
  startPaymentPolling() {
    // Consultar estado cada 3 segundos
    this.pollingSubscription = interval(3000).pipe(
      switchMap(() => 
        this.http.get(`/api/sales/orders/${this.orderId}/check-vpay-payment/`)
      )
    ).subscribe({
      next: (response: any) => {
        if (response.payment_status === 'PAID') {
          // ¡Pago confirmado!
          this.stopPolling();
          this.handlePaymentSuccess(response);
        }
        // Si aún está PENDING, sigue haciendo polling
      },
      error: (error) => {
        console.error('Error verificando pago:', error);
        // Continuar polling incluso si hay error
      }
    });
  }
  
  stopPolling() {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
      this.pollingSubscription = null;
    }
  }
  
  handlePaymentSuccess(response: any) {
    this.isProcessing = false;
    this.showQR = false;
    
    this.toastr.success(
      `Pedido ${response.order_number} confirmado`,
      '¡Pago exitoso!',
      { duration: 5000 }
    );
    
    this.cartService.clearCart();
    this.router.navigate(['/order-success', response.id]);
  }
  
  ngOnDestroy() {
    this.stopPolling();
  }
}
```

### 2. Template HTML

```html
<!-- checkout.component.html -->

<div class="checkout-container">
  <!-- Formulario normal de checkout -->
  <form [formGroup]="checkoutForm" *ngIf="!showQR">
    <!-- ... campos ... -->
    
    <button (click)="onCheckout()" 
            [disabled]="!checkoutForm.valid || isProcessing">
      <span *ngIf="!isProcessing">Pagar con VPAY</span>
      <span *ngIf="isProcessing">
        <i class="spinner"></i> Procesando...
      </span>
    </button>
  </form>
  
  <!-- Modal de QR VPAY -->
  <div class="qr-modal" *ngIf="showQR">
    <div class="qr-container">
      <h2>Escanea el código QR para pagar</h2>
      
      <div class="qr-image">
        <img [src]="qrImage" alt="QR Code VPAY">
      </div>
      
      <div class="instructions">
        <p>1. Abre tu app de banco (Banco Unión, BNB, etc.)</p>
        <p>2. Selecciona "Pagar con QR"</p>
        <p>3. Escanea este código</p>
        <p>4. Confirma el pago</p>
      </div>
      
      <div class="waiting">
        <div class="spinner"></div>
        <p>Esperando confirmación del pago...</p>
      </div>
      
      <button (click)="cancelPayment()" class="btn-cancel">
        Cancelar
      </button>
    </div>
  </div>
</div>
```

### 3. CSS

```css
.qr-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.qr-container {
  background: white;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
  max-width: 400px;
}

.qr-image {
  margin: 20px 0;
  padding: 20px;
  background: white;
  border: 2px solid #4CAF50;
  border-radius: 10px;
}

.qr-image img {
  width: 250px;
  height: 250px;
}

.instructions {
  margin: 20px 0;
  text-align: left;
  background: #f0f0f0;
  padding: 15px;
  border-radius: 5px;
}

.instructions p {
  margin: 5px 0;
  font-size: 14px;
}

.waiting {
  margin: 20px 0;
  color: #666;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## 🔧 Configuración Backend

### Settings.py (Agregar credenciales VPAY)

```python
# VPAY Configuration
VPAY_USER = config('VPAY_USER', default='selvi.lecaro')
VPAY_COMPANY = config('VPAY_COMPANY', default='82')
VPAY_BANK = config('VPAY_BANK', default='BMSC')
VPAY_ACCOUNT = config('VPAY_ACCOUNT', default='selvi.lecaro')
```

### .env (Producción)

```env
VPAY_USER=selvi.lecaro
VPAY_COMPANY=82
VPAY_BANK=BMSC
VPAY_ACCOUNT=selvi.lecaro
```

---

## 📡 Endpoints Disponibles

### 1. Checkout con VPAY

```http
POST /api/sales/carts/{cart_id}/checkout/

{
  "customer_id": 1,
  "shipping_address_id": 2,
  "payment_method": "QR",
  "payment_provider": "VPAY",
  "notes": "Pago QR"
}
```

**Response (201 Created):**
```json
{
  "id": 123,
  "order_number": "ORD-20251112-001",
  "status": "CREATED",
  "payment_status": "PENDING",
  "total": "336.01",
  "vpay_qr": {
    "qr_id": "50526979",
    "qr_image": "iVBORw0KGgoAAAANSUhEUgAA...",
    "expiration_date": "2025-11-13"
  }
}
```

---

### 2. Verificar Estado de Pago (Polling)

```http
GET /api/sales/orders/{order_id}/check-vpay-payment/
```

**Response mientras está pendiente:**
```json
{
  "payment_status": "PENDING",
  "order_status": "CREATED",
  "vpay_status": "PEN",
  "message": "Esperando confirmación de pago"
}
```

**Response cuando se confirma:**
```json
{
  "payment_status": "PAID",
  "order_status": "CONFIRMED",
  "paid_at": "2025-11-12T14:30:00Z",
  "message": "¡Pago confirmado exitosamente!"
}
```

---

## ✅ Ventajas de este Flujo

1. ✅ **No requiere webhook** - Polling es más simple
2. ✅ **Auto-confirmación** - Backend detecta status=PAG
3. ✅ **Email automático** - Se envía al confirmar
4. ✅ **UX fluida** - Usuario ve el QR y espera
5. ✅ **Atómico** - Todo en transacción

---

## 🧪 Testing

### Probar generación de QR:

```python
python manage.py shell

from apps.core.services.vpay_service import VPayService

result = VPayService.generate_qr_payment(
    amount=100.50,
    gloss="Pedido TEST",
    order_number="TEST-001",
    expiration_hours=24
)

print(result)
# {'success': True, 'qr_id': '50526979', 'qr_image': 'iVBORw0...', ...}
```

### Probar verificación de estado:

```python
result = VPayService.check_qr_status('50526979')
print(result)
# {'success': True, 'status': 'PEN', 'is_paid': False}
```

---

## 🎯 Resumen del Flujo

| Paso | Acción | Responsable | API |
|------|--------|-------------|-----|
| 1 | Generar QR | Backend | PUT /transactions/doPayment |
| 2 | Mostrar QR | Frontend | - |
| 3 | Polling (cada 3s) | Frontend | GET /check-vpay-payment/ |
| 4 | Verificar status | Backend | POST /operations/statusQr |
| 5 | Auto-confirmar si PAG | Backend | - |
| 6 | Mostrar éxito | Frontend | - |

¡Listo! 🚀
