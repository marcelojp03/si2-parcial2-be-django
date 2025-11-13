# Sistema de Reservación de Stock

## 📊 Cómo Funciona Actualmente

### Flujo de Stock en una Compra:

```
1. Checkout → Stock RESERVADO (stock_reserved++)
2. Confirmar Pago → Stock DEDUCIDO (stock_on_hand--, stock_reserved--)
3. Cancelar → Stock LIBERADO (stock_reserved--)
```

### Estados del Stock:

En el modelo `Inventory`:
- **`stock_on_hand`**: Stock físico total en el almacén
- **`stock_reserved`**: Stock reservado en órdenes pendientes
- **`stock_available`**: Stock disponible para venta = `stock_on_hand - stock_reserved`

---

## 🔄 Ejemplo Práctico

### Estado Inicial
```
Producto: Google Pixel 6 (128GB Black)
stock_on_hand: 100
stock_reserved: 0
stock_available: 100
```

### Cliente A hace Checkout (compra 5 unidades)
```
POST /api/sales/carts/1/checkout/
{
  "customer_id": 1,
  "shipping_address_id": 1,
  "payment_method": "CREDIT_CARD"
}
```

**Resultado:**
```
stock_on_hand: 100 (sin cambios)
stock_reserved: 5 (aumentó)
stock_available: 95 (100 - 5)
Estado Orden: CREATED
Estado Pago: PENDING
```

### Cliente B intenta comprar 96 unidades
```
❌ ERROR: Solo hay 95 unidades disponibles
```

### Cliente A confirma el pago
```
POST /api/sales/orders/10/confirm_payment/
{
  "idempotency_key": "payment-12345",
  "provider": "STRIPE",
  "provider_ref": "ch_abc123"
}
```

**Resultado:**
```
stock_on_hand: 95 (decrementó 5)
stock_reserved: 0 (liberó 5)
stock_available: 95 (95 - 0)
Estado Orden: PAID
Estado Pago: SUCCESS
```

### Cliente C cancela su orden (había reservado 10)
```
POST /api/sales/orders/11/cancel/
```

**Resultado:**
```
stock_on_hand: 95 (sin cambios - no se había deducido)
stock_reserved: -10 (liberó 10)
stock_available: 105 (95 - (-10))
```

---

## ⚠️ PROBLEMA ACTUAL: Reservaciones Sin Expiración

### El Problema
Actualmente, cuando un cliente hace checkout pero **nunca paga**, el stock queda **reservado indefinidamente**.

**Ejemplo del problema:**
```
1. Cliente hace checkout → reserva 50 unidades
2. Cliente cierra el navegador sin pagar
3. Stock queda reservado para siempre
4. Otros clientes no pueden comprar esas 50 unidades
5. Stock "fantasma" bloqueado
```

### Duración Actual de Reservación
**⏰ INFINITA** - No hay límite de tiempo configurado

---

## ✅ Solución Recomendada: Sistema de Expiración

### Configuración Propuesta

**Tiempo de reservación:** 30 minutos (configurable)

```python
# settings.py
ORDER_RESERVATION_TIMEOUT = 30  # minutos
```

### Nuevo Campo en Order
```python
reservation_expires_at = models.DateTimeField(null=True, blank=True)
```

### Flujo con Expiración

```
1. Checkout → Crear orden
   - reservation_expires_at = now() + 30 minutos
   - stock_reserved++
   
2. Cada X minutos → Tarea automática (Celery)
   - Buscar órdenes expiradas (status=CREATED, expires_at < now())
   - Cambiar status a EXPIRED
   - Liberar stock (stock_reserved--)
   
3a. Cliente paga antes de expirar → Orden PAID
3b. Cliente no paga → Orden EXPIRED (auto-cancelada)
```

---

## 🛠️ Implementación Sugerida

### 1. Agregar campo de expiración

**Migración:**
```python
# sales/migrations/0003_add_reservation_expiration.py
from django.db import migrations, models
from django.utils import timezone
from datetime import timedelta

class Migration(migrations.Migration):
    dependencies = [
        ('sales', '0002_payment_idempotency_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='reservation_expires_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]
```

### 2. Actualizar creación de orden

**sales/views.py - CartViewSet.checkout():**
```python
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

# Al crear la orden
order = Order.objects.create(
    customer_id=serializer.validated_data['customer_id'],
    shipping_address_id=serializer.validated_data['shipping_address_id'],
    status='CREATED',
    payment_status='PENDING',
    notes=serializer.validated_data.get('notes', ''),
    # NUEVO: Agregar expiración
    reservation_expires_at=timezone.now() + timedelta(
        minutes=getattr(settings, 'ORDER_RESERVATION_TIMEOUT', 30)
    )
)
```

### 3. Tarea automática para liberar stock

**sales/tasks.py (con Celery):**
```python
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from sales.models import Order
from inventory.models import Inventory

@shared_task
def expire_pending_orders():
    """
    Busca órdenes con reservación expirada y libera el stock.
    Se ejecuta cada 5 minutos.
    """
    expired_orders = Order.objects.filter(
        status='CREATED',
        payment_status='PENDING',
        reservation_expires_at__lt=timezone.now(),
        is_expired=False
    )
    
    expired_count = 0
    
    for order in expired_orders:
        try:
            with transaction.atomic():
                # Bloquear orden e inventarios
                order = Order.objects.select_for_update().get(pk=order.pk)
                
                # Obtener variantes del pedido
                variant_ids = list(order.items.values_list('variant_id', flat=True))
                inventories = Inventory.objects.select_for_update().filter(
                    variant_id__in=variant_ids
                )
                
                inv_map = {inv.variant_id: inv for inv in inventories}
                
                # Liberar stock reservado
                for item in order.items.all():
                    inventory = inv_map.get(item.variant_id)
                    if inventory and inventory.stock_reserved >= item.qty:
                        inventory.stock_reserved -= item.qty
                        inventory.save(update_fields=['stock_reserved', 'updated_at'])
                
                # Marcar orden como expirada
                order.status = 'EXPIRED'
                order.is_expired = True
                order.save(update_fields=['status', 'is_expired', 'updated_at'])
                
                # Cancelar pago si existe
                try:
                    payment = order.payment
                    if payment.status == 'PENDING':
                        payment.status = 'EXPIRED'
                        payment.save(update_fields=['status'])
                except:
                    pass
                
                expired_count += 1
                
        except Exception as e:
            print(f"Error expirando orden {order.id}: {e}")
            continue
    
    return f"Expiradas {expired_count} órdenes"
```

**celerybeat_schedule:**
```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'expire-pending-orders': {
        'task': 'sales.tasks.expire_pending_orders',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}
```

### 4. Endpoint para verificar tiempo restante

**sales/views.py:**
```python
@extend_schema(summary="Verificar tiempo de reservación", tags=['Sales'])
@action(detail=True, methods=['get'])
def reservation_status(self, request, pk=None):
    """
    Retorna el tiempo restante de la reservación.
    """
    order = self.get_object()
    
    if order.status != 'CREATED':
        return Response({
            'status': order.status,
            'message': 'La orden ya no está en estado de reservación'
        })
    
    if not order.reservation_expires_at:
        return Response({
            'status': 'CREATED',
            'message': 'Reservación sin límite de tiempo',
            'expires_at': None
        })
    
    now = timezone.now()
    
    if order.reservation_expires_at <= now:
        return Response({
            'status': 'EXPIRED',
            'message': 'La reservación ha expirado',
            'expired_at': order.reservation_expires_at
        }, status=status.HTTP_410_GONE)
    
    time_remaining = order.reservation_expires_at - now
    
    return Response({
        'status': 'ACTIVE',
        'expires_at': order.reservation_expires_at,
        'time_remaining_seconds': int(time_remaining.total_seconds()),
        'time_remaining_minutes': int(time_remaining.total_seconds() / 60)
    })
```

---

## 📱 Frontend: Mostrar Temporizador

### React Example
```javascript
function CheckoutTimer({ orderId, expiresAt }) {
  const [timeLeft, setTimeLeft] = useState(null);
  
  useEffect(() => {
    const calculateTimeLeft = () => {
      const diff = new Date(expiresAt) - new Date();
      if (diff <= 0) {
        // Orden expirada
        setTimeLeft(0);
        return;
      }
      setTimeLeft(Math.floor(diff / 1000)); // segundos
    };
    
    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);
    
    return () => clearInterval(timer);
  }, [expiresAt]);
  
  if (timeLeft === null) return null;
  if (timeLeft === 0) {
    return (
      <div className="alert alert-danger">
        ⏰ Tu reservación ha expirado. Por favor, crea una nueva orden.
      </div>
    );
  }
  
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  
  return (
    <div className="alert alert-warning">
      ⏱️ Tiempo para completar el pago: {minutes}:{seconds.toString().padStart(2, '0')}
    </div>
  );
}

// Uso
<CheckoutTimer 
  orderId={order.id} 
  expiresAt={order.reservation_expires_at} 
/>
```

---

## 🎯 Recomendaciones

### Tiempos de Expiración por Tipo

| Método de Pago | Tiempo Recomendado | Razón |
|----------------|-------------------|-------|
| Tarjeta (Stripe/PayPal) | 15-30 minutos | Pago inmediato |
| Transferencia Bancaria | 24 horas | Requiere confirmación manual |
| QR | 30 minutos | Pago semi-inmediato |
| Efectivo | 2-4 horas | Pago en tienda |

### Configuración Dinámica
```python
# sales/views.py - checkout
timeout_minutes = {
    'CREDIT_CARD': 30,
    'DEBIT_CARD': 30,
    'QR': 30,
    'BANK_TRANSFER': 1440,  # 24 horas
    'CASH': 240,  # 4 horas
}.get(payment_method, 30)

order.reservation_expires_at = timezone.now() + timedelta(minutes=timeout_minutes)
```

---

## 📧 Notificaciones

### Email de recordatorio
```python
@shared_task
def send_expiration_reminder():
    """
    Envía email 10 minutos antes de que expire la reservación.
    """
    expiring_soon = Order.objects.filter(
        status='CREATED',
        payment_status='PENDING',
        reservation_expires_at__lte=timezone.now() + timedelta(minutes=10),
        reservation_expires_at__gt=timezone.now(),
        reminder_sent=False
    )
    
    for order in expiring_soon:
        send_email(
            to=order.customer.email,
            subject='¡Tu orden está por expirar!',
            template='order_expiring_soon.html',
            context={'order': order}
        )
        order.reminder_sent = True
        order.save(update_fields=['reminder_sent'])
```

---

## 🔍 Monitoreo

### Métricas Importantes
- Tasa de expiración: % de órdenes que expiran sin pago
- Tiempo promedio de pago: ¿Cuánto tardan en pagar?
- Stock liberado por expiración: Impacto en ventas

### Dashboard Query
```sql
SELECT 
  DATE(created_at) as fecha,
  COUNT(*) as total_ordenes,
  SUM(CASE WHEN status = 'EXPIRED' THEN 1 ELSE 0 END) as expiradas,
  SUM(CASE WHEN status = 'PAID' THEN 1 ELSE 0 END) as pagadas,
  ROUND(AVG(TIMESTAMPDIFF(MINUTE, created_at, updated_at)), 2) as minutos_promedio
FROM sales_order
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at)
ORDER BY fecha DESC;
```

---

## ✅ Estado Actual vs Propuesto

| Aspecto | Estado Actual | Con Expiración |
|---------|---------------|----------------|
| **Duración de reservación** | ⏰ Infinita | ⏰ 30 minutos |
| **Stock bloqueado** | ❌ Permanente | ✅ Temporal |
| **Órdenes abandonadas** | ❌ Bloquean stock | ✅ Auto-liberan |
| **Experiencia de usuario** | ⚠️ Sin urgencia | ✅ Contador de tiempo |
| **Gestión de inventario** | ❌ Stock fantasma | ✅ Stock real |
| **Conversión** | ⚠️ Baja urgencia | ✅ Mayor urgencia |

---

## 🚀 Próximos Pasos

1. **Corto Plazo (Ahora):**
   - Documentar el comportamiento actual
   - Informar al equipo del riesgo de stock fantasma

2. **Mediano Plazo (Sprint 2):**
   - Implementar campo `reservation_expires_at`
   - Crear tarea de expiración manual (management command)

3. **Largo Plazo (Sprint 3):**
   - Implementar Celery + Celery Beat
   - Agregar notificaciones por email
   - Dashboard de métricas

---

## 📝 Resumen

**Sistema Actual:**
```
Checkout → Stock reservado INDEFINIDAMENTE
Pago → Stock deducido
Cancelar → Stock liberado MANUALMENTE
```

**Sistema Propuesto:**
```
Checkout → Stock reservado por 30 minutos
├── Paga antes de 30 min → Stock deducido ✅
└── No paga en 30 min → Stock liberado automáticamente ✅
```

**Beneficios:**
- ✅ Elimina stock fantasma
- ✅ Mejora disponibilidad real
- ✅ Aumenta urgencia de compra
- ✅ Gestión automática de abandonos
