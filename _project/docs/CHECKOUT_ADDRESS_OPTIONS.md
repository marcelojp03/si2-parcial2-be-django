# 🛒 CHECKOUT: Crear Dirección sobre la marcha

## ✅ OPCIÓN 1: Usar dirección existente

Si el cliente ya tiene direcciones guardadas:

```http
POST /api/sales/carts/{cart_id}/checkout/
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 5,
  "shipping_address_id": 2,
  "payment_method": "CASH",
  "payment_provider": "MOCK",
  "notes": "Tocar el timbre"
}
```

---

## ✅ OPCIÓN 2: Crear dirección nueva (Cliente sin direcciones)

Si el cliente NO tiene direcciones o quiere usar una nueva:

```http
POST /api/sales/carts/{cart_id}/checkout/
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": 5,
  "shipping_address": {
    "line1": "Av. Principal 123",
    "city": "Santa Cruz",
    "state": "Santa Cruz",
    "zip": "0000",
    "notes": "Edificio azul, 3er piso",
    "is_default": false
  },
  "payment_method": "CASH",
  "payment_provider": "MOCK",
  "notes": "Tocar el timbre, entregar en portería"
}
```

### Campos de `shipping_address`:
- ✅ `line1` (string, **requerido**) - Dirección/Calle
- ✅ `city` (string, **requerido**) - Ciudad
- ⚪ `state` (string, opcional) - Departamento
- ⚪ `zip` (string, opcional) - Código Postal
- ⚪ `notes` (string, opcional) - Referencia
- ⚪ `is_default` (boolean, opcional) - Marcar como predeterminada (default: false)

---

## 🔄 Flujo Completo del Frontend

### Caso 1: Cliente con direcciones existentes

```typescript
// 1. Obtener direcciones del cliente
const addresses = await this.http.get<Address[]>('/api/sales/addresses/?customer=5').toPromise();

if (addresses.length > 0) {
  // Mostrar selector de direcciones
  this.showAddressSelector = true;
  
  // Checkout con dirección seleccionada
  await this.checkout({
    customer_id: this.customerId,
    shipping_address_id: this.selectedAddressId,
    payment_method: 'CASH',
    payment_provider: 'MOCK',
    notes: this.checkoutForm.value.notes
  });
}
```

### Caso 2: Cliente SIN direcciones (Formulario vacío)

```typescript
// 1. Mostrar formulario de dirección
this.showAddressForm = true;

// 2. Checkout creando la dirección
await this.checkout({
  customer_id: this.customerId,
  shipping_address: {
    line1: this.addressForm.value.street,
    city: this.addressForm.value.city,
    state: this.addressForm.value.state,
    zip: this.addressForm.value.postalCode,
    notes: this.addressForm.value.reference,
    is_default: this.addressForm.value.saveAddress
  },
  payment_method: this.checkoutForm.value.paymentMethod,
  payment_provider: 'MOCK',
  notes: this.checkoutForm.value.notes
});
```

---

## 📝 Ejemplo Angular Component

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

interface Address {
  id: number;
  line1: string;
  city: string;
  state: string;
  zip: string;
}

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html'
})
export class CheckoutComponent implements OnInit {
  checkoutForm: FormGroup;
  addressForm: FormGroup;
  
  existingAddresses: Address[] = [];
  useExistingAddress = false;
  selectedAddressId: number | null = null;
  
  constructor(private fb: FormBuilder, private http: HttpClient) {}
  
  async ngOnInit() {
    // Crear formularios
    this.checkoutForm = this.fb.group({
      paymentMethod: ['CASH', Validators.required],
      notes: ['']
    });
    
    this.addressForm = this.fb.group({
      street: ['', Validators.required],
      city: ['', Validators.required],
      state: [''],
      postalCode: [''],
      reference: [''],
      saveAddress: [false]
    });
    
    // Cargar direcciones existentes
    await this.loadAddresses();
  }
  
  async loadAddresses() {
    const customerId = this.authService.getCurrentUser().customer_id;
    
    this.existingAddresses = await this.http.get<Address[]>(
      `/api/sales/addresses/?customer=${customerId}`
    ).toPromise();
    
    // Si tiene direcciones, mostrar selector
    this.useExistingAddress = this.existingAddresses.length > 0;
    
    if (this.useExistingAddress) {
      // Seleccionar la primera por defecto
      this.selectedAddressId = this.existingAddresses[0].id;
    }
  }
  
  async onCheckout() {
    if (!this.checkoutForm.valid) return;
    
    const customerId = this.authService.getCurrentUser().customer_id;
    const cartId = this.cartService.getCartId();
    
    let checkoutData: any = {
      customer_id: customerId,
      payment_method: this.checkoutForm.value.paymentMethod,
      payment_provider: 'MOCK',
      notes: this.checkoutForm.value.notes
    };
    
    if (this.useExistingAddress && this.selectedAddressId) {
      // OPCIÓN 1: Usar dirección existente
      checkoutData.shipping_address_id = this.selectedAddressId;
    } else {
      // OPCIÓN 2: Crear nueva dirección
      if (!this.addressForm.valid) {
        alert('Complete los datos de dirección');
        return;
      }
      
      checkoutData.shipping_address = {
        line1: this.addressForm.value.street,
        city: this.addressForm.value.city,
        state: this.addressForm.value.state || '',
        zip: this.addressForm.value.postalCode || '',
        notes: this.addressForm.value.reference || '',
        is_default: this.addressForm.value.saveAddress
      };
    }
    
    try {
      const order = await this.http.post(
        `/api/sales/carts/${cartId}/checkout/`,
        checkoutData
      ).toPromise();
      
      // Redirigir a confirmación
      this.router.navigate(['/checkout/confirm', order.id]);
    } catch (error) {
      console.error('Error en checkout:', error);
      alert('Error al procesar el pedido');
    }
  }
  
  toggleAddressMode() {
    this.useExistingAddress = !this.useExistingAddress;
  }
}
```

---

## 📄 Template HTML

```html
<div class="checkout-container">
  <h2>Checkout</h2>
  
  <!-- DIRECCIÓN DE ENVÍO -->
  <div class="section">
    <h3>Dirección de Envío</h3>
    
    <!-- Botón para agregar nueva dirección -->
    <button *ngIf="existingAddresses.length > 0" 
            (click)="toggleAddressMode()" 
            class="btn-link">
      {{ useExistingAddress ? '+ Agregar nueva dirección' : 'Usar dirección guardada' }}
    </button>
    
    <!-- OPCIÓN 1: Selector de direcciones existentes -->
    <div *ngIf="useExistingAddress && existingAddresses.length > 0">
      <div *ngFor="let address of existingAddresses" class="address-card">
        <input type="radio" 
               [value]="address.id" 
               [(ngModel)]="selectedAddressId"
               name="address">
        <label>
          <strong>{{ address.line1 }}</strong><br>
          {{ address.city }}, {{ address.state }} {{ address.zip }}
        </label>
      </div>
    </div>
    
    <!-- OPCIÓN 2: Formulario para nueva dirección -->
    <form *ngIf="!useExistingAddress" [formGroup]="addressForm">
      <div class="form-group">
        <label>Calle *</label>
        <input type="text" 
               formControlName="street" 
               placeholder="Av. Principal 123"
               class="form-control">
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Ciudad *</label>
          <input type="text" 
                 formControlName="city" 
                 placeholder="Santa Cruz"
                 class="form-control">
        </div>
        
        <div class="form-group">
          <label>Departamento</label>
          <input type="text" 
                 formControlName="state" 
                 placeholder="Santa Cruz"
                 class="form-control">
        </div>
      </div>
      
      <div class="form-group">
        <label>Código Postal</label>
        <input type="text" 
               formControlName="postalCode" 
               placeholder="0000"
               class="form-control">
      </div>
      
      <div class="form-group">
        <label>Referencia</label>
        <input type="text" 
               formControlName="reference" 
               placeholder="Edificio azul, 3er piso"
               class="form-control">
      </div>
      
      <div class="form-group">
        <label>
          <input type="checkbox" formControlName="saveAddress">
          Guardar esta dirección
        </label>
      </div>
    </form>
  </div>
  
  <!-- MÉTODO DE PAGO -->
  <div class="section">
    <h3>Método de Pago</h3>
    <form [formGroup]="checkoutForm">
      <div class="payment-methods">
        <label>
          <input type="radio" value="CASH" formControlName="paymentMethod">
          Efectivo
        </label>
        <label>
          <input type="radio" value="CARD" formControlName="paymentMethod">
          Tarjeta de Crédito
        </label>
        <label>
          <input type="radio" value="TRANSFER" formControlName="paymentMethod">
          Transferencia Bancaria
        </label>
        <label>
          <input type="radio" value="QR" formControlName="paymentMethod">
          Código QR
        </label>
      </div>
      
      <div class="form-group">
        <label>Notas (Opcional)</label>
        <textarea formControlName="notes" 
                  placeholder="Ej: Tocar el timbre, entregar en portería..."
                  class="form-control"></textarea>
      </div>
    </form>
  </div>
  
  <!-- RESUMEN DEL PEDIDO -->
  <div class="section">
    <h3>Resumen del Pedido</h3>
    <!-- Tu componente de resumen actual -->
  </div>
  
  <!-- BOTÓN CONFIRMAR -->
  <button (click)="onCheckout()" 
          class="btn-primary btn-block"
          [disabled]="!checkoutForm.valid">
    Confirmar Pedido
  </button>
</div>
```

---

## ❌ Validaciones y Errores

### Error: No se proporciona dirección
```json
{
  "non_field_errors": [
    "Debe proporcionar shipping_address_id o shipping_address"
  ]
}
```

### Error: Se proporciona ambas opciones
```json
{
  "non_field_errors": [
    "Proporcione solo shipping_address_id O shipping_address, no ambos"
  ]
}
```

### Error: Faltan campos requeridos en shipping_address
```json
{
  "non_field_errors": [
    "shipping_address requiere los campos: line1, city"
  ]
}
```

### Error: Dirección no existe
```json
{
  "shipping_address_id": [
    "Invalid pk \"999\" - object does not exist."
  ]
}
```

---

## 💡 Recomendaciones

1. **Cargar direcciones al inicio** del componente de checkout
2. **Detectar automáticamente** si el cliente tiene direcciones guardadas
3. **Mostrar formulario vacío** si no tiene direcciones
4. **Permitir toggle** entre usar dirección guardada o crear nueva
5. **Validar campos requeridos** antes de enviar (line1, city)
6. **Checkbox "Guardar dirección"** para futuras compras
7. **Marcar como predeterminada** la primera dirección si no tiene ninguna

---

## ✅ Beneficios

- ✅ Cliente sin direcciones puede hacer checkout inmediatamente
- ✅ Cliente con direcciones puede elegir o crear nueva
- ✅ Dirección se guarda automáticamente para próximas compras
- ✅ Un solo endpoint para ambos casos
- ✅ Transacción atómica (si falla el checkout, no se guarda la dirección)
