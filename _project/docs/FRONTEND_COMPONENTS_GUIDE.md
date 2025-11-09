# 🎨 Guía de Componentes Frontend - E-Commerce

**Para equipos de desarrollo Frontend**  
**Base URL API:** `http://127.0.0.1:8000/api/`  
**Documentación API:** `http://127.0.0.1:8000/api/docs/`

---

## 📁 Estructura de Proyecto Recomendada

```
frontend/
├── admin/                    # Panel de administración
│   ├── components/
│   │   ├── common/          # Componentes compartidos admin
│   │   ├── catalog/         # Gestión de productos
│   │   ├── inventory/       # Control de inventario
│   │   ├── sales/           # Gestión de pedidos
│   │   ├── security/        # Usuarios y permisos
│   │   └── analytics/       # Reportes y dashboard
│   ├── pages/
│   ├── services/           # API calls
│   └── utils/
│
└── shopping/               # E-commerce público
    ├── components/
    │   ├── common/         # Header, Footer, Layout
    │   ├── product/        # Catálogo de productos
    │   ├── cart/           # Carrito de compras
    │   ├── checkout/       # Proceso de compra
    │   └── account/        # Perfil de usuario
    ├── pages/
    ├── services/           # API calls
    └── utils/
```

---

## 🔧 **ADMIN PANEL** - Componentes Sugeridos

### 📊 **Dashboard Principal**

#### `DashboardOverview.jsx`
```javascript
// Consume: GET /api/analytics/sales/dashboard/
const DashboardOverview = () => {
  // Métricas principales: ventas, pedidos, productos
  // Gráficos de tendencias
  // KPIs del negocio
}
```

#### `RevenueChart.jsx`
```javascript
// Gráfico de ingresos por período
// Usa Chart.js o Recharts
```

#### `TopProductsWidget.jsx`
```javascript
// Lista de productos más vendidos
// Consume data del dashboard API
```

---

### 📦 **CATALOG - Gestión de Productos**

#### `ProductList.jsx`
```javascript
// Consume: GET /api/catalog/products/
const ProductList = () => {
  // Tabla con paginación
  // Filtros: categoría, precio, estado
  // Búsqueda por nombre
  // Acciones: editar, eliminar, destacar
}
```

#### `ProductForm.jsx`
```javascript
// Consume: POST/PUT /api/catalog/products/
const ProductForm = ({ productId, onSave }) => {
  // Formulario completo de producto
  // Upload de imágenes
  // Gestión de variantes
  // Selección de categoría
  // Atributos dinámicos
}
```

#### `CategoryTree.jsx`
```javascript
// Consume: GET /api/catalog/categories/
const CategoryTree = () => {
  // Árbol jerárquico de categorías
  // Drag & drop para reordenar
  // Edición inline
}
```

#### `VariantManager.jsx`
```javascript
// Gestión de variantes de producto
const VariantManager = ({ productId }) => {
  // Tabla de variantes (Color, Talla, etc.)
  // Precio por variante
  // Códigos únicos
}
```

#### `AttributeManager.jsx`
```javascript
// Consume: GET/POST /api/catalog/attributes/
const AttributeManager = () => {
  // Gestión de atributos (Color, Talla, Material)
  // Valores por atributo
  // Tipos de datos
}
```

---

### 📊 **INVENTORY - Control de Inventario**

#### `InventoryDashboard.jsx`
```javascript
// Consume: GET /api/inventory/inventory/
const InventoryDashboard = () => {
  // Resumen de stock total
  // Alertas de stock bajo
  // Movimientos recientes
}
```

#### `WarehouseList.jsx`
```javascript
// Consume: GET /api/inventory/warehouses/
const WarehouseList = () => {
  // Lista de almacenes
  // Stock total por almacén
  // Estado activo/inactivo
}
```

#### `InventoryTable.jsx`
```javascript
// Tabla principal de inventario
const InventoryTable = () => {
  // Filtros: almacén, producto, stock bajo
  // Columnas: producto, almacén, stock disponible, reservado
  // Acciones: ajustar stock, ver historial
}
```

#### `StockAdjustmentModal.jsx`
```javascript
// Consume: POST /api/inventory/inventory/{id}/adjust_stock/
const StockAdjustmentModal = ({ inventoryId }) => {
  // Modal para ajustar stock
  // Motivo del ajuste
  // Cantidad a agregar/quitar
  // Validación de stock negativo
}
```

#### `LowStockAlert.jsx`
```javascript
// Consume: GET /api/inventory/inventory/?low_stock=true
const LowStockAlert = () => {
  // Componente de alerta
  // Lista productos con stock bajo
  // Link directo para ajustar
}
```

---

### 🛒 **SALES - Gestión de Pedidos**

#### `OrdersList.jsx`
```javascript
// Consume: GET /api/sales/orders/
const OrdersList = () => {
  // Tabla de pedidos con filtros
  // Estados: CREATED, PAID, SHIPPED, etc.
  // Búsqueda por número de orden
  // Acciones: ver detalle, cambiar estado
}
```

#### `OrderDetail.jsx`
```javascript
// Consume: GET /api/sales/orders/{id}/
const OrderDetail = ({ orderId }) => {
  // Información completa del pedido
  // Lista de productos
  // Datos del cliente
  // Historial de estados
  // Información de pago
}
```

#### `OrderStatusManager.jsx`
```javascript
// Gestión de estados de pedido
const OrderStatusManager = ({ orderId, currentStatus }) => {
  // Botones para cambiar estado
  // Validación de transiciones válidas
  // Confirmaciones para acciones críticas
}
```

#### `PaymentConfirmation.jsx`
```javascript
// Consume: POST /api/sales/orders/{id}/confirm_payment/
const PaymentConfirmation = ({ orderId }) => {
  // Modal para confirmar pago
  // Información del proveedor
  // Referencia de transacción
  // Manejo de idempotencia
}
```

#### `CustomerList.jsx`
```javascript
// Consume: GET /api/sales/customers/
const CustomerList = () => {
  // Lista de clientes
  // Búsqueda por nombre, email, CI/NIT
  // Total de pedidos por cliente
  // Última compra
}
```

#### `CustomerDetail.jsx`
```javascript
// Consume: GET /api/sales/customers/{id}/
const CustomerDetail = ({ customerId }) => {
  // Perfil completo del cliente
  // Historial de pedidos
  // Direcciones registradas
  // Estadísticas de compra
}
```

---

### 🔐 **SECURITY - Usuarios y Permisos**

#### `UserList.jsx`
```javascript
// Consume: GET /api/auth/users/
const UserList = () => {
  // Tabla de usuarios del sistema
  // Roles asignados
  // Estado activo/inactivo
  // Última conexión
}
```

#### `UserForm.jsx`
```javascript
// Consume: POST/PUT /api/auth/users/
const UserForm = ({ userId }) => {
  // Formulario de usuario
  // Asignación de rol
  // Datos personales
  // Configuración de acceso
}
```

#### `RoleManager.jsx`
```javascript
// Consume: GET /api/auth/roles/
const RoleManager = () => {
  // Gestión de roles
  // Asignación de permisos
  // Matriz de permisos por recurso
}
```

#### `PermissionMatrix.jsx`
```javascript
// Consume: GET/POST /api/auth/permissions/
const PermissionMatrix = () => {
  // Tabla de permisos
  // Roles vs Recursos
  // Checkboxes: crear, leer, actualizar, eliminar
}
```

---

### 📈 **ANALYTICS - Reportes**

#### `SalesReports.jsx`
```javascript
// Consume: GET /api/analytics/sales/
const SalesReports = () => {
  // Generador de reportes de ventas
  // Filtros por fecha, producto, categoría
  // Exportar: JSON, CSV, PDF, Excel
}
```

#### `SalesChart.jsx`
```javascript
// Consume: GET /api/analytics/sales/dashboard/
const SalesChart = ({ period }) => {
  // Gráfico de ventas por período
  // Line chart con tendencias
  // Comparación períodos anteriores
}
```

#### `ForecastingPanel.jsx`
```javascript
// Consume: GET/POST /api/analytics/forecasts/
const ForecastingPanel = () => {
  // Panel de predicciones
  // Crear modelos de forecast
  // Visualización de predicciones
}
```

---

## 🛍️ **SHOPPING SITE** - Componentes Sugeridos

### 🏠 **Layout y Navegación**

#### `Header.jsx`
```javascript
const Header = () => {
  // Logo y navegación principal
  // Barra de búsqueda
  // Carrito (badge con cantidad)
  // Login/Logout
  // Menú de categorías
}
```

#### `CategoryNavigation.jsx`
```javascript
// Consume: GET /api/catalog/categories/root/
const CategoryNavigation = () => {
  // Menú de categorías
  // Subcategorías en dropdown/mega menu
  // Links a páginas de categoría
}
```

#### `SearchBar.jsx`
```javascript
// Consume: GET /api/catalog/products/?search=
const SearchBar = () => {
  // Búsqueda con autocompletado
  // Sugerencias de productos
  // Filtros rápidos
}
```

---

### 📦 **Catálogo de Productos**

#### `ProductGrid.jsx`
```javascript
// Consume: GET /api/catalog/products/
const ProductGrid = ({ categoryId, filters }) => {
  // Grid responsive de productos
  // Paginación
  // Loading states
  // Product cards
}
```

#### `ProductCard.jsx`
```javascript
const ProductCard = ({ product }) => {
  // Card individual de producto
  // Imagen principal
  // Nombre, precio
  // Badge "Destacado"
  // Botón "Agregar al carrito"
  // Link a detalle
}
```

#### `ProductDetail.jsx`
```javascript
// Consume: GET /api/catalog/products/{id}/
const ProductDetail = ({ productId }) => {
  // Página completa de producto
  // Galería de imágenes
  // Selector de variantes
  // Descripción completa
  // Productos relacionados
  // Reviews (futuro)
}
```

#### `ProductFilters.jsx`
```javascript
const ProductFilters = ({ onFilterChange }) => {
  // Sidebar de filtros
  // Rango de precios
  // Categorías
  // Atributos (Color, Talla, etc.)
  // Limpiar filtros
}
```

#### `VariantSelector.jsx`
```javascript
const VariantSelector = ({ variants, onSelect }) => {
  // Selector de variantes
  // Dropdowns o swatches para color/talla
  // Precio dinámico
  // Stock disponible
}
```

#### `FeaturedProducts.jsx`
```javascript
// Consume: GET /api/catalog/products/?featured=true
const FeaturedProducts = () => {
  // Slider de productos destacados
  // Autoplay con controles
  // Responsive
}
```

---

### 🛒 **Carrito de Compras**

#### `CartIcon.jsx`
```javascript
const CartIcon = () => {
  // Ícono con badge de cantidad
  // Click para abrir dropdown/sidebar
  // Estado del carrito desde context
}
```

#### `CartSidebar.jsx`
```javascript
// Consume: GET /api/sales/carts/{id}/
const CartSidebar = ({ isOpen, onClose }) => {
  // Sidebar deslizable
  // Lista de items del carrito
  // Subtotal
  // Botón "Ir a checkout"
}
```

#### `CartItem.jsx`
```javascript
const CartItem = ({ item, onUpdate, onRemove }) => {
  // Item individual en carrito
  // Imagen del producto
  // Variante seleccionada
  // Cantidad con +/- buttons
  // Precio unitario y total
  // Botón eliminar
}
```

#### `CartPage.jsx`
```javascript
const CartPage = () => {
  // Página completa del carrito
  // Lista detallada de productos
  // Cálculo de totales
  // Cupones de descuento (futuro)
  // Continuar comprando / Checkout
}
```

#### `AddToCartButton.jsx`
```javascript
// Consume: POST /api/sales/carts/{id}/add_item/
const AddToCartButton = ({ productId, variantId, quantity }) => {
  // Botón para agregar al carrito
  // Loading state
  // Feedback visual (toast)
  // Validación de stock
}
```

---

### 💳 **Proceso de Checkout**

#### `CheckoutFlow.jsx`
```javascript
const CheckoutFlow = () => {
  // Wizard de checkout
  // Pasos: Dirección → Pago → Confirmación
  // Navegación entre pasos
  // Validación en cada paso
}
```

#### `ShippingForm.jsx`
```javascript
// Consume: GET/POST /api/sales/addresses/
const ShippingForm = ({ customerId, onNext }) => {
  // Formulario de dirección de envío
  // Direcciones guardadas
  // Agregar nueva dirección
  // Validación de campos
}
```

#### `PaymentForm.jsx`
```javascript
const PaymentForm = ({ onNext }) => {
  // Formulario de pago
  // Métodos: Tarjeta, Transferencia, etc.
  // Integración con pasarela de pago
  // Validación de tarjeta
}
```

#### `OrderSummary.jsx`
```javascript
const OrderSummary = ({ cartItems }) => {
  // Resumen del pedido
  // Lista de productos
  // Subtotal + IVA
  // Costos de envío
  // Total final
}
```

#### `CheckoutConfirmation.jsx`
```javascript
// Consume: POST /api/sales/carts/{id}/checkout/
const CheckoutConfirmation = ({ orderData }) => {
  // Paso final de confirmación
  // Resumen completo
  // Términos y condiciones
  // Botón "Confirmar pedido"
  // Loading durante procesamiento
}
```

#### `OrderSuccess.jsx`
```javascript
const OrderSuccess = ({ orderNumber }) => {
  // Página de éxito
  // Número de pedido
  // Detalles de entrega
  // Link a seguimiento
  // Continuar comprando
}
```

---

### 👤 **Cuenta de Usuario**

#### `LoginForm.jsx`
```javascript
// Consume: POST /api/auth/login/
const LoginForm = ({ onSuccess }) => {
  // Formulario de login
  // Validación de campos
  // Manejo de errores
  // Link a registro
}
```

#### `RegisterForm.jsx`
```javascript
// Consume: POST /api/sales/customers/
const RegisterForm = ({ onSuccess }) => {
  // Formulario de registro
  // Datos personales
  // Validación de email único
  // Términos y condiciones
}
```

#### `UserProfile.jsx`
```javascript
// Consume: GET /api/auth/me/
const UserProfile = () => {
  // Perfil del usuario
  // Datos personales editables
  // Cambio de contraseña
  // Preferencias
}
```

#### `OrderHistory.jsx`
```javascript
// Consume: GET /api/sales/customers/{id}/orders/
const OrderHistory = ({ customerId }) => {
  // Historial de pedidos
  // Lista con estados
  // Filtros por estado/fecha
  // Link a detalle de pedido
}
```

#### `AddressList.jsx`
```javascript
// Consume: GET /api/sales/addresses/?customer={id}
const AddressList = ({ customerId }) => {
  // Lista de direcciones del usuario
  // Dirección por defecto
  // Editar/eliminar direcciones
  // Agregar nueva dirección
}
```

---

## 🔧 **COMPONENTES COMUNES** (Ambos Proyectos)

### 🛠️ **Servicios API**

#### `api.js` (Service Layer)
```javascript
// Configuración base de API
const API_BASE_URL = 'http://127.0.0.1:8000/api';

class ApiService {
  // GET requests con paginación
  async get(endpoint, params = {}) {}
  
  // POST requests
  async post(endpoint, data) {}
  
  // PUT/PATCH requests
  async put(endpoint, data) {}
  
  // DELETE requests
  async delete(endpoint) {}
  
  // Manejo de errores global
  handleError(error) {}
}
```

#### `endpoints.js`
```javascript
// Constantes de endpoints
export const ENDPOINTS = {
  // Catalog
  PRODUCTS: '/catalog/products/',
  CATEGORIES: '/catalog/categories/',
  ATTRIBUTES: '/catalog/attributes/',
  
  // Inventory
  WAREHOUSES: '/inventory/warehouses/',
  INVENTORY: '/inventory/inventory/',
  
  // Sales
  CUSTOMERS: '/sales/customers/',
  CARTS: '/sales/carts/',
  ORDERS: '/sales/orders/',
  
  // Auth
  LOGIN: '/auth/login/',
  USERS: '/auth/users/',
  ROLES: '/auth/roles/',
  
  // Analytics
  SALES_DASHBOARD: '/analytics/sales/dashboard/',
  FORECASTS: '/analytics/forecasts/'
};
```

---

### 🎨 **Componentes UI Reutilizables**

#### `LoadingSpinner.jsx`
```javascript
const LoadingSpinner = ({ size = 'md', overlay = false }) => {
  // Spinner de carga
  // Tamaños: sm, md, lg
  // Overlay para modales
}
```

#### `Pagination.jsx`
```javascript
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  // Componente de paginación
  // Botones anterior/siguiente
  // Números de página
  // Responsive
}
```

#### `Modal.jsx`
```javascript
const Modal = ({ isOpen, onClose, title, children }) => {
  // Modal reutilizable
  // Backdrop con click para cerrar
  // Escape key handler
  // Portal rendering
}
```

#### `Toast.jsx`
```javascript
const Toast = ({ message, type, duration }) => {
  // Notificaciones toast
  // Tipos: success, error, warning, info
  // Auto-dismiss
  // Stack de múltiples toasts
}
```

#### `DataTable.jsx`
```javascript
const DataTable = ({ 
  columns, 
  data, 
  pagination, 
  onSort, 
  onFilter 
}) => {
  // Tabla de datos avanzada
  // Sorting por columnas
  // Filtros integrados
  // Paginación
  // Responsive
}
```

#### `FormField.jsx`
```javascript
const FormField = ({ 
  label, 
  type, 
  error, 
  required, 
  ...props 
}) => {
  // Campo de formulario consistente
  // Validación visual
  // Labels y errores
  // Diferentes tipos
}
```

---

### 🔄 **Hooks Personalizados**

#### `useApi.js`
```javascript
const useApi = (endpoint, options = {}) => {
  // Hook para llamadas API
  // Loading, error, data states
  // Refetch function
  // Cache opcional
}
```

#### `usePagination.js`
```javascript
const usePagination = (apiCall, pageSize = 10) => {
  // Hook para paginación
  // Current page, total pages
  // Next, previous functions
  // Loading states
}
```

#### `useCart.js` (Solo Shopping)
```javascript
const useCart = () => {
  // Hook para carrito de compras
  // Add, remove, update items
  // Cart total calculation
  // Persistent storage
}
```

#### `useAuth.js`
```javascript
const useAuth = () => {
  // Hook para autenticación
  // Current user
  // Login, logout functions
  // Permission checking
}
```

---

## 🎯 **INTEGRACIÓN CON API**

### 📡 **Configuración de API Client**

#### Interceptors Recomendados
```javascript
// Request interceptor
api.interceptors.request.use(config => {
  // Add auth token
  // Add content-type
  // Add X-Requested-With
  return config;
});

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    // Handle 401 -> redirect to login
    // Handle 500 -> show error toast
    // Handle network errors
    return Promise.reject(error);
  }
);
```

### 🔄 **Estado Global Recomendado**

#### Context Providers
```javascript
// AuthContext - Usuario actual, login/logout
// CartContext - Estado del carrito (solo shopping)
// NotificationContext - Toasts y alertas
// ThemeContext - Modo claro/oscuro
```

#### Estado por módulo
```javascript
// Admin: Redux Toolkit o Zustand
// Shopping: Context API + useReducer
```

---

## 🚀 **CARACTERÍSTICAS IMPLEMENTAR**

### ✅ **Funcionalidades Críticas**

1. **Paginación en todas las listas**
   - Usar `?page=` y `?page_size=`
   - Mostrar total de resultados

2. **Búsqueda y filtros**
   - Debounce en búsquedas
   - Filtros combinados
   - Clear filters

3. **Estados de carga**
   - Loading spinners
   - Skeleton screens
   - Error boundaries

4. **Validación de formularios**
   - Client-side validation
   - Server error handling
   - Field-level feedback

5. **Responsive design**
   - Mobile-first approach
   - Breakpoints consistentes
   - Touch-friendly

### ⚡ **Optimizaciones**

1. **Lazy loading de imágenes**
2. **Code splitting por rutas**
3. **Caching de API calls**
4. **Debounce en búsquedas**
5. **Virtual scrolling en listas largas**

---

## 🔐 **Consideraciones de Seguridad**

### 🛡️ **Validación**
- **Client-side**: UX rápida, feedback inmediato
- **Server-side**: Seguridad real (ya implementada en API)
- **Sanitización**: Escape de HTML, validación de inputs

### 🔑 **Autenticación**
- **Desarrollo**: Sessions (actual)
- **Producción**: JWT tokens (pendiente backend)
- **Refresh tokens**: Para sesiones largas
- **Logout**: Limpiar tokens y redirigir

---

## 🎨 **Recomendaciones de UI/UX**

### 📱 **Framework UI Sugerido**
- **Admin**: Ant Design, Material-UI, Chakra UI
- **Shopping**: Tailwind CSS + Headless UI, Mantine

### 🎯 **Patrones de Diseño**
- **Admin**: Dashboard tradicional, tablas densas
- **Shopping**: Cards, grids, mobile-first
- **Consistencia**: Design system común

### 🚦 **Estados de la Aplicación**
- **Loading**: Skeletons mejor que spinners
- **Empty**: Ilustraciones y CTAs claros
- **Error**: Mensajes útiles con acciones
- **Success**: Feedback inmediato

---

## 📊 **Métricas y Monitoring**

### 📈 **Analytics Recomendados**
- **Google Analytics**: Comportamiento de usuarios
- **Hotjar**: Heatmaps y grabaciones
- **Sentry**: Error tracking
- **Performance**: Core Web Vitals

---

## 🔄 **Flujos Críticos a Implementar**

### 🛒 **Flujo de Compra Completo**
1. **Catálogo** → Filtrar productos → Ver detalle
2. **Producto** → Seleccionar variante → Agregar carrito
3. **Carrito** → Revisar items → Ir a checkout
4. **Checkout** → Dirección → Pago → Confirmar
5. **Confirmación** → Mostrar número de orden → Email

### 🔧 **Flujo Admin Pedidos**
1. **Dashboard** → Ver pedidos pendientes
2. **Lista pedidos** → Filtrar por estado
3. **Detalle pedido** → Confirmar pago → Cambiar estado
4. **Actualización** → Notificar cliente (futuro)

---

## 🧪 **Testing Recomendado**

### ✅ **Tipos de Tests**
- **Unit**: Componentes individuales
- **Integration**: Flujos de usuario
- **E2E**: Cypress para flujos críticos
- **API**: Validar integración con backend

### 🎯 **Casos Críticos**
- **Carrito**: Agregar, quitar, modificar cantidad
- **Checkout**: Flujo completo de compra
- **Admin**: Confirmar pagos, gestionar inventario
- **Auth**: Login, logout, permisos

---

## 📞 **Endpoints Críticos por Prioridad**

### 🔥 **Prioridad ALTA (MVP)**
1. `GET /api/catalog/products/` - Catálogo
2. `POST /api/sales/carts/{id}/add_item/` - Agregar carrito  
3. `POST /api/sales/carts/{id}/checkout/` - Crear pedido
4. `POST /api/sales/orders/{id}/confirm_payment/` - Confirmar pago
5. `GET /api/sales/orders/` - Listar pedidos (admin)

### ⭐ **Prioridad MEDIA**
1. `GET /api/analytics/sales/dashboard/` - Dashboard admin
2. `GET /api/inventory/inventory/` - Control inventario
3. `GET /api/auth/users/` - Gestión usuarios
4. `GET /api/sales/customers/` - Gestión clientes

### 💎 **Prioridad BAJA (Futuro)**
1. `GET /api/analytics/forecasts/` - Predicciones
2. `POST /api/analytics/sales/generate_report/` - Reportes
3. `GET /api/auth/permissions/` - Permisos avanzados

---

## 📚 **Recursos Adicionales**

### 🔗 **Links Útiles**
- **API Docs**: http://127.0.0.1:8000/api/docs/
- **API Status**: [API_STATUS_REPORT.md](API_STATUS_REPORT.md)
- **Documentación Completa**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Referencia Rápida**: [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)

### 📦 **Dependencias Recomendadas**

#### **React/Next.js**
```json
{
  "axios": "^1.6.0",
  "react-query": "^3.39.0",
  "react-hook-form": "^7.47.0",
  "react-router-dom": "^6.17.0",
  "zustand": "^4.4.0"
}
```

#### **Vue/Nuxt**
```json
{
  "axios": "^1.6.0",
  "@tanstack/vue-query": "^5.0.0",
  "vee-validate": "^4.11.0",
  "vue-router": "^4.2.0",
  "pinia": "^2.1.0"
}
```

#### **Angular**
```json
{
  "@angular/common/http": "^17.0.0",
  "@ngrx/store": "^17.0.0",
  "rxjs": "^7.8.0",
  "@angular/forms": "^17.0.0"
}
```

---

**🚀 ¡Con esta guía tendrás todos los componentes necesarios para consumir el backend de manera eficiente!**

**📞 Para dudas específicas, consulta la documentación API o el Swagger UI.**