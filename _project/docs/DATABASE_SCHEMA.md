# Esquema de Base de Datos - E-commerce Django

## Resumen del Proyecto

Sistema de e-commerce completo con:
- **RBAC (Control de Acceso Basado en Roles)** 
- **Catálogo con variantes y atributos dinámicos**
- **Inventario multi-almacén**
- **Sistema de pedidos y pagos desacoplados**
- **Analytics para reportes con IA y forecasting**

---

## Módulos y Modelos

### 1. SECURITY (Seguridad y RBAC)

#### User
Usuario del sistema extendido de AbstractUser.
- `username`, `email`, `password` (heredados)
- `phone`: Teléfono
- `avatar`: URL/path de avatar

#### Role
Roles del sistema vinculados a Groups de Django.
- `name`: Nombre del rol (Admin, Vendedor, Almacenero)
- `group`: Relación 1:1 con Group de Django
- `description`: Descripción del rol

#### Resource
Recursos principales del menú.
- `name`: Nombre del recurso (Catálogo, Ventas, Inventario)
- `description`: Descripción
- `order`: Orden de visualización
- `icon`: Icono para UI

#### Subresource
Subrecursos dentro de un recurso.
- `resource`: FK a Resource
- `name`: Nombre del subrecurso
- `url`: URL/ruta del subrecurso
- `order`: Orden de visualización

#### RoleResource
Asignación de permisos: qué puede ver cada rol.
- `role`: FK a Role
- `resource`: FK a Resource
- `subresource`: FK a Subresource
- **Unique together**: (role, resource, subresource)

---

### 2. CATALOG (Catálogo de Productos)

#### Category
Categorías jerárquicas de productos.
- `name`: Nombre de categoría
- `parent`: FK autorreferencial para jerarquía
- `status`: ACTIVE/INACTIVE
- `created_at`: Fecha de creación

#### Attribute
Atributos para variantes (Talla, Color, etc).
- `name`: Nombre del atributo (único)

#### AttributeValue
Valores de atributos (S, M, L / Rojo, Azul).
- `attribute`: FK a Attribute
- `value`: Valor específico
- **Unique together**: (attribute, value)

#### Product
Producto maestro.
- `sku`: Código único del producto
- `name`: Nombre del producto
- `description`: Descripción detallada
- `base_price`: Precio base
- `brand`: Marca
- `status`: ACTIVE/INACTIVE/DRAFT
- `categories`: M2M con Category (through ProductCategory)
- `created_at`, `updated_at`: Timestamps

#### ProductCategory
Tabla intermedia Product-Category (M2M).
- `product`: FK a Product
- `category`: FK a Category

#### ProductVariant
Variantes de producto (SKU específico).
- `product`: FK a Product
- `code`: Código único de variante
- `price`: Precio de la variante
- `status`: ACTIVE/INACTIVE
- `created_at`: Timestamp

#### VariantAttributeValue
Atributos asignados a variante.
- `variant`: FK a ProductVariant
- `attribute`: FK a Attribute
- `attribute_value`: FK a AttributeValue
- **Unique together**: (variant, attribute)

#### ProductImage
Imágenes de productos.
- `product`: FK a Product
- `url`: URL de imagen (S3/local)
- `alt`: Texto alternativo
- `is_main`: Imagen principal
- `sort`: Orden de visualización
- `created_at`: Timestamp

---

### 3. INVENTORY (Inventario)

#### Warehouse
Almacenes o bodegas.
- `name`: Nombre del almacén
- `location`: Ubicación/dirección
- `code`: Código único
- `is_active`: Activo/Inactivo
- `created_at`: Timestamp

#### Inventory
Inventario por variante y almacén.
- `variant`: FK a ProductVariant
- `warehouse`: FK a Warehouse
- `stock_on_hand`: Stock físico disponible
- `stock_reserved`: Stock reservado en pedidos
- `min_stock`: Stock mínimo para alertas
- `updated_at`: Timestamp
- **Unique together**: (variant, warehouse)

**Métodos**:
- `stock_available`: Property (stock_on_hand - stock_reserved)
- `reserve_stock(quantity)`: Reserva stock
- `release_stock(quantity)`: Libera stock reservado
- `confirm_sale(quantity)`: Descuenta stock físico

---

### 4. SALES (Ventas)

#### Customer
Clientes del ecommerce.
- `full_name`: Nombre completo
- `email`: Email
- `phone`: Teléfono
- `ci_nit`: CI/NIT
- `is_active`: Activo/Inactivo
- `created_at`: Timestamp

#### Address
Direcciones de clientes.
- `customer`: FK a Customer
- `line1`: Dirección
- `city`: Ciudad
- `state`: Departamento
- `zip`: Código postal
- `notes`: Referencias
- `is_default`: Dirección por defecto

#### Cart
Carrito de compras.
- `customer`: 1:1 con Customer
- `created_at`, `updated_at`: Timestamps

#### CartItem
Items del carrito.
- `cart`: FK a Cart
- `variant`: FK a ProductVariant
- `qty`: Cantidad
- `unit_price`: Precio unitario
- `added_at`: Timestamp
- **Unique together**: (cart, variant)

#### Order
Pedidos/Órdenes.
- `customer`: FK a Customer
- `order_number`: Número único de orden
- `currency`: Moneda (BOB, USD)
- `status`: CREATED/PAID/PROCESSING/SHIPPED/DELIVERED/CANCELLED
- `subtotal`: Subtotal
- `discount_total`: Descuentos
- `shipping_total`: Envío
- `total`: Total
- `payment_status`: PENDING/PAID/FAILED/REFUNDED
- `shipping_address`: FK a Address
- `created_at`, `updated_at`: Timestamps

#### OrderItem
Items de pedido.
- `order`: FK a Order
- `variant`: FK a ProductVariant
- `qty`: Cantidad
- `unit_price`: Precio unitario
- `discount`: Descuento aplicado

#### Payment
Pagos (desacoplados de Order).
- `order`: 1:1 con Order
- `provider`: Proveedor (STRIPE/PAYPAL/MOCK/QR)
- `provider_ref`: Referencia del proveedor
- `status`: INIT/PENDING/SUCCESS/FAILED/CANCELLED
- `amount`: Monto
- `paid_at`: Fecha de pago
- `created_at`: Timestamp

---

### 5. ANALYTICS (Reportes y Forecasting)

#### SaleFact
Tabla de hechos para análisis (desnormalizada).
- `date`: Fecha de venta
- `product_id`, `product_name`: Info del producto
- `category_id`, `category_name`: Info de categoría
- `variant_id`, `variant_code`: Info de variante
- `customer_id`, `customer_name`: Info de cliente
- `qty`: Cantidad vendida
- `revenue`: Ingresos
- `cost`: Costo (opcional)
- `discount`: Descuentos
- `order_id`: Referencia a orden
- `created_at`: Timestamp

**Índices**: Por fecha, producto+fecha, categoría+fecha, cliente+fecha

#### ForecastModel
Modelos de predicción entrenados.
- `name`: Nombre del modelo
- `description`: Descripción
- `model_type`: Tipo (RandomForest, etc)
- `file_path`: Path al .joblib
- `mae`, `rmse`, `r2_score`: Métricas de evaluación
- `training_date_from`, `training_date_to`: Rango de entrenamiento
- `features_used`: JSON de features
- `is_active`: Activo/Inactivo
- `created_at`: Timestamp

#### Report
Registro de reportes generados.
- `report_type`: Tipo de reporte (SALES_BY_DATE, etc)
- `title`: Título
- `description`: Descripción
- `format`: PDF/EXCEL/CSV/JSON
- `filters`: JSON con filtros aplicados
- `generated_by`: Usuario que generó
- `file_path`: Path del archivo generado
- `file_size`: Tamaño en bytes
- `created_at`: Timestamp

---

## Relaciones Principales

```
User (security) 1:N Order (sales)
Customer (sales) 1:N Order
Customer 1:N Address
Customer 1:1 Cart
Cart 1:N CartItem
Order 1:N OrderItem
Order 1:1 Payment

Product (catalog) 1:N ProductVariant
Product 1:N ProductImage
Product N:M Category (through ProductCategory)
ProductVariant 1:N VariantAttributeValue
ProductVariant 1:N Inventory
Warehouse 1:N Inventory

Role (security) N:M Subresource (through RoleResource)
Resource 1:N Subresource
```

---

## Características Clave del Diseño

### 1. **Variantes con Atributos Dinámicos**
- Soporta cualquier tipo de producto (ropa, electrónica, etc)
- Atributos configurables (Talla, Color, Capacidad, etc)
- Cada variante tiene precio y stock independiente

### 2. **Inventario Multi-Almacén**
- Stock por variante × almacén
- Reserva de stock (prevent overselling)
- Métodos para gestión de stock

### 3. **Pedidos y Pagos Desacoplados**
- Order independiente de Payment
- Permite múltiples proveedores de pago
- Estado de pago separado de estado de orden

### 4. **RBAC Completo**
- Roles vinculados a Groups de Django
- Menú dinámico basado en permisos
- Resources y Subresources para UI

### 5. **Analytics Optimizado**
- SaleFact desnormalizado para queries rápidas
- Índices estratégicos por fecha y dimensiones
- Preparado para forecasting con ML

---

## Próximos Pasos

1. **Crear fixtures de demo** (categorías, atributos, productos)
2. **Implementar serializers y views DRF**
3. **Crear endpoints de API**:
   - Auth y menú dinámico
   - CRUD de catálogo
   - Carrito y checkout
   - Reportes con IA
   - Forecasting
4. **Management commands**:
   - Generar variante DEFAULT
   - Poblar SaleFact desde Orders
   - ETL de datos legacy
5. **Tests unitarios e integración**
