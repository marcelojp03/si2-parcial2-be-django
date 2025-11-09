# 🚀 Inicio Rápido - E-commerce Django

## Estado Actual del Proyecto ✅

**Base de datos completa implementada** con 5 apps y todos los modelos según el esquema propuesto.

### Lo que ya está hecho:
- ✅ 5 apps creadas: security, catalog, inventory, sales, analytics
- ✅ 20+ modelos implementados con relaciones completas
- ✅ Migraciones aplicadas
- ✅ Admin de Django configurado
- ✅ Datos iniciales cargados (categorías, atributos, almacenes)
- ✅ Documentación completa (DATABASE_SCHEMA.md, ERD.md)

---

## 📦 Verificar Base de Datos

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Verificar configuración
python manage.py check

# Ver datos cargados
python manage.py shell -c "from catalog.models import Category, Attribute, AttributeValue; from inventory.models import Warehouse; print(f'Categorias: {Category.objects.count()}'); print(f'Atributos: {Attribute.objects.count()}'); print(f'Valores: {AttributeValue.objects.count()}'); print(f'Almacenes: {Warehouse.objects.count()}')"

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

Luego abre: http://localhost:8000/admin

---

## 📊 Modelos Disponibles

### SECURITY (RBAC)
- `User` - Usuarios del sistema
- `Role` - Roles vinculados a Groups
- `Resource` - Recursos del menú
- `Subresource` - Subrecursos
- `RoleResource` - Permisos

### CATALOG (Productos)
- `Category` - Categorías jerárquicas ✅ 6 cargadas
- `Attribute` - Atributos (Talla, Color, etc) ✅ 4 cargados
- `AttributeValue` - Valores ✅ 19 cargados
- `Product` - Productos maestros
- `ProductVariant` - Variantes con SKU
- `ProductImage` - Imágenes

### INVENTORY (Almacenes)
- `Warehouse` - Almacenes ✅ 3 cargados
- `Inventory` - Stock por variante×almacén

### SALES (Ventas)
- `Customer` - Clientes
- `Address` - Direcciones
- `Cart` / `CartItem` - Carrito
- `Order` / `OrderItem` - Pedidos
- `Payment` - Pagos

### ANALYTICS (Reportes)
- `SaleFact` - Tabla de hechos
- `ForecastModel` - Modelos ML
- `Report` - Reportes generados

---

## 🎯 Ejemplos de Uso en el Shell

```python
# Entrar al shell
python manage.py shell

# Crear un producto
from catalog.models import Product, ProductVariant, Category
from inventory.models import Warehouse, Inventory

# Obtener categoría
laptops = Category.objects.get(name="Laptops")

# Crear producto
producto = Product.objects.create(
    sku="LAPTOP-001",
    name="Laptop Dell Inspiron 15",
    description="Laptop de alto rendimiento",
    base_price=5500.00,
    brand="Dell",
    status="ACTIVE"
)
producto.categories.add(laptops)

# Crear variante
variante = ProductVariant.objects.create(
    product=producto,
    code="LAPTOP-001-16GB-512GB",
    price=6500.00,
    status="ACTIVE"
)

# Agregar atributos a la variante
from catalog.models import Attribute, AttributeValue, VariantAttributeValue

ram = Attribute.objects.get(name="Memoria RAM")
ram_16gb = AttributeValue.objects.get(attribute=ram, value="16GB")

VariantAttributeValue.objects.create(
    variant=variante,
    attribute=ram,
    attribute_value=ram_16gb
)

storage = Attribute.objects.get(name="Almacenamiento")
storage_512 = AttributeValue.objects.get(attribute=storage, value="512GB")

VariantAttributeValue.objects.create(
    variant=variante,
    attribute=storage,
    attribute_value=storage_512
)

# Agregar inventario
wh = Warehouse.objects.get(code="WH-SC-01")
inventario = Inventory.objects.create(
    variant=variante,
    warehouse=wh,
    stock_on_hand=50,
    stock_reserved=0,
    min_stock=5
)

print(f"Stock disponible: {inventario.stock_available}")
```

---

## 🔄 Flujo de Carrito → Pedido

```python
# Crear cliente
from sales.models import Customer, Cart, CartItem, Order, OrderItem
from catalog.models import ProductVariant

cliente = Customer.objects.create(
    full_name="Juan Pérez",
    email="juan@example.com",
    phone="77777777",
    ci_nit="1234567"
)

# Crear carrito
carrito = Cart.objects.create(customer=cliente)

# Agregar items
variante = ProductVariant.objects.get(code="LAPTOP-001-16GB-512GB")
CartItem.objects.create(
    cart=carrito,
    variant=variante,
    qty=2,
    unit_price=variante.price
)

# Crear orden desde carrito
orden = Order.objects.create(
    customer=cliente,
    order_number="ORD-2025-0001",
    currency="BOB",
    status="CREATED"
)

# Copiar items del carrito
for item in carrito.items.all():
    OrderItem.objects.create(
        order=orden,
        variant=item.variant,
        qty=item.qty,
        unit_price=item.unit_price
    )
    # Reservar stock
    inventario = item.variant.inventories.first()
    inventario.reserve_stock(item.qty)

# Calcular totales
orden.subtotal = sum(item.subtotal for item in orden.items.all())
orden.total = orden.subtotal + orden.shipping_total - orden.discount_total
orden.save()
```

---

## 📈 Generar Datos de Ventas (SaleFact)

```python
from analytics.models import SaleFact
from datetime import date

# Crear registro de venta
SaleFact.objects.create(
    date=date.today(),
    product_id=producto.id,
    product_name=producto.name,
    category_id=laptops.id,
    category_name=laptops.name,
    variant_id=variante.id,
    variant_code=variante.code,
    customer_id=cliente.id,
    customer_name=cliente.full_name,
    qty=2,
    revenue=13000.00,  # 2 × 6500
    discount=0,
    order_id=orden.id
)
```

---

## 🎨 Próximos Pasos Inmediatos

### 1. Explorar Admin Django
```bash
python manage.py runserver
# Ir a http://localhost:8000/admin
# Crear productos, variantes, clientes manualmente
```

### 2. Crear API REST
```bash
# Día 1: Crear serializers
catalog/serializers.py
inventory/serializers.py
sales/serializers.py

# Día 2: Crear ViewSets
catalog/views.py
inventory/views.py
sales/views.py
```

### 3. Instalar dependencias adicionales
```bash
# JWT para autenticación
pip install djangorestframework-simplejwt

# Swagger para documentación
pip install drf-spectacular

# ML para forecasting
pip install scikit-learn pandas numpy joblib

# Reportes
pip install reportlab openpyxl
```

---

## 📚 Documentación

- **DATABASE_SCHEMA.md** → Descripción detallada de todos los modelos
- **ERD.md** → Diagrama de entidad-relación (Mermaid)
- **IMPLEMENTATION_SUMMARY.md** → Resumen completo de lo implementado
- **README.md** → Guía general del proyecto

---

## ✅ Checklist de Validación

- [ ] Servidor ejecutándose sin errores
- [ ] Admin accesible en /admin
- [ ] Datos iniciales cargados (6 categorías, 4 atributos, 3 almacenes)
- [ ] Puedo crear un producto en el admin
- [ ] Puedo crear una variante con atributos
- [ ] Puedo ver el stock en inventory

---

## 🆘 Solución de Problemas

**Error de migraciones**:
```bash
python manage.py migrate --run-syncdb
```

**Recargar datos iniciales**:
```bash
Get-Content populate_db.py | python manage.py shell
```

**Limpiar base de datos**:
```bash
rm db.sqlite3
python manage.py migrate
Get-Content populate_db.py | python manage.py shell
python manage.py createsuperuser
```

---

**¡Base de datos lista para desarrollo! 🎉**
