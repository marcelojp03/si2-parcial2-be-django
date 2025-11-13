# 🚀 VPAY PAYMENT GATEWAY & EMAIL SERVICE

## ✅ Cambios Realizados

### 1. **VPAY como Payment Provider**

VPAY es una pasarela de pagos que soporta:
- 💳 **Tarjetas de crédito/débito**
- 📱 **Pagos por QR**

#### Actualización en `sales/serializers.py`:
```python
payment_provider = serializers.ChoiceField(
    choices=['STRIPE', 'PAYPAL', 'VPAY', 'MOCK', 'QR'],
    required=False,
    default='MOCK'
)
```

---

### 2. **Servicio de Email con Turbo SMTP**

#### Configuración en `ecommerce/settings.py`:
```python
# Email Configuration (Turbo SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'pro.eu.turbo-smtp.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = '1200a91cedc0cac41b08'
EMAIL_HOST_PASSWORD = 'pSPJhX9oMtzmAbBjckie'
DEFAULT_FROM_EMAIL = 'marcelojp03@gmail.com'
```

**Nota:** El dominio del remitente debe estar verificado en Turbo SMTP. Actualmente usa `marcelojp03@gmail.com`.

---

### 3. **Servicio de Email Creado**

Archivo: `apps/core/services/email_service.py`

#### Funciones disponibles:

##### a) `send_order_confirmation_email(order, customer_email=None)`
Envía email de confirmación de pedido con:
- ✅ Número de pedido
- 📦 Listado de productos
- 💰 Totales (subtotal + envío + total)
- 📍 Dirección de envío
- 🎨 Formato HTML profesional
- 📧 Fallback texto plano

##### b) `send_test_email(recipient_email)`
Envía email de prueba simple para verificar configuración.

---

### 4. **Integración con Checkout**

El email se envía automáticamente cuando:
1. El pago se **auto-confirma** (MOCK, QR, CASH, TRANSFER, **VPAY**)
2. Después de confirmar el stock

#### Código en `sales/views.py`:
```python
if should_auto_confirm:
    # ... confirmar pago y pedido ...
    
    # Enviar email de confirmación
    try:
        from apps.core.services.email_service import send_order_confirmation_email
        send_order_confirmation_email(order)
    except Exception as email_error:
        # No fallar el checkout si falla el email
        logger.warning(f"Error enviando email de confirmación: {email_error}")
```

**Importante:** Si falla el envío de email, el checkout **NO falla**. Solo se registra un warning en los logs.

---

## 🎯 Uso de VPAY

### Opción 1: VPAY con Tarjeta
```json
{
  "customer_id": 1,
  "shipping_address_id": 2,
  "payment_method": "CARD",
  "payment_provider": "VPAY",
  "notes": "Entregar por la tarde"
}
```

**Flujo:**
1. Frontend redirige a VPAY Checkout
2. Cliente paga con tarjeta en VPAY
3. VPAY envía webhook a backend
4. Backend llama a `confirm_payment()`
5. Email de confirmación enviado

---

### Opción 2: VPAY con QR
```json
{
  "customer_id": 1,
  "shipping_address_id": 2,
  "payment_method": "QR",
  "payment_provider": "VPAY",
  "notes": "Pago con QR"
}
```

**Flujo:**
1. Frontend muestra código QR de VPAY
2. Cliente escanea y paga
3. VPAY envía webhook (confirmación instantánea)
4. Backend confirma pedido
5. Email de confirmación enviado

---

## 📧 Email de Confirmación

### Contenido del Email:

```
✅ Pedido Confirmado #ORD-20241112-0001

Hola Juan Pérez,

Tu pedido ha sido confirmado exitosamente.

📦 DETALLES DEL PEDIDO
======================
Número de Pedido: ORD-20241112-0001
Fecha: 12/11/2024 14:30
Estado: Confirmado
Estado de Pago: Pagado

📋 PRODUCTOS
============
iPhone 15 Pro (IPH15P-128-BLK) - 1 x Bs. 8500.00 = Bs. 8500.00
AirPods Pro (AIRP-PRO-WHT) - 2 x Bs. 1850.00 = Bs. 3700.00

Subtotal: Bs. 12200.00
Envío: Bs. 0.00
TOTAL: Bs. 12200.00

📍 DIRECCIÓN DE ENVÍO
=====================
Av. Busch #123
Santa Cruz, Santa Cruz
Referencia: Frente al parque

Nos pondremos en contacto contigo pronto para coordinar la entrega.
```

---

## 🧪 Pruebas

### 1. **Probar Email de Prueba**
```python
python manage.py shell

from apps.core.services.email_service import send_test_email
send_test_email('marcelojp03@gmail.com')
```

✅ **Resultado:** Email enviado exitosamente

---

### 2. **Probar Checkout con VPAY**

#### Request a `/api/sales/carts/{id}/checkout/`:
```json
{
  "customer_id": 1,
  "shipping_address": {
    "line1": "Av. Cristo Redentor #456",
    "city": "Santa Cruz",
    "state": "Santa Cruz",
    "notes": "Casa blanca, portón negro"
  },
  "payment_method": "CARD",
  "payment_provider": "VPAY",
  "notes": "Pago con tarjeta VPAY"
}
```

#### Response:
```json
{
  "id": 15,
  "order_number": "ORD-20241112-0005",
  "status": "CONFIRMED",  // ✅ Auto-confirmado
  "payment_status": "PAID",
  "total": "1250.00",
  "items": [...],
  "shipping_address": {...}
}
```

✅ **Resultado:** 
- Pedido creado y confirmado
- Stock decrementado
- Carrito vaciado
- **Email enviado a marcelojp03@gmail.com**

---

## 🔧 Configuración de Auto-Confirmación

VPAY debe configurarse para **auto-confirmar** o **quedar pendiente** según tu necesidad:

### Opción A: Auto-Confirmar VPAY (Simulación)
```python
# En sales/views.py
should_auto_confirm = payment_provider in ['MOCK', 'QR', 'VPAY'] or payment_method in ['CASH', 'TRANSFER']
```

✅ **Uso:** Cuando VPAY es simulado en desarrollo
✅ **Email:** Se envía inmediatamente

---

### Opción B: VPAY con Webhook (Producción)
```python
# En sales/views.py
should_auto_confirm = payment_provider in ['MOCK', 'QR'] or payment_method in ['CASH', 'TRANSFER']
```

❌ VPAY **NO** auto-confirma
⏳ Espera webhook de VPAY
✅ **Email:** Se envía cuando VPAY confirme el pago

---

## 📊 Comparación de Providers

| Provider | Método | Auto-Confirma | Email Inmediato | Requiere Webhook |
|----------|--------|---------------|-----------------|------------------|
| MOCK | CARD/QR | ✅ Sí | ✅ Sí | ❌ No |
| MOCK | CASH | ✅ Sí | ✅ Sí | ❌ No |
| MOCK | TRANSFER | ✅ Sí | ✅ Sí | ❌ No |
| QR | QR | ✅ Sí | ✅ Sí | ❌ No |
| VPAY | CARD | 🔧 Configurable | 🔧 Depende | 🔧 Depende |
| VPAY | QR | 🔧 Configurable | 🔧 Depende | 🔧 Depende |
| STRIPE | CARD | ❌ No | ⏳ Después | ✅ Sí |
| PAYPAL | CARD | ❌ No | ⏳ Después | ✅ Sí |

---

## 🎨 Personalizar Email

### Cambiar remitente:
```python
# settings.py
DEFAULT_FROM_EMAIL = 'tu-email@dominio.com'  # Debe estar verificado en Turbo SMTP
```

### Modificar template HTML:
Editar `apps/core/services/email_service.py` → función `send_order_confirmation_email()`

---

## 🔒 Seguridad

### Credenciales en producción:
```env
# .env
EMAIL_HOST=pro.eu.turbo-smtp.com
EMAIL_PORT=465
EMAIL_HOST_USER=1200a91cedc0cac41b08
EMAIL_HOST_PASSWORD=pSPJhX9oMtzmAbBjckie
DEFAULT_FROM_EMAIL=marcelojp03@gmail.com
```

```python
# settings.py
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

---

## ✅ Checklist de Implementación

- [x] VPAY agregado como payment provider
- [x] Configuración SMTP en settings.py
- [x] Servicio de email creado (`email_service.py`)
- [x] Integración con checkout (envío automático)
- [x] Email de prueba enviado exitosamente
- [ ] Configurar VPAY para auto-confirmar o webhook
- [ ] Implementar endpoint de webhook VPAY (si no auto-confirma)
- [ ] Configurar dominio verificado en Turbo SMTP (opcional)
- [ ] Personalizar template HTML del email (opcional)

---

## 🚀 Próximos Pasos

1. **Decidir flujo de VPAY:**
   - ¿Auto-confirmar? (desarrollo/simulación)
   - ¿Webhook? (producción)

2. **Si webhook:**
   - Crear endpoint `/api/payments/vpay-webhook/`
   - Validar firma de VPAY
   - Llamar a `confirm_payment(order_id)`
   - Email se enviará automáticamente

3. **Personalización:**
   - Logo de la empresa en email
   - Colores corporativos
   - Footer personalizado

---

## 📞 Contacto

Si tienes problemas con:
- **Email:** Verificar credenciales de Turbo SMTP
- **VPAY:** Consultar documentación de la pasarela
- **Auto-confirmación:** Revisar `sales/views.py` línea 214

¡Listo! 🎉
