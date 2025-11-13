# 💳 LÓGICA DE AUTO-CONFIRMACIÓN DE PAGOS

## 🎯 Regla de Auto-Confirmación

El sistema **auto-confirma** el pago cuando es un **método simulado** o que **no requiere pasarela externa**.

```python
should_auto_confirm = payment_provider in ['MOCK', 'QR'] or payment_method in ['CASH', 'TRANSFER']
```

---

## ✅ MÉTODOS QUE AUTO-CONFIRMAN (Inmediato)

### 1. **CASH (Efectivo)**
```json
{
  "payment_method": "CASH",
  "payment_provider": "MOCK"
}
```
- ✅ **Auto-confirma**: Sí
- **Razón**: Pago en efectivo contra entrega, no requiere pasarela
- **Estado final**: `CONFIRMED` / `PAID`

---

### 2. **TRANSFER (Transferencia Bancaria)**
```json
{
  "payment_method": "TRANSFER",
  "payment_provider": "MOCK"
}
```
- ✅ **Auto-confirma**: Sí
- **Razón**: Transferencia directa, no requiere pasarela
- **Estado final**: `CONFIRMED` / `PAID`
- **Nota**: En producción real, podrías validar el comprobante manualmente antes de confirmar

---

### 3. **QR (Código QR)**
```json
{
  "payment_method": "QR",
  "payment_provider": "QR"
}
```
- ✅ **Auto-confirma**: Sí
- **Razón**: Simulación de QR Bolivia, Tigo Money, etc.
- **Estado final**: `CONFIRMED` / `PAID`

---

### 4. **CARD con MOCK (Tarjeta simulada)**
```json
{
  "payment_method": "CARD",
  "payment_provider": "MOCK"
}
```
- ✅ **Auto-confirma**: Sí
- **Razón**: Simulación de pago con tarjeta
- **Estado final**: `CONFIRMED` / `PAID`

---

## ⏳ MÉTODOS QUE QUEDAN PENDIENTES (Requieren webhook)

### 5. **CARD con STRIPE (Tarjeta real)**
```json
{
  "payment_method": "CARD",
  "payment_provider": "STRIPE"
}
```
- ❌ **Auto-confirma**: NO
- **Razón**: Requiere redirección a Stripe y webhook de confirmación
- **Estado inicial**: `CREATED` / `PENDING`
- **Flujo**:
  1. Frontend redirige a Stripe Checkout
  2. Usuario paga en Stripe
  3. Stripe envía webhook
  4. Backend llama a `confirm_payment()`
  5. Estado final: `CONFIRMED` / `PAID`

---

### 6. **CARD con PAYPAL (Tarjeta real vía PayPal)**
```json
{
  "payment_method": "CARD",
  "payment_provider": "PAYPAL"
}
```
- ❌ **Auto-confirma**: NO
- **Razón**: Requiere redirección a PayPal y webhook de confirmación
- **Estado inicial**: `CREATED` / `PENDING`
- **Flujo**: Similar a Stripe

---

## 📊 Tabla Resumen

| Método | Provider | Auto-Confirma | Estado Final | Requiere Webhook |
|--------|----------|---------------|--------------|------------------|
| CASH | MOCK | ✅ Sí | CONFIRMED/PAID | ❌ No |
| TRANSFER | MOCK | ✅ Sí | CONFIRMED/PAID | ❌ No |
| QR | QR | ✅ Sí | CONFIRMED/PAID | ❌ No |
| CARD | MOCK | ✅ Sí | CONFIRMED/PAID | ❌ No |
| CARD | STRIPE | ❌ No | CREATED/PENDING | ✅ Sí |
| CARD | PAYPAL | ❌ No | CREATED/PENDING | ✅ Sí |

---

## 🔄 Flujo de Auto-Confirmación

```python
# En sales/views.py - checkout()

# Determinar si debe auto-confirmar
should_auto_confirm = (
    payment_provider in ['MOCK', 'QR'] or 
    payment_method in ['CASH', 'TRANSFER']
)

if should_auto_confirm:
    # Simular pago exitoso
    payment.status = 'SUCCESS'
    payment.paid_at = timezone.now()
    payment.save()
    
    # Confirmar pedido
    order.status = 'CONFIRMED'
    order.payment_status = 'PAID'
    order.save()
    
    # Confirmar venta (decrementar stock)
    for item in order.items.all():
        inventory.confirm_sale(item.qty)
```

---

## 🎨 Frontend: Manejo de Respuesta

```typescript
async onCheckout() {
  const checkoutData = {
    customer_id: this.customerId,
    shipping_address: { /* ... */ },
    payment_method: this.selectedMethod, // 'CASH', 'CARD', 'QR', 'TRANSFER'
    payment_provider: this.selectedProvider, // 'MOCK', 'STRIPE', 'QR', 'PAYPAL'
    notes: this.notes
  };
  
  const order = await this.http.post('/api/sales/carts/5/checkout/', checkoutData).toPromise();
  
  // Verificar estado del pedido
  if (order.status === 'CONFIRMED') {
    // ✅ Auto-confirmado - Mostrar éxito
    this.toastr.success('¡Pedido confirmado!');
    this.router.navigate(['/order-success', order.id]);
    
  } else if (order.status === 'CREATED' && order.payment_status === 'PENDING') {
    // ⏳ Requiere pago externo - Redirigir a pasarela
    if (order.payment_redirect_url) {
      window.location.href = order.payment_redirect_url; // Stripe/PayPal
    }
  }
}
```

---

## 🛠️ Configuración Recomendada por Entorno

### **Desarrollo / Testing:**
```json
{
  "payment_method": "CASH",
  "payment_provider": "MOCK"
}
```
✅ Siempre auto-confirma, sin complicaciones

---

### **Producción (Bolivia):**

#### Opción 1: Efectivo contra entrega
```json
{
  "payment_method": "CASH",
  "payment_provider": "MOCK"
}
```
✅ Auto-confirma, verificación manual al entregar

#### Opción 2: QR Bolivia
```json
{
  "payment_method": "QR",
  "payment_provider": "QR"
}
```
✅ Auto-confirma (simula escaneo de QR)

En producción real con QR Bolivia:
- Mostrarías código QR al cliente
- Cliente escanea y paga
- API de QR Bolivia envía webhook
- Backend confirma con `confirm_payment()`

#### Opción 3: Transferencia bancaria
```json
{
  "payment_method": "TRANSFER",
  "payment_provider": "MOCK"
}
```
✅ Auto-confirma, cliente sube comprobante después

---

### **Producción Internacional:**

#### Stripe
```json
{
  "payment_method": "CARD",
  "payment_provider": "STRIPE"
}
```
❌ NO auto-confirma, requiere:
1. Redirigir a Stripe Checkout
2. Webhook de confirmación
3. Llamar a `confirm_payment()`

#### PayPal
```json
{
  "payment_method": "CARD",
  "payment_provider": "PAYPAL"
}
```
❌ NO auto-confirma, requiere webhook

---

## 🔧 Personalización

Si necesitas **cambiar la lógica** de auto-confirmación:

```python
# En sales/views.py

# Opción 1: Auto-confirmar TODO (para demos)
should_auto_confirm = True

# Opción 2: Auto-confirmar solo efectivo y QR
should_auto_confirm = payment_method in ['CASH', 'QR']

# Opción 3: Auto-confirmar todo excepto STRIPE
should_auto_confirm = payment_provider != 'STRIPE'

# Opción 4: Personalizado por método Y provider
should_auto_confirm = (
    (payment_method == 'CASH') or
    (payment_method == 'QR' and payment_provider == 'QR') or
    (payment_method == 'CARD' and payment_provider == 'MOCK')
)
```

---

## 📧 Email de Confirmación

Solo enviar email cuando el pago está confirmado:

```python
if should_auto_confirm:
    # ... código de confirmación ...
    
    # Enviar email de confirmación
    try:
        send_order_confirmation_email(order)
    except Exception as e:
        logger.warning(f"Error enviando email: {e}")
```

---

## ✅ Ventajas de esta Lógica

1. ✅ **Flexible**: Fácil agregar nuevos providers
2. ✅ **Realista**: Simula flujos de pago reales
3. ✅ **Escalable**: Soporta pasarelas externas cuando sea necesario
4. ✅ **Simple para demos**: MOCK auto-confirma siempre
5. ✅ **Completo**: Soporta cash, QR, transferencias, tarjetas

---

## 🎯 Resumen

### Para tu proyecto actual (demo):
```json
{
  "payment_method": "CASH",      // o "CARD", "QR", "TRANSFER"
  "payment_provider": "MOCK"     // Siempre auto-confirma
}
```

### Para producción futura:
```json
{
  "payment_method": "CARD",
  "payment_provider": "STRIPE"   // Requiere webhook
}
```

¡Elige según tu caso de uso! 🚀
