# Estructura de Base de Datos - E-commerce Django

## 🗂️ Resumen General

**Total de Tablas:** 29 tablas organizadas en 7 módulos funcionales

### Módulos:
1. **Administration** (RBAC) - 5 tablas
2. **Customers** - 1 tabla
3. **Catalog** (Productos) - 8 tablas
4. **Inventory** - 2 tablas
5. **Sales** (Ventas y Carritos) - 6 tablas
6. **Analytics** (BI) - 2 tablas
7. **Django Core** - 5 tablas (auth, sessions, etc.)

---

## 1️⃣ MÓDULO: ADMINISTRATION (Autenticación y RBAC)

### [*] `administration_user`
**Propósito:** Usuarios del sistema (clientes y staff)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| username | CharField | Usuario único |
| email | EmailField | Email |
| first_name | CharField | Nombre |
| last_name | CharField | Apellido |
| phone | CharField | Teléfono |
| password | CharField | Hash de contraseña |
| avatar | CharField | URL avatar |
| avatar_s3_bucket | CharField | Bucket S3 |
| avatar_s3_key | CharField | Key S3 |
| is_staff | BooleanField | ¿Es staff? |
| is_superuser | BooleanField | ¿Es superuser? |
| is_active | BooleanField | ¿Está activo? |
| date_joined | DateTimeField | Fecha registro |
| last_login | DateTimeField | Último login |

**Relaciones:**
- `OneToOne` → `customers_customer` (Cliente asociado)
- `ManyToMany` → `auth_group` (Grupos/Roles)
- `ManyToMany` → `auth_permission` (Permisos directos)

---

### [*] `administration_role`
**Propósito:** Roles del sistema (Admin, Gerente, Vendedor, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField | Nombre del rol |
| description | CharField | Descripción |
| group | OneToOneField | FK → auth_group |

**Relaciones:**
- `OneToOne` → `auth_group`
- `ManyToMany` → `administration_resource` (a través de role_resource)

---

### [*] `administration_resource`
**Propósito:** Recursos del sistema (módulos)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField | Nombre recurso |
| description | CharField | Descripción |
| order | PositiveIntegerField | Orden en menú |
| icon | CharField | Ícono |

---

### [*] `administration_subresource`
**Propósito:** Sub-recursos (páginas/acciones dentro de un recurso)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| resource | ForeignKey | FK → resource |
| name | CharField | Nombre |
| description | CharField | Descripción |
| url | CharField | URL/ruta |
| icon | CharField | Ícono |
| order | PositiveIntegerField | Orden |

---

### [*] `administration_role_resource`
**Propósito:** Tabla intermedia - Permisos de rol sobre recursos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| role | ForeignKey | FK → role |
| resource | ForeignKey | FK → resource |
| subresource | ForeignKey | FK → subresource |

---

## 2️⃣ MÓDULO: CUSTOMERS

### [*] `customers_customer`
**Propósito:** Perfil de cliente (información adicional del user)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| user | OneToOneField | FK → administration_user |
| phone | CharField | Teléfono |
| address | CharField | Dirección |
| city | CharField | Ciudad |
| country | CharField | País |
| postal_code | CharField | Código postal |
| created_at | DateTimeField | Fecha creación |
| updated_at | DateTimeField | Última actualización |

**Relaciones:**
- `OneToOne` → `administration_user`
- `OneToOne` ← `sales_cart` (Carrito del cliente)
- `OneToMany` ← `sales_address` (Direcciones de envío)
- `OneToMany` ← `sales_order` (Pedidos)

---

## 3️⃣ MÓDULO: CATALOG (Productos)

### [*] `catalog_category`
**Propósito:** Categorías de productos (árbol jerárquico)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField | Nombre categoría |
| parent | ForeignKey | FK → category (self) |
| status | CharField | ACTIVE/INACTIVE |
| created_at | DateTimeField | Fecha creación |

**Relaciones:**
- `ForeignKey` → `catalog_category` (Categoría padre)
- `ManyToMany` ← `catalog_product` (Productos en la categoría)

---

### [*] `catalog_product`
**Propósito:** Productos (entidad base)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| sku | CharField | SKU único |
| name | CharField | Nombre producto |
| description | TextField | Descripción |
| base_price | DecimalField | Precio base |
| brand | CharField | Marca |
| status | CharField | ACTIVE/INACTIVE/ARCHIVED |
| created_at | DateTimeField | Fecha creación |
| updated_at | DateTimeField | Última actualización |

**Relaciones:**
- `ManyToMany` → `catalog_category` (Categorías)
- `OneToMany` ← `catalog_product_variant` (Variantes)
- `OneToMany` ← `catalog_product_image` (Imágenes)

---

### [*] `catalog_product_variant`
**Propósito:** Variantes de producto (color, talla, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| product | ForeignKey | FK → product |
| code | CharField | Código variante |
| price | DecimalField | Precio variante |
| status | CharField | ACTIVE/INACTIVE |
| created_at | DateTimeField | Fecha creación |

**Relaciones:**
- `ForeignKey` → `catalog_product`
- `ManyToMany` → `catalog_attribute_value` (a través de variant_attribute_value)
- `OneToMany` ← `inventory_inventory` (Stock)
- `OneToMany` ← `sales_cart_item` (Items en carrito)
- `OneToMany` ← `sales_order_item` (Items en pedido)

---

### [*] `catalog_attribute`
**Propósito:** Atributos configurables (Color, Talla, Material, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField | Nombre atributo |

---

### [*] `catalog_attribute_value`
**Propósito:** Valores de atributos (Rojo, XL, Algodón, etc.)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| attribute | ForeignKey | FK → attribute |
| value | CharField | Valor |

---

### [*] `catalog_variant_attribute_value`
**Propósito:** Tabla intermedia - Atributos de cada variante

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| variant | ForeignKey | FK → product_variant |
| attribute | ForeignKey | FK → attribute |
| attribute_value | ForeignKey | FK → attribute_value |

---

### [*] `catalog_product_image`
**Propósito:** Imágenes de productos (almacenadas en S3)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| product | ForeignKey | FK → product |
| s3_bucket | CharField | Bucket S3 |
| s3_key | CharField | Key S3 |
| url | CharField | URL directa (alternativa) |
| alt | CharField | Texto alternativo |
| is_main | BooleanField | ¿Es imagen principal? |
| sort | PositiveIntegerField | Orden |
| created_at | DateTimeField | Fecha subida |

---

### [*] `catalog_product_category`
**Propósito:** Tabla intermedia - Productos en categorías

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| product | ForeignKey | FK → product |
| category | ForeignKey | FK → category |

---

## 4️⃣ MÓDULO: INVENTORY

### [*] `inventory_warehouse`
**Propósito:** Almacenes/bodegas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField | Nombre almacén |
| location | CharField | Ubicación |
| code | CharField | Código único |
| is_active | BooleanField | ¿Está activo? |
| created_at | DateTimeField | Fecha creación |

---

### [*] `inventory_inventory`
**Propósito:** Inventario por variante y almacén

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| variant | ForeignKey | FK → product_variant |
| warehouse | ForeignKey | FK → warehouse |
| stock_on_hand | IntegerField | Stock disponible |
| stock_reserved | IntegerField | Stock reservado |
| min_stock | IntegerField | Stock mínimo |
| updated_at | DateTimeField | Última actualización |

**Relaciones:**
- `ForeignKey` → `catalog_product_variant`
- `ForeignKey` → `inventory_warehouse`

---

## 5️⃣ MÓDULO: SALES (Ventas y Carritos)

### [*] `sales_cart`
**Propósito:** Carrito de compras del cliente

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| customer | OneToOneField | FK → customer |
| created_at | DateTimeField | Fecha creación |
| updated_at | DateTimeField | Última actualización |

**Relaciones:**
- `OneToOne` → `customers_customer`
- `OneToMany` ← `sales_cart_item` (Items del carrito)

---

### [*] `sales_cart_item`
**Propósito:** Items dentro del carrito

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| cart | ForeignKey | FK → cart |
| variant | ForeignKey | FK → product_variant |
| qty | PositiveIntegerField | Cantidad |
| unit_price | DecimalField | Precio unitario |
| added_at | DateTimeField | Fecha agregado |

---

### [*] `sales_address`
**Propósito:** Direcciones de envío del cliente

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| customer | ForeignKey | FK → customer |
| line1 | CharField | Dirección |
| city | CharField | Ciudad |
| state | CharField | Departamento |
| zip | CharField | Código postal |
| notes | CharField | Referencia |
| is_default | BooleanField | ¿Es por defecto? |

---

### [*] `sales_order`
**Propósito:** Pedidos/Órdenes de compra

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| customer | ForeignKey | FK → customer |
| order_number | CharField | Número único |
| currency | CharField | Moneda (BOB) |
| status | CharField | CREATED/PAID/PROCESSING/SHIPPED/DELIVERED/CANCELLED |
| subtotal | DecimalField | Subtotal |
| discount_total | DecimalField | Descuento total |
| shipping_total | DecimalField | Costo envío |
| total | DecimalField | Total |
| payment_status | CharField | PENDING/PAID/FAILED/REFUNDED |
| shipping_address | ForeignKey | FK → address |
| notes | TextField | Notas cliente |
| created_at | DateTimeField | Fecha creación |
| updated_at | DateTimeField | Última actualización |

**Relaciones:**
- `ForeignKey` → `customers_customer`
- `ForeignKey` → `sales_address`
- `OneToOne` ← `sales_payment` (Pago)
- `OneToMany` ← `sales_order_item` (Items del pedido)

---

### [*] `sales_order_item`
**Propósito:** Items dentro del pedido

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| order | ForeignKey | FK → order |
| variant | ForeignKey | FK → product_variant |
| qty | PositiveIntegerField | Cantidad |
| unit_price | DecimalField | Precio unitario |
| discount | DecimalField | Descuento |

---

### [*] `sales_payment`
**Propósito:** Pago asociado al pedido

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| order | OneToOneField | FK → order |
| provider | CharField | VPAY/MOCK/QR/STRIPE |
| provider_ref | CharField | ID transacción proveedor |
| status | CharField | INIT/PENDING/SUCCESS/FAILED/CANCELLED |
| amount | DecimalField | Monto |
| idempotency_key | CharField | Clave idempotencia |
| paid_at | DateTimeField | Fecha pago |
| created_at | DateTimeField | Fecha creación |

---

## 6️⃣ MÓDULO: ANALYTICS (Business Intelligence)

### [*] `analytics_sale_fact`
**Propósito:** Tabla de hechos para análisis de ventas (Data Warehouse)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| date | DateField | Fecha venta |
| product_id | IntegerField | ID producto |
| product_name | CharField | Nombre producto |
| category_id | IntegerField | ID categoría |
| category_name | CharField | Nombre categoría |
| variant_id | IntegerField | ID variante |
| variant_code | CharField | Código variante |
| customer_id | IntegerField | ID cliente |
| customer_name | CharField | Nombre cliente |
| qty | IntegerField | Cantidad vendida |
| revenue | DecimalField | Ingreso |
| cost | DecimalField | Costo |
| discount | DecimalField | Descuento |
| order_id | IntegerField | ID pedido |
| created_at | DateTimeField | Timestamp |

---

### [*] `analytics_forecast_model`
**Propósito:** Modelos de machine learning para pronósticos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| name | CharField | Nombre modelo |
| description | TextField | Descripción |
| model_type | CharField | ARIMA/PROPHET/LSTM |
| file_path | CharField | Path del modelo |
| mae | FloatField | Mean Absolute Error |
| rmse | FloatField | Root Mean Squared Error |
| r2_score | FloatField | R² Score |
| training_date_from | DateField | Inicio entrenamiento |
| training_date_to | DateField | Fin entrenamiento |
| features_used | TextField | Features usadas |
| is_active | BooleanField | ¿Está activo? |
| created_at | DateTimeField | Fecha creación |

---

### [*] `analytics_report`
**Propósito:** Reportes generados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BigAutoField | PK |
| report_type | CharField | SALES/INVENTORY/CUSTOMERS |
| title | CharField | Título |
| description | TextField | Descripción |
| format | CharField | PDF/EXCEL/CSV |
| filters | TextField | Filtros aplicados (JSON) |
| generated_by | CharField | Usuario generador |
| file_path | CharField | Path archivo |
| file_size | IntegerField | Tamaño bytes |
| created_at | DateTimeField | Fecha generación |

---

## 🔗 DIAGRAMA DE RELACIONES PRINCIPALES

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO DE VENTA                              │
└─────────────────────────────────────────────────────────────────┘

administration_user (1)
    ↓ OneToOne
customers_customer (1)
    ↓ OneToOne
sales_cart (1)
    ↓ OneToMany
sales_cart_item (N)
    ↓ FK
catalog_product_variant (1)
    ↓ FK
catalog_product (1)
    ↓ ManyToMany
catalog_category (N)


┌─────────────────────────────────────────────────────────────────┐
│                   PROCESO DE CHECKOUT                            │
└─────────────────────────────────────────────────────────────────┘

sales_cart → sales_order (conversión)
    ↓ FK
customers_customer
    ↓ FK
sales_address (shipping)

sales_order (1)
    ↓ OneToOne
sales_payment (1)

sales_order (1)
    ↓ OneToMany
sales_order_item (N)
    ↓ FK
catalog_product_variant (1)


┌─────────────────────────────────────────────────────────────────┐
│                  GESTIÓN DE INVENTARIO                           │
└─────────────────────────────────────────────────────────────────┘

catalog_product_variant (1)
    ↓ OneToMany
inventory_inventory (N)
    ↓ FK
inventory_warehouse (1)


┌─────────────────────────────────────────────────────────────────┐
│                      RBAC (Permisos)                             │
└─────────────────────────────────────────────────────────────────┘

administration_user (1)
    ↓ ManyToMany
auth_group (N)
    ↓ OneToOne
administration_role (1)
    ↓ ManyToMany (via role_resource)
administration_resource (N)
    ↓ OneToMany
administration_subresource (N)
```

---

## ESTADÍSTICAS

| Módulo | Tablas | % del Total |
|--------|--------|-------------|
| Catalog | 8 | 27.6% |
| Sales | 6 | 20.7% |
| Administration | 5 | 17.2% |
| Django Core | 5 | 17.2% |
| Inventory | 2 | 6.9% |
| Analytics | 2 | 6.9% |
| Customers | 1 | 3.4% |
| **TOTAL** | **29** | **100%** |

---

## [*] ÍNDICES Y CONSTRAINTS

### Unique Constraints:
- `administration_user.username` (UNIQUE)
- `administration_user.email` (UNIQUE)
- `catalog_product.sku` (UNIQUE)
- `catalog_product_variant.code` (UNIQUE)
- `sales_order.order_number` (UNIQUE)
- `sales_cart_item` (cart, variant) - UNIQUE TOGETHER
- `inventory_inventory` (variant, warehouse) - UNIQUE TOGETHER

### Foreign Keys con CASCADE:
- `sales_cart_item.cart` → ON DELETE CASCADE
- `sales_order_item.order` → ON DELETE CASCADE
- `catalog_product_variant.product` → ON DELETE CASCADE
- `catalog_product_image.product` → ON DELETE CASCADE

### Foreign Keys con PROTECT:
- `sales_order.customer` → ON DELETE PROTECT
- `sales_order_item.variant` → ON DELETE PROTECT
- `catalog_product_variant.product` → ON DELETE PROTECT

---

## NOTAS IMPORTANTES

1. **S3 Storage:** Las imágenes se almacenan en S3 (bucket: `si2-proyectos`, path: `si2-ecommerce-images/`)

2. **Stock Management:**
   - `stock_on_hand`: Stock disponible para venta
   - `stock_reserved`: Stock reservado en órdenes pendientes
   - Stock real disponible = `stock_on_hand - stock_reserved`

3. **Payment Flow:**
   - MOCK/QR: Confirmación inmediata
   - VPAY: Confirmación diferida (polling cada 3-5s)

4. **Order Status Flow:**
   ```
   CREATED → PAID → PROCESSING → SHIPPED → DELIVERED
              ↓
          CANCELLED
   ```

5. **Payment Status Flow:**
   ```
   INIT → PENDING → SUCCESS
            ↓
         FAILED
            ↓
        CANCELLED
   ```

6. **Analytics:**
   - `sale_fact`: Tabla de hechos desnormalizada para análisis OLAP
   - `forecast_model`: Modelos ML para pronósticos de demanda
   - `report`: Reportes generados con IA (OpenAI GPT-4)


