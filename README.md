# 🛍️ E-Commerce API Backend

API REST completa para plataforma de comercio electrónico desarrollada con Django REST Framework.

## � Estructura del Proyecto

```
ecommerce-django-be/
├── _project/docs/                    # �📚 Documentación completa
│   ├── API_DOCUMENTATION.md
│   ├── API_QUICK_REFERENCE.md
│   ├── API_STATUS_REPORT.md
│   ├── ANGULAR_FRONTEND_GUIDE.md
│   ├── FRONTEND_COMPONENTS_GUIDE.md
│   ├── DATABASE_SCHEMA.md
│   └── Ecommerce_API.postman_collection.json
├── _project/tests/                   # 🧪 Tests y validaciones
│   ├── test_endpoints.py
│   └── test_results.json
├── _project/scripts/                 # 🔧 Scripts de utilidad
│   ├── populate_db.py
│   └── check_tables.py
├── _project/fixtures/                # 📦 Datos de prueba
├── catalog/                 # 📦 Módulo de productos
├── inventory/               # 📊 Módulo de inventario
├── sales/                   # 🛒 Módulo de ventas
├── security/                # 🔐 Módulo de autenticación
├── analytics/               # 📈 Módulo de reportes
├── ecommerce/               # ⚙️ Configuración Django
├── manage.py
├── requirements.txt
└── README.md
```

**Ver estructura detallada:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📚 Documentación

### 🚀 Guías de Inicio
- **[_project/docs/QUICK_START.md](_project/docs/QUICK_START.md)** - Inicio rápido del proyecto
- **[_project/docs/API_STATUS_REPORT.md](_project/docs/API_STATUS_REPORT.md)** - Estado actual del backend (96.4% funcional)

### 📖 Documentación API
- **[_project/docs/API_DOCUMENTATION.md](_project/docs/API_DOCUMENTATION.md)** - Documentación completa de todos los endpoints
- **[_project/docs/API_QUICK_REFERENCE.md](_project/docs/API_QUICK_REFERENCE.md)** - Referencia rápida de endpoints
- **[_project/docs/Ecommerce_API.postman_collection.json](_project/docs/Ecommerce_API.postman_collection.json)** - Colección de Postman

### 👨‍💻 Guías para Frontend
- **[_project/docs/ANGULAR_FRONTEND_GUIDE.md](_project/docs/ANGULAR_FRONTEND_GUIDE.md)** - Guía completa para Angular
- **[_project/docs/FRONTEND_COMPONENTS_GUIDE.md](_project/docs/FRONTEND_COMPONENTS_GUIDE.md)** - Componentes recomendados (React/Vue/Angular)

### 🗄️ Base de Datos
- **[_project/docs/DATABASE_SCHEMA.md](_project/docs/DATABASE_SCHEMA.md)** - Esquema completo de la base de datos
- **[_project/docs/ERD.md](_project/docs/ERD.md)** - Diagrama entidad-relación

## 🚀 Inicio Rápido

### URLs Principales

```
Base URL:     http://127.0.0.1:8000
Swagger UI:   http://127.0.0.1:8000/api/_project/docs/
ReDoc:        http://127.0.0.1:8000/api/redoc/
Admin Panel:  http://127.0.0.1:8000/admin/
Healthcheck:  http://127.0.0.1:8000/api/healthz/
```

### Iniciar Servidor

```bash
# Activar entorno virtual
.\venv\Scripts\activate

# Ejecutar servidor
python manage.py runserver
```

## 📦 Módulos Implementados (5 Módulos - 100% Funcionales)

### 1. **CATALOG** `/api/catalog/` - Gestión de Productos ✅
```
📁 catalog/
├── models.py          # Category, Attribute, Product, ProductVariant
├── serializers.py     # Serializers con relaciones anidadas
├── views.py           # ViewSets con filtros avanzados
└── urls.py            # 15+ endpoints
```
- Categorías jerárquicas con subcategorías
- Atributos configurables (Color, Talla, Material, etc.)
- Productos con múltiples variantes
- Búsqueda y filtros avanzados
- Gestión de imágenes

### 2. **INVENTORY** `/api/inventory/` - Control de Inventario ✅
```
📁 inventory/
├── models.py          # Warehouse, Inventory
├── serializers.py     # Serializers con stock disponible
├── views.py           # Actions para ajustar/reservar stock
└── urls.py            # 12+ endpoints
```
- Múltiples almacenes
- Stock por almacén y variante
- Reservas y confirmaciones de stock
- Alertas de stock bajo
- **Bloqueo pesimista** para evitar race conditions

### 3. **SALES** `/api/sales/` - Ventas y Pedidos ✅
```
📁 sales/
├── models.py          # Customer, Cart, Order, Payment
├── serializers.py     # Serializers con cálculos de totales
├── views.py           # Checkout, confirmar pago, cancelar
└── urls.py            # 18+ endpoints
```
- Gestión de clientes y direcciones
- Carrito de compras completo
- Proceso de checkout con transacciones atómicas
- Confirmación de pagos con **idempotencia**
- Cancelación con liberación automática de stock
- Cálculo automático de IVA (13%)

### 4. **SECURITY** `/api/auth/` - Autenticación y RBAC ✅
```
📁 security/
├── models.py          # User, Role, Resource, RoleResource
├── serializers.py     # Serializers con permisos
├── views.py           # Auth, usuarios, roles, permisos
└── urls.py            # 15+ endpoints
```
- Sistema RBAC completo
- Menú dinámico basado en permisos
- Gestión de usuarios y roles
- Permisos granulares por recurso

### 5. **ANALYTICS** `/api/analytics/` - Reportes y Análisis ✅
```
📁 analytics/
├── models.py          # SaleFact, ForecastModel, Report
├── serializers.py     # Serializers con métricas
├── views.py           # Dashboard, reportes, forecasting
└── urls.py            # 10+ endpoints
```
- Dashboard con métricas de ventas
- Top productos y categorías
- Generación de reportes personalizados
- Forecasting de ventas (simulado, listo para ML real)
- **SaleFact automático** via signals

## ⚡ Características Avanzadas Implementadas

### ✅ Concurrencia y Transacciones
- **Bloqueo Pesimista** (`select_for_update()`) en operaciones críticas
- **Transacciones Atómicas** para garantizar integridad
- **Idempotencia** en confirmación de pagos para evitar duplicados

### ✅ Automatización
- **Signal Automático**: Pedidos PAID → SaleFact automáticamente
- **Reserva Automática**: Checkout → Stock reservado
- **Liberación Automática**: Cancelación → Stock liberado

### ✅ Validaciones
- **Máquina de Estados**: Solo transiciones válidas (CREATED → PAID)
- **Validación de Stock**: Verifica disponibilidad antes de confirmar
- **Validación de Concurrencia**: Evita confirmaciones simultáneas

## 🔥 Flujo Completo de Compra

```
1. Cliente agrega al carrito
   POST /api/sales/carts/{id}/add_item/

2. Cliente hace checkout
   POST /api/sales/carts/{id}/checkout/
   → Pedido CREATED
   → Stock RESERVADO

3. Confirmar pago (con idempotencia)
   POST /api/sales/orders/{id}/confirm_payment/
   → Pedido PAID
   → Stock DECREMENTADO
   → SaleFact CREADO (automático)

4. Analytics actualizado
   GET /api/analytics/sales/dashboard/
```

## 💾 Base de Datos

**Motor:** PostgreSQL 15+ (AWS RDS)  
**Schema:** `si2-ecommmerce`  
**Tablas:** 34 tablas organizadas en 5 módulos

**Datos Precargados:**
- 6 categorías jerárquicas
- 4 atributos (Color, Talla, Material, Estilo)
- 19 valores de atributos
- 3 almacenes (Principal, Norte, Sur)

## 🛠️ Stack Tecnológico

- **Python:** 3.12.9
- **Django:** 5.2.7
- **Django REST Framework:** 3.16.1
- **PostgreSQL:** 15+ en AWS RDS
- **drf-spectacular:** 0.28.0 (OpenAPI/Swagger)
- **django-cors-headers:** 4.9.0
- **python-decouple:** 3.8

## 🎯 Características Principales

## 🎯 Endpoints Totales: ~70+ Documentados

- **System:** 3 endpoints (healthcheck, schema, docs)
- **Catalog:** 15+ endpoints (categorías, atributos, productos)
- **Inventory:** 12+ endpoints (almacenes, inventario, stock)
- **Sales:** 18+ endpoints (clientes, carritos, pedidos)
- **Security:** 15+ endpoints (auth, usuarios, roles, permisos)
- **Analytics:** 10+ endpoints (dashboard, reportes, forecasting)

## 📱 CORS Configurado

- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://127.0.0.1:8000` (mismo origen)

## 🧪 Pruebas

### Swagger UI (Recomendado)
```
http://127.0.0.1:8000/api/docs/
```

### Postman
Importar: `_project/docs/Ecommerce_API.postman_collection.json`

### Healthcheck
```bash
curl http://127.0.0.1:8000/api/healthz/
```

## � Configuración de Negocio

- **Moneda:** BOB (Bolivianos)
- **IVA:** 13%
- **Formato fechas:** ISO 8601
- **Paginación:** 10 items/página (max 100)

## � Seguridad

### Actualmente
- `AllowAny` para desarrollo
- Sesiones de Django

### Para Producción (Pendiente)
- JWT Authentication
- Rate Limiting / Throttling
- Permisos `IsAuthenticated`

## 📝 Comandos Útiles

```bash
# === Desarrollo ===
python manage.py runserver                    # Iniciar servidor
python manage.py shell                        # Shell interactivo

# === Migraciones ===
python manage.py makemigrations               # Crear migraciones
python manage.py migrate                      # Aplicar migraciones
python manage.py showmigrations               # Ver estado de migraciones

# === Usuarios ===
python manage.py createsuperuser              # Crear superusuario

# === Scripts de utilidad ===
python _project/scripts/populate_db.py                 # Poblar base de datos con datos demo
python _project/scripts/check_tables.py                # Verificar tablas en la base de datos

# === Testing ===
python _project/tests/test_endpoints.py                # Probar todos los endpoints (28 tests)
python manage.py test                         # Ejecutar tests unitarios

# === Producción ===
python manage.py collectstatic                # Recopilar archivos estáticos
python manage.py check --deploy               # Verificar configuración para producción
```

## 🔐 Configuración de Seguridad

Para producción, asegúrate de:

1. Cambiar `SECRET_KEY` en settings.py
2. Configurar `DEBUG = False`
3. Establecer `ALLOWED_HOSTS` apropiados
4. Usar PostgreSQL en lugar de SQLite
5. Configurar variables de entorno para datos sensibles

## 📄 Licencia

Proyecto académico - UAGRM - Sistemas de Información 2

