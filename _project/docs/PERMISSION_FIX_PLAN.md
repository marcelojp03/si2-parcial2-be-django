# 🔒 Plan de Corrección de Permisos

## ❌ Problema Detectado

Todos los ViewSets tienen `permission_classes = [AllowAny]` explícito, lo cual sobrescribe el default `IsAuthenticated` que configuramos en settings.py.

## ✅ Solución

Remover `permission_classes = [AllowAny]` de los ViewSets que deben estar protegidos, dejando que usen el permiso por defecto (`IsAuthenticated`).

---

## 📋 Cambios Necesarios por Módulo

### 1. **CATALOG** - Mantener Público (✓ OK)
**ViewSets:**
- `CategoryViewSet` → ✅ Mantener `AllowAny` (lectura pública del catálogo)
- `AttributeViewSet` → ✅ Mantener `AllowAny` (filtros del catálogo)
- `ProductViewSet` → ✅ Mantener `AllowAny` (lectura pública de productos)

**Justificación:** El catálogo debe ser accesible sin login para que los visitantes vean productos.

---

### 2. **INVENTORY** - Proteger Todo (❌ CAMBIAR)
**ViewSets:**
- `WarehouseViewSet` → ❌ Remover `AllowAny` → Usar `IsAuthenticated`
- `InventoryViewSet` → ❌ Remover `AllowAny` → Usar `IsAuthenticated`

**Justificación:** Solo administradores deben ver/modificar inventario.

**Cambio:**
```python
# ANTES
permission_classes = [AllowAny]

# DESPUÉS
# No especificar permission_classes (usa el default IsAuthenticated)
```

---

### 3. **SALES** - Proteger Todo (❌ CAMBIAR)
**ViewSets:**
- `CustomerViewSet` → ❌ Remover `AllowAny`
- `AddressViewSet` → ❌ Remover `AllowAny`
- `CartViewSet` → ❌ Remover `AllowAny`
- `OrderViewSet` → ❌ Remover `AllowAny`

**Justificación:** 
- Solo usuarios autenticados pueden tener carrito
- Solo usuarios autenticados pueden hacer pedidos
- Los clientes solo deben ver sus propios datos

**Cambio:**
```python
# ANTES
permission_classes = [AllowAny]

# DESPUÉS
# No especificar permission_classes
```

---

### 4. **ANALYTICS** - Proteger Todo (❌ CAMBIAR)
**ViewSets:**
- `SaleFactViewSet` → ❌ Remover `AllowAny`
- `ForecastModelViewSet` → ❌ Remover `AllowAny`
- `ReportViewSet` → ❌ Remover `AllowAny` (incluyendo action `ai_report`)

**Justificación:** Solo administradores deben ver analytics y generar reportes.

**Cambio:**
```python
# ANTES
permission_classes = [AllowAny]

# DESPUÉS
# No especificar permission_classes
```

---

### 5. **SECURITY** - Mixto (⚠️ REVISAR)
**ViewSets:**
- `UserViewSet` → ❌ Remover `AllowAny` (solo admins)
- `RoleViewSet` → ❌ Remover `AllowAny` (solo admins)
- `ResourceViewSet` → ❌ Remover `AllowAny` (solo admins)
- `RoleResourceViewSet` → ❌ Remover `AllowAny` (solo admins)

**Functions que DEBEN mantener AllowAny:**
- `login_view` → ✅ Mantener `@permission_classes([AllowAny])`
- `register_view` → ✅ Mantener `@permission_classes([AllowAny])`

**Functions que DEBEN estar protegidas:**
- `logout_view` → ✅ Ya tiene `@permission_classes([IsAuthenticated])`
- `current_user_view` → ✅ Ya tiene `@permission_classes([IsAuthenticated])`
- `user_menu_view` → ✅ Ya tiene `@permission_classes([IsAuthenticated])`

---

## 🎯 Resumen de Acciones

| Módulo | ViewSets a Cambiar | Action |
|--------|-------------------|---------|
| catalog | 0/3 | Mantener AllowAny |
| inventory | 2/2 | Remover AllowAny |
| sales | 4/4 | Remover AllowAny |
| analytics | 3/3 | Remover AllowAny |
| security | 4/4 | Remover AllowAny |
| **TOTAL** | **13/16** | **Proteger 81%** |

---

## ✅ Endpoints que quedarán públicos (AllowAny)

```
GET  /api/catalog/categories/          → Ver categorías
GET  /api/catalog/categories/{id}/     → Ver categoría específica
GET  /api/catalog/attributes/          → Ver atributos
GET  /api/catalog/attributes/{id}/     → Ver atributo específico
GET  /api/catalog/products/            → Ver productos
GET  /api/catalog/products/{id}/       → Ver producto específico

POST /api/auth/token/                  → Login JWT
POST /api/auth/token/refresh/          → Refresh JWT
POST /api/auth/register/               → Registro
POST /api/auth/login/                  → Login legacy

GET  /api/healthz/                     → Healthcheck
GET  /api/docs/                        → Swagger UI
GET  /api/schema/                      → OpenAPI Schema
```

---

## 🔒 Endpoints que quedarán protegidos (IsAuthenticated)

```
# INVENTORY (Solo Admin)
GET/POST/PUT/DELETE /api/inventory/warehouses/
GET/POST/PUT/DELETE /api/inventory/inventory/

# SALES (Usuario Autenticado)
GET/POST/PUT/DELETE /api/sales/customers/
GET/POST/PUT/DELETE /api/sales/addresses/
GET/POST/PUT/DELETE /api/sales/carts/
GET/POST /api/sales/carts/{id}/checkout/
GET/POST /api/sales/orders/
POST /api/sales/orders/{id}/confirm_payment/
POST /api/sales/orders/{id}/cancel/

# ANALYTICS (Solo Admin)
GET /api/analytics/sales/
GET /api/analytics/sales/dashboard/
GET/POST /api/analytics/forecasts/
GET /api/analytics/reports/
POST /api/analytics/reports/ai-report/  ← IMPORTANTE

# SECURITY (Solo Admin)
GET/POST/PUT/DELETE /api/auth/users/
GET/POST/PUT/DELETE /api/auth/roles/
GET/POST/PUT/DELETE /api/auth/resources/
GET/POST/PUT/DELETE /api/auth/permissions/

# AUTH (Usuario Autenticado)
GET /api/auth/me/
GET /api/auth/menu/
POST /api/auth/logout/
```

---

## 🔧 Implementación

### Paso 1: Inventory

```python
# inventory/views.py
class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    # permission_classes = [AllowAny]  ← REMOVER ESTA LÍNEA
    ...

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('variant', 'warehouse').all()
    serializer_class = InventorySerializer
    # permission_classes = [AllowAny]  ← REMOVER ESTA LÍNEA
    ...
```

### Paso 2: Sales

```python
# sales/views.py
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [AllowAny]  ← REMOVER ESTA LÍNEA
    ...

# Repetir para AddressViewSet, CartViewSet, OrderViewSet
```

### Paso 3: Analytics

```python
# analytics/views.py
class SaleFactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaleFact.objects.all().order_by('-date')
    serializer_class = SaleFactSerializer
    # permission_classes = [AllowAny]  ← REMOVER ESTA LÍNEA
    ...

# Repetir para ForecastModelViewSet, ReportViewSet
```

### Paso 4: Security

```python
# security/views.py
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('groups__role').all()
    # permission_classes = [AllowAny]  ← REMOVER ESTA LÍNEA
    ...

# Repetir para RoleViewSet, ResourceViewSet, RoleResourceViewSet
```

---

## ✅ Resultado Esperado

Después de los cambios, el Test 5 debería **pasar**:

```python
def test_without_token():
    response = requests.get(f"{BASE_URL}/api/sales/orders/")
    # Antes: 200 (error)
    # Después: 401 (correcto) ✓
```

---

## 📊 Comparación

### Antes (Actual)
```
Endpoints públicos:  ~75/75  (100%) ❌
Endpoints protegidos: 0/75   (0%)   ❌
```

### Después (Correcto)
```
Endpoints públicos:  ~12/75  (16%)  ✓
Endpoints protegidos: ~63/75  (84%)  ✓
```

---

## ⚠️ Nota Importante

El catálogo (products, categories, attributes) **DEBE** permanecer público porque:

1. Los usuarios no logueados deben poder ver productos
2. SEO requiere que los productos sean accesibles
3. Es el comportamiento estándar de e-commerce (Amazon, MercadoLibre, etc.)

Si queremos que TODO requiera autenticación (incluido el catálogo), entonces debemos cambiar también los ViewSets de catalog, pero esto NO es recomendable para un e-commerce.

---

**Decisión:** Mantener catálogo público, proteger el resto.
