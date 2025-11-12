# 🎨 Guía para Desarrolladores Frontend

**Backend E-Commerce API** - Información para Angular/React/Vue  
**Versión:** 2.0 (JWT + AI Reports)  
**Fecha:** 9 de Noviembre, 2025

---

## 📋 Tabla de Contenidos

1. [Configuración Base](#configuración-base)
2. [Autenticación JWT](#autenticación-jwt)
3. [Estructura de Respuestas](#estructura-de-respuestas)
4. [Módulos y Endpoints](#módulos-y-endpoints)
5. [Componentes Sugeridos](#componentes-sugeridos)
6. [Servicios Recomendados](#servicios-recomendados)
7. [Guards y Interceptors](#guards-y-interceptors)
8. [Manejo de Errores](#manejo-de-errores)
9. [Ejemplos de Código](#ejemplos-de-código)

---

## 📡 Configuración Base

### Información del Servidor

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://127.0.0.1:8000',
  apiPrefix: '/api',
  
  // JWT Config
  tokenKey: 'access_token',
  refreshTokenKey: 'refresh_token',
  tokenExpiry: 3600, // 1 hora en segundos
  
  // Credenciales de prueba
  testUser: {
    username: 'admin',
    password: 'admin123'
  }
};
```

### URLs Completas

```
Base URL:     http://127.0.0.1:8000
API Prefix:   /api
Swagger UI:   http://127.0.0.1:8000/api/docs/
Healthcheck:  http://127.0.0.1:8000/api/healthz/
```

---

## 🔐 Autenticación JWT

### 1️⃣ Flujo de Login

```typescript
// auth.service.ts
interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access: string;  // Válido por 1 hora
  refresh: string; // Válido por 7 días
}

login(credentials: LoginRequest): Observable<LoginResponse> {
  return this.http.post<LoginResponse>(
    `${this.apiUrl}/api/auth/token/`,
    credentials
  ).pipe(
    tap(response => {
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
    })
  );
}
```

### 2️⃣ Refresh Token

```typescript
refreshToken(): Observable<LoginResponse> {
  const refreshToken = localStorage.getItem('refresh_token');
  
  return this.http.post<LoginResponse>(
    `${this.apiUrl}/api/auth/token/refresh/`,
    { refresh: refreshToken }
  ).pipe(
    tap(response => {
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
    })
  );
}
```

### 3️⃣ Interceptor JWT

```typescript
// jwt.interceptor.ts
export class JwtInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }
    
    return next.handle(request).pipe(
      catchError(error => {
        if (error.status === 401) {
          // Token expirado - intentar refresh
          return this.authService.refreshToken().pipe(
            switchMap(() => {
              const newToken = localStorage.getItem('access_token');
              request = request.clone({
                setHeaders: { Authorization: `Bearer ${newToken}` }
              });
              return next.handle(request);
            }),
            catchError(refreshError => {
              // Refresh falló - logout
              this.authService.logout();
              this.router.navigate(['/login']);
              return throwError(refreshError);
            })
          );
        }
        return throwError(error);
      })
    );
  }
}
```

### 4️⃣ Auth Guard

```typescript
// auth.guard.ts
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    if (this.authService.isAuthenticated()) {
      return true;
    }
    
    this.router.navigate(['/login']);
    return false;
  }
}

// auth.service.ts
isAuthenticated(): boolean {
  const token = localStorage.getItem('access_token');
  if (!token) return false;
  
  // Verificar expiración (opcional)
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp > Date.now() / 1000;
  } catch {
    return false;
  }
}
```

### 5️⃣ Logout

```typescript
logout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  this.router.navigate(['/login']);
}
```

---

## 📦 Estructura de Respuestas

### Respuesta Estándar

```typescript
interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  meta?: {
    timestamp?: string;
    [key: string]: any;
  };
}
```

### Respuesta Paginada

```typescript
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

### Respuesta de Error

```typescript
interface ErrorResponse {
  detail?: string;
  success?: boolean;
  message?: string;
  errors?: Record<string, string[]>;
}
```

---

## 🏗️ Módulos y Endpoints

### 1. Catálogo (Público)

```typescript
// catalog.service.ts
interface Product {
  id: number;
  name: string;
  description: string;
  base_price: number;
  categories: Category[];
  variants: ProductVariant[];
  images: ProductImage[];
  is_featured: boolean;
  status: 'ACTIVE' | 'INACTIVE';
}

interface Category {
  id: number;
  name: string;
  parent: number | null;
  children: Category[];
  status: 'ACTIVE' | 'INACTIVE';
}

// Endpoints
getProducts(filters?: ProductFilters): Observable<PaginatedResponse<Product>> {
  return this.http.get<PaginatedResponse<Product>>(`${this.apiUrl}/api/catalog/products/`, {
    params: { ...filters }
  });
}

getCategories(): Observable<PaginatedResponse<Category>> {
  return this.http.get<PaginatedResponse<Category>>(`${this.apiUrl}/api/catalog/categories/`);
}

getProductById(id: number): Observable<Product> {
  return this.http.get<Product>(`${this.apiUrl}/api/catalog/products/${id}/`);
}
```

**Filtros disponibles:**
- `category` - ID de categoría
- `search` - Búsqueda por nombre
- `min_price` - Precio mínimo
- `max_price` - Precio máximo
- `featured` - true/false
- `page` - Número de página
- `page_size` - Elementos por página

### 2. Carrito y Compras

```typescript
// cart.service.ts
interface Cart {
  id: number;
  items: CartItem[];
  subtotal: number;
  tax: number;
  total_amount: number;
  created_at: string;
}

interface CartItem {
  id: number;
  variant: ProductVariant;
  quantity: number;
  price: number;
  subtotal: number;
}

// Endpoints
getCart(cartId: number): Observable<Cart> {
  return this.http.get<Cart>(`${this.apiUrl}/api/sales/carts/${cartId}/`);
}

addToCart(cartId: number, variantId: number, quantity: number): Observable<Cart> {
  return this.http.post<Cart>(
    `${this.apiUrl}/api/sales/carts/${cartId}/add_item/`,
    { variant_id: variantId, quantity }
  );
}

checkout(cartId: number, checkoutData: CheckoutRequest): Observable<Order> {
  return this.http.post<Order>(
    `${this.apiUrl}/api/sales/carts/${cartId}/checkout/`,
    checkoutData
  );
}
```

### 3. Pedidos

```typescript
// order.service.ts
interface Order {
  id: number;
  order_number: string;
  customer: Customer;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  total: number;
  status: OrderStatus;
  shipping_address: Address;
  created_at: string;
  updated_at: string;
}

type OrderStatus = 'CREATED' | 'PAID' | 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';

// Endpoints
getOrders(filters?: OrderFilters): Observable<PaginatedResponse<Order>> {
  return this.http.get<PaginatedResponse<Order>>(`${this.apiUrl}/api/sales/orders/`, {
    params: { ...filters }
  });
}

getOrderById(id: number): Observable<Order> {
  return this.http.get<Order>(`${this.apiUrl}/api/sales/orders/${id}/`);
}

confirmPayment(orderId: number, paymentData: PaymentRequest): Observable<ApiResponse<any>> {
  return this.http.post<ApiResponse<any>>(
    `${this.apiUrl}/api/sales/orders/${orderId}/confirm_payment/`,
    paymentData
  );
}
```

### 4. Reportes con IA (NUEVO)

```typescript
// ai-report.service.ts
interface AIReportRequest {
  query: string;           // Consulta en lenguaje natural
  format: 'json' | 'csv' | 'excel' | 'pdf';
  limit?: number;          // Límite de resultados (default: 100)
  dry_run?: boolean;       // Solo generar SQL sin ejecutar
}

interface AIReportResponse {
  success: boolean;
  message: string;
  data: {
    sql: string;
    columns: string[];
    rows: any[][];
    interpretation: string;  // Explicación en lenguaje natural
    summary: {
      total_rows: number;
      execution_time_ms: number;
    };
    export_options: string[];
  };
}

// Endpoints
generateReport(request: AIReportRequest): Observable<AIReportResponse | Blob> {
  if (request.format === 'json') {
    return this.http.post<AIReportResponse>(
      `${this.apiUrl}/api/analytics/reports/ai-report/`,
      request
    );
  } else {
    // Para CSV, Excel, PDF
    return this.http.post(
      `${this.apiUrl}/api/analytics/reports/ai-report/`,
      request,
      { responseType: 'blob' }
    );
  }
}

// Ejemplo de uso
this.aiReportService.generateReport({
  query: 'Muéstrame las ventas de los últimos 30 días',
  format: 'json',
  limit: 100
}).subscribe(response => {
  console.log('SQL generado:', response.data.sql);
  console.log('Interpretación:', response.data.interpretation);
  console.log('Datos:', response.data.rows);
});
```

### 5. Analytics Dashboard

```typescript
// analytics.service.ts
interface DashboardStats {
  period: string;
  total_revenue: number;
  total_orders: number;
  avg_order_value: number;
  total_customers: number;
  revenue_by_date: Array<{ date: string; revenue: number }>;
  top_products: Array<{ product: string; quantity: number; revenue: number }>;
  top_categories: Array<{ category: string; revenue: number }>;
}

getDashboard(days: number = 30): Observable<DashboardStats> {
  return this.http.get<DashboardStats>(
    `${this.apiUrl}/api/analytics/sales/dashboard/`,
    { params: { days: days.toString() } }
  );
}
```

---

## 🎨 Componentes Sugeridos

### Estructura de Carpetas

```
src/app/
├── core/
│   ├── guards/
│   │   └── auth.guard.ts
│   ├── interceptors/
│   │   └── jwt.interceptor.ts
│   ├── services/
│   │   ├── auth.service.ts
│   │   └── api.service.ts
│   └── models/
│       ├── user.model.ts
│       ├── product.model.ts
│       └── order.model.ts
├── features/
│   ├── auth/
│   │   ├── login/
│   │   │   ├── login.component.ts
│   │   │   ├── login.component.html
│   │   │   └── login.component.scss
│   │   └── register/
│   │       └── register.component.ts
│   ├── catalog/
│   │   ├── product-list/
│   │   │   └── product-list.component.ts
│   │   ├── product-detail/
│   │   │   └── product-detail.component.ts
│   │   └── category-filter/
│   │       └── category-filter.component.ts
│   ├── cart/
│   │   ├── cart-view/
│   │   │   └── cart-view.component.ts
│   │   ├── cart-item/
│   │   │   └── cart-item.component.ts
│   │   └── checkout/
│   │       └── checkout.component.ts
│   ├── orders/
│   │   ├── order-list/
│   │   │   └── order-list.component.ts
│   │   └── order-detail/
│   │   │   └── order-detail.component.ts
│   ├── analytics/
│   │   ├── dashboard/
│   │   │   └── dashboard.component.ts
│   │   └── ai-reports/
│   │       ├── report-generator/
│   │       │   └── report-generator.component.ts
│   │       └── report-viewer/
│   │           └── report-viewer.component.ts
│   └── admin/
│       ├── inventory/
│       ├── users/
│       └── roles/
└── shared/
    ├── components/
    │   ├── navbar/
    │   ├── sidebar/
    │   ├── loading-spinner/
    │   └── error-message/
    └── pipes/
        ├── currency.pipe.ts
        └── date-format.pipe.ts
```

### Componentes Clave

#### 1. LoginComponent
```typescript
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  loginForm = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required]
  });

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.value).subscribe({
        next: () => this.router.navigate(['/dashboard']),
        error: (err) => console.error('Login failed', err)
      });
    }
  }
}
```

#### 2. ProductListComponent
```typescript
@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html'
})
export class ProductListComponent implements OnInit {
  products$: Observable<PaginatedResponse<Product>>;
  filters: ProductFilters = {};

  constructor(private catalogService: CatalogService) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.products$ = this.catalogService.getProducts(this.filters);
  }

  onFilterChange(filters: ProductFilters): void {
    this.filters = filters;
    this.loadProducts();
  }

  addToCart(product: Product, variantId: number): void {
    const cartId = localStorage.getItem('cart_id');
    this.cartService.addToCart(+cartId, variantId, 1).subscribe({
      next: () => alert('Producto agregado al carrito'),
      error: (err) => console.error('Error', err)
    });
  }
}
```

#### 3. AIReportGeneratorComponent (NUEVO)
```typescript
@Component({
  selector: 'app-ai-report-generator',
  templateUrl: './report-generator.component.html'
})
export class AIReportGeneratorComponent {
  reportForm = this.fb.group({
    query: ['', Validators.required],
    format: ['json'],
    limit: [100]
  });

  reportResult: AIReportResponse | null = null;
  isLoading = false;

  formatOptions = [
    { value: 'json', label: 'JSON (con interpretación)' },
    { value: 'csv', label: 'CSV' },
    { value: 'excel', label: 'Excel' },
    { value: 'pdf', label: 'PDF' }
  ];

  exampleQueries = [
    'Muéstrame las ventas de los últimos 30 días',
    'Top 10 productos más vendidos',
    'Total de ingresos por categoría',
    'Clientes con más compras este mes'
  ];

  constructor(
    private fb: FormBuilder,
    private aiReportService: AIReportService
  ) {}

  generateReport(): void {
    if (this.reportForm.valid) {
      this.isLoading = true;
      const request = this.reportForm.value as AIReportRequest;

      if (request.format === 'json') {
        this.aiReportService.generateReport(request).subscribe({
          next: (response: AIReportResponse) => {
            this.reportResult = response;
            this.isLoading = false;
          },
          error: (err) => {
            console.error('Error generando reporte', err);
            this.isLoading = false;
          }
        });
      } else {
        // Descarga archivo
        this.aiReportService.generateReport(request).subscribe({
          next: (blob: Blob) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte.${request.format}`;
            a.click();
            this.isLoading = false;
          },
          error: (err) => {
            console.error('Error descargando reporte', err);
            this.isLoading = false;
          }
        });
      }
    }
  }

  useExampleQuery(query: string): void {
    this.reportForm.patchValue({ query });
  }
}
```

---

## 🛡️ Manejo de Errores

```typescript
// error-handler.service.ts
@Injectable()
export class ErrorHandlerService {
  handleError(error: HttpErrorResponse): string {
    let errorMessage = 'Ha ocurrido un error';

    if (error.error instanceof ErrorEvent) {
      // Error del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del servidor
      switch (error.status) {
        case 400:
          errorMessage = 'Solicitud inválida';
          break;
        case 401:
          errorMessage = 'No autorizado - Por favor inicia sesión';
          break;
        case 403:
          errorMessage = 'Acceso denegado';
          break;
        case 404:
          errorMessage = 'Recurso no encontrado';
          break;
        case 500:
          errorMessage = 'Error interno del servidor';
          break;
        default:
          errorMessage = error.error?.message || error.message;
      }
    }

    return errorMessage;
  }
}
```

---

## 📝 Ejemplos de Código Completos

### Servicio de Autenticación Completo

```typescript
// auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadCurrentUser();
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/api/auth/token/`,
      credentials
    ).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        this.loadCurrentUser();
      })
    );
  }

  refreshToken(): Observable<LoginResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/api/auth/token/refresh/`,
      { refresh: refreshToken }
    ).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/api/auth/me/`);
  }

  private loadCurrentUser(): void {
    if (this.isAuthenticated()) {
      this.getCurrentUser().subscribe({
        next: (user) => this.currentUserSubject.next(user),
        error: () => this.logout()
      });
    }
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch {
      return false;
    }
  }
}
```

---

## 📊 Endpoints Resumidos

### Públicos (No requieren JWT)
- `POST /api/auth/token/` - Login
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/register/` - Registro
- `GET /api/catalog/*` - Catálogo completo
- `GET /api/healthz/` - Healthcheck

### Protegidos (Requieren JWT)
- `GET /api/auth/me/` - Usuario actual
- `POST /api/auth/logout/` - Logout
- `GET /api/sales/orders/` - Pedidos
- `POST /api/sales/carts/{id}/checkout/` - Checkout
- `GET /api/analytics/sales/dashboard/` - Dashboard
- `POST /api/analytics/reports/ai-report/` - Reportes IA (NUEVO)
- `GET /api/inventory/*` - Inventario
- `GET /api/auth/users/` - Gestión usuarios

---

## ✅ Checklist de Implementación

### Fase 1: Setup Inicial
- [ ] Configurar environment con apiUrl
- [ ] Crear AuthService con login/logout
- [ ] Implementar JwtInterceptor
- [ ] Crear AuthGuard
- [ ] Componente de Login

### Fase 2: Catálogo
- [ ] Servicio de Catálogo
- [ ] Listado de productos
- [ ] Detalle de producto
- [ ] Filtros de búsqueda
- [ ] Categorías

### Fase 3: Carrito y Compras
- [ ] Servicio de Carrito
- [ ] Vista de carrito
- [ ] Agregar/Quitar items
- [ ] Proceso de checkout
- [ ] Confirmación de pedido

### Fase 4: Pedidos
- [ ] Servicio de Pedidos
- [ ] Listado de pedidos
- [ ] Detalle de pedido
- [ ] Estados de pedido

### Fase 5: Analytics (Opcional)
- [ ] Dashboard de estadísticas
- [ ] Gráficos de ventas
- [ ] Generador de reportes IA
- [ ] Exportación de datos

---

## 🚀 Para Empezar Rápido

```bash
# 1. Verificar backend corriendo
curl http://127.0.0.1:8000/api/healthz/

# 2. Probar login
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. Ver catálogo (público)
curl http://127.0.0.1:8000/api/catalog/products/

# 4. Explorar Swagger
# Abrir: http://127.0.0.1:8000/api/docs/
```

---

**Credenciales de Prueba:**
```
Username: admin
Password: admin123
```

**¿Dudas?** Consulta la documentación completa en `API_DOCUMENTATION.md` o `API_QUICK_REFERENCE.md`
