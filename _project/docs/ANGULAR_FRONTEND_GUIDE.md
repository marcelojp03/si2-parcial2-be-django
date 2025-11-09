# 🎯 Guía Angular - E-Commerce Frontend

**Framework:** Angular 17+  
**Base URL API:** `http://127.0.0.1:8000/api/`  
**Documentación API:** `http://127.0.0.1:8000/api/docs/`

---

## 📁 Estructura de Proyecto Angular

```
frontend/
├── admin/                          # Aplicación Admin
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/              # Servicios singleton
│   │   │   │   ├── services/      # API Services
│   │   │   │   ├── guards/        # Route Guards
│   │   │   │   ├── interceptors/  # HTTP Interceptors
│   │   │   │   └── models/        # TypeScript interfaces
│   │   │   ├── shared/            # Componentes compartidos
│   │   │   │   ├── components/    # UI Components reutilizables
│   │   │   │   ├── pipes/         # Custom Pipes
│   │   │   │   └── directives/    # Custom Directives
│   │   │   ├── features/          # Módulos de funcionalidad
│   │   │   │   ├── dashboard/     # Dashboard principal
│   │   │   │   ├── catalog/       # Gestión productos
│   │   │   │   ├── inventory/     # Control inventario
│   │   │   │   ├── sales/         # Gestión pedidos
│   │   │   │   ├── security/      # Usuarios y permisos
│   │   │   │   └── analytics/     # Reportes y analytics
│   │   │   └── layout/            # Layout components
│   │   └── environments/
│
└── shopping/                       # Aplicación Shopping
    ├── src/
    │   ├── app/
    │   │   ├── core/              # Servicios singleton
    │   │   ├── shared/            # Componentes compartidos
    │   │   ├── features/          # Módulos de funcionalidad
    │   │   │   ├── catalog/       # Catálogo público
    │   │   │   ├── cart/          # Carrito de compras
    │   │   │   ├── checkout/      # Proceso de compra
    │   │   │   ├── account/       # Perfil usuario
    │   │   │   └── orders/        # Historial pedidos
    │   │   └── layout/            # Layout components
    │   └── environments/
```

---

## 🏗️ **CONFIGURACIÓN BASE**

### 📦 **package.json recomendado**
```json
{
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/router": "^17.0.0",
    "@angular/material": "^17.0.0",
    "@ngrx/store": "^17.0.0",
    "@ngrx/effects": "^17.0.0",
    "rxjs": "^7.8.0",
    "chart.js": "^4.4.0",
    "ng2-charts": "^5.0.0",
    "ngx-pagination": "^6.0.3",
    "ngx-toastr": "^18.0.0"
  }
}
```

### 🔧 **environment.ts**
```typescript
export const environment = {
  production: false,
  apiBaseUrl: 'http://127.0.0.1:8000/api',
  appTitle: 'E-Commerce Admin',
  itemsPerPage: 10
};
```

---

## 🔗 **CORE SERVICES**

### 🌐 **HttpClient Service**
```typescript
// core/services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  get<T>(endpoint: string, params?: any): Observable<T> {
    const httpParams = this.buildParams(params);
    return this.http.get<T>(`${this.apiUrl}${endpoint}`, { params: httpParams })
      .pipe(catchError(this.handleError));
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.apiUrl}${endpoint}`, data)
      .pipe(catchError(this.handleError));
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(`${this.apiUrl}${endpoint}`, data)
      .pipe(catchError(this.handleError));
  }

  patch<T>(endpoint: string, data: any): Observable<T> {
    return this.http.patch<T>(`${this.apiUrl}${endpoint}`, data)
      .pipe(catchError(this.handleError));
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.apiUrl}${endpoint}`)
      .pipe(catchError(this.handleError));
  }

  private buildParams(params: any): HttpParams {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return httpParams;
  }

  private handleError(error: any) {
    console.error('API Error:', error);
    return throwError(() => error);
  }
}
```

### 🔐 **Auth Service**
```typescript
// core/services/auth.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from './api.service';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_name?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private apiService: ApiService) {
    this.checkCurrentUser();
  }

  login(credentials: LoginRequest): Observable<User> {
    return this.apiService.post<{user: User, message: string}>('/auth/login/', credentials)
      .pipe(
        map(response => {
          this.currentUserSubject.next(response.user);
          return response.user;
        })
      );
  }

  logout(): Observable<any> {
    return this.apiService.post('/auth/logout/', {})
      .pipe(
        map(() => {
          this.currentUserSubject.next(null);
        })
      );
  }

  getCurrentUser(): Observable<User> {
    return this.apiService.get<User>('/auth/me/');
  }

  getUserMenu(): Observable<any> {
    return this.apiService.get<any>('/auth/menu/');
  }

  private checkCurrentUser(): void {
    this.getCurrentUser().subscribe({
      next: (user) => this.currentUserSubject.next(user),
      error: () => this.currentUserSubject.next(null)
    });
  }

  get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  get isAuthenticated(): boolean {
    return !!this.currentUserValue;
  }
}
```

---

## 📦 **CATALOG MODULE** (Admin)

### 🏷️ **Product Models**
```typescript
// features/catalog/models/product.model.ts
export interface Category {
  id: number;
  name: string;
  description?: string;
  parent?: number;
  children?: Category[];
}

export interface Attribute {
  id: number;
  name: string;
  data_type: 'TEXT' | 'NUMBER' | 'BOOLEAN' | 'DATE';
}

export interface AttributeValue {
  id: number;
  attribute: number;
  value: string;
}

export interface ProductVariant {
  id: number;
  code: string;
  price: number;
  attributes: Array<{
    name: string;
    value: string;
  }>;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  category: Category;
  status: 'ACTIVE' | 'INACTIVE' | 'DRAFT';
  is_featured: boolean;
  variants: ProductVariant[];
  images: Array<{
    id: number;
    image: string;
    alt_text: string;
  }>;
}

export interface ProductFilters {
  category?: number;
  search?: string;
  min_price?: number;
  max_price?: number;
  featured?: boolean;
  page?: number;
  page_size?: number;
}
```

### 🛍️ **Product Service**
```typescript
// features/catalog/services/product.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService, ApiResponse } from '../../../core/services/api.service';
import { Product, Category, ProductFilters } from '../models/product.model';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  constructor(private apiService: ApiService) {}

  getProducts(filters?: ProductFilters): Observable<ApiResponse<Product>> {
    return this.apiService.get<ApiResponse<Product>>('/catalog/products/', filters);
  }

  getProduct(id: number): Observable<Product> {
    return this.apiService.get<Product>(`/catalog/products/${id}/`);
  }

  createProduct(product: Partial<Product>): Observable<Product> {
    return this.apiService.post<Product>('/catalog/products/', product);
  }

  updateProduct(id: number, product: Partial<Product>): Observable<Product> {
    return this.apiService.put<Product>(`/catalog/products/${id}/`, product);
  }

  deleteProduct(id: number): Observable<any> {
    return this.apiService.delete(`/catalog/products/${id}/`);
  }

  getCategories(): Observable<ApiResponse<Category>> {
    return this.apiService.get<ApiResponse<Category>>('/catalog/categories/');
  }

  getRootCategories(): Observable<Category[]> {
    return this.apiService.get<Category[]>('/catalog/categories/root/');
  }

  getFeaturedProducts(): Observable<Product[]> {
    return this.apiService.get<Product[]>('/catalog/products/featured/');
  }
}
```

### 📋 **Product List Component**
```typescript
// features/catalog/components/product-list/product-list.component.ts
import { Component, OnInit } from '@angular/core';
import { Observable, BehaviorSubject, combineLatest } from 'rxjs';
import { map, startWith, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { FormControl } from '@angular/forms';
import { ProductService } from '../../services/product.service';
import { Product, Category, ProductFilters } from '../../models/product.model';

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.scss']
})
export class ProductListComponent implements OnInit {
  products$ = new BehaviorSubject<Product[]>([]);
  categories$: Observable<Category[]>;
  loading = false;
  
  // Filtros
  searchControl = new FormControl('');
  categoryControl = new FormControl('');
  featuredControl = new FormControl(false);
  
  // Paginación
  currentPage = 1;
  totalItems = 0;
  pageSize = 10;

  displayedColumns: string[] = [
    'id', 'name', 'category', 'status', 'is_featured', 'actions'
  ];

  constructor(private productService: ProductService) {}

  ngOnInit(): void {
    this.categories$ = this.productService.getRootCategories();
    this.setupFilters();
    this.loadProducts();
  }

  private setupFilters(): void {
    // Combinar todos los filtros y aplicar debounce
    combineLatest([
      this.searchControl.valueChanges.pipe(
        startWith(''),
        debounceTime(300),
        distinctUntilChanged()
      ),
      this.categoryControl.valueChanges.pipe(startWith('')),
      this.featuredControl.valueChanges.pipe(startWith(false))
    ]).subscribe(() => {
      this.currentPage = 1;
      this.loadProducts();
    });
  }

  loadProducts(): void {
    this.loading = true;
    
    const filters: ProductFilters = {
      page: this.currentPage,
      page_size: this.pageSize
    };

    // Aplicar filtros
    if (this.searchControl.value?.trim()) {
      filters.search = this.searchControl.value.trim();
    }
    
    if (this.categoryControl.value) {
      filters.category = +this.categoryControl.value;
    }
    
    if (this.featuredControl.value) {
      filters.featured = true;
    }

    this.productService.getProducts(filters).subscribe({
      next: (response) => {
        this.products$.next(response.results);
        this.totalItems = response.count;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.loading = false;
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadProducts();
  }

  onEdit(product: Product): void {
    // Navigate to edit form
  }

  onDelete(product: Product): void {
    if (confirm(`¿Eliminar producto "${product.name}"?`)) {
      this.productService.deleteProduct(product.id).subscribe({
        next: () => {
          this.loadProducts();
        },
        error: (error) => console.error('Error deleting product:', error)
      });
    }
  }

  clearFilters(): void {
    this.searchControl.setValue('');
    this.categoryControl.setValue('');
    this.featuredControl.setValue(false);
  }
}
```

### 📝 **Product Form Component**
```typescript
// features/catalog/components/product-form/product-form.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { Product, Category } from '../../models/product.model';

@Component({
  selector: 'app-product-form',
  templateUrl: './product-form.component.html',
  styleUrls: ['./product-form.component.scss']
})
export class ProductFormComponent implements OnInit {
  productForm: FormGroup;
  categories: Category[] = [];
  isEdit = false;
  productId?: number;
  loading = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private productService: ProductService
  ) {
    this.productForm = this.createForm();
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.isEdit = true;
        this.productId = +params['id'];
        this.loadProduct();
      }
    });

    this.loadCategories();
  }

  private createForm(): FormGroup {
    return this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(100)]],
      description: [''],
      category: ['', Validators.required],
      status: ['ACTIVE', Validators.required],
      is_featured: [false],
      variants: this.fb.array([])
    });
  }

  get variants(): FormArray {
    return this.productForm.get('variants') as FormArray;
  }

  addVariant(): void {
    const variantGroup = this.fb.group({
      code: ['', Validators.required],
      price: [0, [Validators.required, Validators.min(0)]],
      attributes: this.fb.array([])
    });
    
    this.variants.push(variantGroup);
  }

  removeVariant(index: number): void {
    this.variants.removeAt(index);
  }

  private loadCategories(): void {
    this.productService.getRootCategories().subscribe({
      next: (categories) => this.categories = categories,
      error: (error) => console.error('Error loading categories:', error)
    });
  }

  private loadProduct(): void {
    if (this.productId) {
      this.productService.getProduct(this.productId).subscribe({
        next: (product) => {
          this.productForm.patchValue({
            name: product.name,
            description: product.description,
            category: product.category.id,
            status: product.status,
            is_featured: product.is_featured
          });
          
          // Load variants
          this.loadVariants(product.variants);
        },
        error: (error) => console.error('Error loading product:', error)
      });
    }
  }

  private loadVariants(variants: any[]): void {
    this.variants.clear();
    variants.forEach(variant => {
      const variantGroup = this.fb.group({
        code: [variant.code],
        price: [variant.price],
        attributes: this.fb.array([])
      });
      this.variants.push(variantGroup);
    });
  }

  onSubmit(): void {
    if (this.productForm.valid) {
      this.loading = true;
      const formData = this.productForm.value;

      const request = this.isEdit 
        ? this.productService.updateProduct(this.productId!, formData)
        : this.productService.createProduct(formData);

      request.subscribe({
        next: (product) => {
          this.router.navigate(['/admin/catalog/products']);
        },
        error: (error) => {
          console.error('Error saving product:', error);
          this.loading = false;
        }
      });
    }
  }

  onCancel(): void {
    this.router.navigate(['/admin/catalog/products']);
  }
}
```

---

## 🛒 **SALES MODULE** (Admin)

### 📋 **Order Models**
```typescript
// features/sales/models/order.model.ts
export interface Customer {
  id: number;
  full_name: string;
  email: string;
  phone?: string;
  ci_nit?: string;
}

export interface OrderItem {
  id: number;
  variant: {
    id: number;
    code: string;
    product_name: string;
  };
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: number;
  order_number: string;
  customer: Customer;
  status: 'CREATED' | 'PAID' | 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
  payment_status: 'PENDING' | 'PAID' | 'FAILED' | 'REFUNDED';
  items: OrderItem[];
  subtotal: number;
  total: number;
  created_at: string;
  updated_at: string;
  notes?: string;
}

export interface OrderFilters {
  customer?: number;
  status?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface PaymentConfirmation {
  idempotency_key: string;
  provider: string;
  provider_ref: string;
}
```

### 🛍️ **Order Service**
```typescript
// features/sales/services/order.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService, ApiResponse } from '../../../core/services/api.service';
import { Order, OrderFilters, PaymentConfirmation } from '../models/order.model';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  constructor(private apiService: ApiService) {}

  getOrders(filters?: OrderFilters): Observable<ApiResponse<Order>> {
    return this.apiService.get<ApiResponse<Order>>('/sales/orders/', filters);
  }

  getOrder(id: number): Observable<Order> {
    return this.apiService.get<Order>(`/sales/orders/${id}/`);
  }

  confirmPayment(orderId: number, payment: PaymentConfirmation): Observable<any> {
    return this.apiService.post(`/sales/orders/${orderId}/confirm_payment/`, payment);
  }

  cancelOrder(orderId: number): Observable<any> {
    return this.apiService.post(`/sales/orders/${orderId}/cancel/`, {});
  }

  getOrderStatuses(): string[] {
    return ['CREATED', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'];
  }
}
```

### 📋 **Order List Component**
```typescript
// features/sales/components/order-list/order-list.component.ts
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { BehaviorSubject, combineLatest } from 'rxjs';
import { startWith, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { OrderService } from '../../services/order.service';
import { Order, OrderFilters } from '../../models/order.model';

@Component({
  selector: 'app-order-list',
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.scss']
})
export class OrderListComponent implements OnInit {
  orders$ = new BehaviorSubject<Order[]>([]);
  loading = false;

  // Filtros
  searchControl = new FormControl('');
  statusControl = new FormControl('');
  
  // Paginación
  currentPage = 1;
  totalItems = 0;
  pageSize = 10;

  statusOptions: string[] = [];
  
  displayedColumns: string[] = [
    'order_number', 'customer', 'status', 'payment_status', 
    'total', 'created_at', 'actions'
  ];

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.statusOptions = this.orderService.getOrderStatuses();
    this.setupFilters();
    this.loadOrders();
  }

  private setupFilters(): void {
    combineLatest([
      this.searchControl.valueChanges.pipe(
        startWith(''),
        debounceTime(300),
        distinctUntilChanged()
      ),
      this.statusControl.valueChanges.pipe(startWith(''))
    ]).subscribe(() => {
      this.currentPage = 1;
      this.loadOrders();
    });
  }

  loadOrders(): void {
    this.loading = true;
    
    const filters: OrderFilters = {
      page: this.currentPage,
      page_size: this.pageSize
    };

    if (this.searchControl.value?.trim()) {
      filters.search = this.searchControl.value.trim();
    }
    
    if (this.statusControl.value) {
      filters.status = this.statusControl.value;
    }

    this.orderService.getOrders(filters).subscribe({
      next: (response) => {
        this.orders$.next(response.results);
        this.totalItems = response.count;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading orders:', error);
        this.loading = false;
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadOrders();
  }

  onViewDetail(order: Order): void {
    // Navigate to order detail
  }

  getStatusColor(status: string): string {
    const colors: {[key: string]: string} = {
      'CREATED': 'warn',
      'PAID': 'primary',
      'PROCESSING': 'accent',
      'SHIPPED': 'primary',
      'DELIVERED': 'primary',
      'CANCELLED': 'warn'
    };
    return colors[status] || 'primary';
  }
}
```

### 📄 **Order Detail Component**
```typescript
// features/sales/components/order-detail/order-detail.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { OrderService } from '../../services/order.service';
import { Order } from '../../models/order.model';

@Component({
  selector: 'app-order-detail',
  templateUrl: './order-detail.component.html',
  styleUrls: ['./order-detail.component.scss']
})
export class OrderDetailComponent implements OnInit {
  order?: Order;
  loading = false;
  
  paymentForm: FormGroup;

  constructor(
    private route: ActivatedRoute,
    private orderService: OrderService,
    private fb: FormBuilder,
    private dialog: MatDialog
  ) {
    this.paymentForm = this.fb.group({
      provider: ['MOCK', Validators.required],
      provider_ref: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.params['id'];
    this.loadOrder(+id);
  }

  loadOrder(id: number): void {
    this.loading = true;
    this.orderService.getOrder(id).subscribe({
      next: (order) => {
        this.order = order;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading order:', error);
        this.loading = false;
      }
    });
  }

  confirmPayment(): void {
    if (this.order && this.paymentForm.valid) {
      const payment = {
        idempotency_key: this.generateIdempotencyKey(),
        ...this.paymentForm.value
      };

      this.orderService.confirmPayment(this.order.id, payment).subscribe({
        next: () => {
          this.loadOrder(this.order!.id);
        },
        error: (error) => console.error('Error confirming payment:', error)
      });
    }
  }

  cancelOrder(): void {
    if (this.order && confirm('¿Confirma la cancelación del pedido?')) {
      this.orderService.cancelOrder(this.order.id).subscribe({
        next: () => {
          this.loadOrder(this.order!.id);
        },
        error: (error) => console.error('Error canceling order:', error)
      });
    }
  }

  private generateIdempotencyKey(): string {
    return `payment_${this.order?.id}_${Date.now()}`;
  }

  canConfirmPayment(): boolean {
    return this.order?.status === 'CREATED' && this.order?.payment_status === 'PENDING';
  }

  canCancelOrder(): boolean {
    return this.order?.status === 'CREATED' || this.order?.status === 'PAID';
  }
}
```

---

## 📊 **ANALYTICS MODULE**

### 📈 **Dashboard Service**
```typescript
// features/analytics/services/analytics.service.ts
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';

export interface DashboardMetrics {
  period: string;
  metrics: {
    total_revenue: number;
    total_orders: number;
    avg_order_value: number;
  };
  daily_sales: Array<{
    date: string;
    revenue: number;
    orders: number;
  }>;
  top_products: Array<{
    product_name: string;
    quantity_sold: number;
    revenue: number;
  }>;
  top_categories: Array<{
    category_name: string;
    quantity_sold: number;
    revenue: number;
  }>;
}

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  constructor(private apiService: ApiService) {}

  getDashboard(days: number = 30): Observable<DashboardMetrics> {
    return this.apiService.get<DashboardMetrics>('/analytics/sales/dashboard/', { days });
  }

  generateReport(params: any): Observable<any> {
    return this.apiService.post('/analytics/sales/generate_report/', params);
  }
}
```

### 📊 **Dashboard Component**
```typescript
// features/analytics/components/dashboard/dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { AnalyticsService, DashboardMetrics } from '../../services/analytics.service';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  dashboardData?: DashboardMetrics;
  loading = false;
  
  periodControl = new FormControl(30);
  
  // Configuración de gráficos
  lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: [
      {
        data: [],
        label: 'Ventas Diarias',
        fill: true,
        tension: 0.5,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)'
      }
    ]
  };
  
  lineChartOptions: ChartOptions<'line'> = {
    responsive: true
  };
  
  pieChartData: ChartConfiguration<'pie'>['data'] = {
    labels: [],
    datasets: [{
      data: []
    }]
  };

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    this.periodControl.valueChanges.subscribe(days => {
      this.loadDashboard(days || 30);
    });
    
    this.loadDashboard(30);
  }

  loadDashboard(days: number): void {
    this.loading = true;
    this.analyticsService.getDashboard(days).subscribe({
      next: (data) => {
        this.dashboardData = data;
        this.updateCharts();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading dashboard:', error);
        this.loading = false;
      }
    });
  }

  private updateCharts(): void {
    if (this.dashboardData) {
      // Line Chart - Ventas diarias
      this.lineChartData.labels = this.dashboardData.daily_sales.map(item => item.date);
      this.lineChartData.datasets[0].data = this.dashboardData.daily_sales.map(item => item.revenue);
      
      // Pie Chart - Top categorías
      this.pieChartData.labels = this.dashboardData.top_categories.map(item => item.category_name);
      this.pieChartData.datasets[0].data = this.dashboardData.top_categories.map(item => item.revenue);
    }
  }
}
```

---

## 🛍️ **SHOPPING SITE COMPONENTS**

### 🏠 **Product Catalog Component**
```typescript
// shopping/features/catalog/components/product-catalog/product-catalog.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormControl } from '@angular/forms';
import { BehaviorSubject, combineLatest } from 'rxjs';
import { startWith, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { ProductService } from '../../services/product.service';
import { Product, Category, ProductFilters } from '../../models/product.model';

@Component({
  selector: 'app-product-catalog',
  templateUrl: './product-catalog.component.html',
  styleUrls: ['./product-catalog.component.scss']
})
export class ProductCatalogComponent implements OnInit {
  products$ = new BehaviorSubject<Product[]>([]);
  categories: Category[] = [];
  loading = false;

  // Filtros
  searchControl = new FormControl('');
  categoryControl = new FormControl('');
  minPriceControl = new FormControl(null);
  maxPriceControl = new FormControl(null);
  sortControl = new FormControl('name');

  // Paginación
  currentPage = 1;
  totalItems = 0;
  pageSize = 12;

  // Vista
  viewMode: 'grid' | 'list' = 'grid';

  constructor(
    private productService: ProductService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.setupFilters();
    this.handleRouteParams();
  }

  private handleRouteParams(): void {
    this.route.queryParams.subscribe(params => {
      if (params['category']) {
        this.categoryControl.setValue(params['category']);
      }
      if (params['search']) {
        this.searchControl.setValue(params['search']);
      }
      this.loadProducts();
    });
  }

  private setupFilters(): void {
    combineLatest([
      this.searchControl.valueChanges.pipe(
        startWith(''),
        debounceTime(300),
        distinctUntilChanged()
      ),
      this.categoryControl.valueChanges.pipe(startWith('')),
      this.minPriceControl.valueChanges.pipe(startWith(null)),
      this.maxPriceControl.valueChanges.pipe(startWith(null)),
      this.sortControl.valueChanges.pipe(startWith('name'))
    ]).subscribe(() => {
      this.currentPage = 1;
      this.loadProducts();
    });
  }

  loadProducts(): void {
    this.loading = true;
    
    const filters: ProductFilters = {
      page: this.currentPage,
      page_size: this.pageSize
    };

    // Aplicar filtros
    if (this.searchControl.value?.trim()) {
      filters.search = this.searchControl.value.trim();
    }
    
    if (this.categoryControl.value) {
      filters.category = +this.categoryControl.value;
    }
    
    if (this.minPriceControl.value) {
      filters.min_price = this.minPriceControl.value;
    }
    
    if (this.maxPriceControl.value) {
      filters.max_price = this.maxPriceControl.value;
    }

    this.productService.getProducts(filters).subscribe({
      next: (response) => {
        this.products$.next(response.results);
        this.totalItems = response.count;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.loading = false;
      }
    });
  }

  private loadCategories(): void {
    this.productService.getRootCategories().subscribe({
      next: (categories) => this.categories = categories,
      error: (error) => console.error('Error loading categories:', error)
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadProducts();
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
  }

  clearFilters(): void {
    this.searchControl.setValue('');
    this.categoryControl.setValue('');
    this.minPriceControl.setValue(null);
    this.maxPriceControl.setValue(null);
  }
}
```

### 🛒 **Cart Service**
```typescript
// shopping/features/cart/services/cart.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';

export interface CartItem {
  id: number;
  variant: {
    id: number;
    code: string;
    product_name: string;
    price: number;
  };
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total_items: number;
  total_amount: number;
}

@Injectable({
  providedIn: 'root'
})
export class CartService {
  private cartSubject = new BehaviorSubject<Cart | null>(null);
  public cart$ = this.cartSubject.asObservable();

  constructor(private apiService: ApiService) {
    this.loadCart();
  }

  loadCart(): void {
    // Asumir cart ID = 1 para demo
    this.apiService.get<Cart>('/sales/carts/1/').subscribe({
      next: (cart) => this.cartSubject.next(cart),
      error: () => this.cartSubject.next(null)
    });
  }

  addItem(variantId: number, quantity: number = 1): Observable<Cart> {
    return this.apiService.post<Cart>('/sales/carts/1/add_item/', {
      variant_id: variantId,
      quantity
    }).pipe(
      map(cart => {
        this.cartSubject.next(cart);
        return cart;
      })
    );
  }

  removeItem(itemId: number): Observable<any> {
    return this.apiService.post(`/sales/carts/1/remove_item/${itemId}/`, {})
      .pipe(
        map(() => this.loadCart())
      );
  }

  clearCart(): Observable<any> {
    return this.apiService.post('/sales/carts/1/clear/', {})
      .pipe(
        map(() => this.loadCart())
      );
  }

  get cartItemCount(): number {
    return this.cartSubject.value?.total_items || 0;
  }

  get cartTotal(): number {
    return this.cartSubject.value?.total_amount || 0;
  }
}
```

---

## 🔧 **SHARED COMPONENTS**

### 📄 **Pagination Component**
```typescript
// shared/components/pagination/pagination.component.ts
import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-pagination',
  template: `
    <mat-paginator
      [length]="totalItems"
      [pageSize]="pageSize"
      [pageIndex]="currentPage - 1"
      [pageSizeOptions]="pageSizeOptions"
      (page)="onPageChange($event)"
      showFirstLastButtons>
    </mat-paginator>
  `
})
export class PaginationComponent {
  @Input() currentPage = 1;
  @Input() totalItems = 0;
  @Input() pageSize = 10;
  @Input() pageSizeOptions = [5, 10, 25, 50];
  
  @Output() pageChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();

  onPageChange(event: any): void {
    this.pageChange.emit(event.pageIndex + 1);
    if (event.pageSize !== this.pageSize) {
      this.pageSizeChange.emit(event.pageSize);
    }
  }
}
```

### ⚠️ **Error Handling Interceptor**
```typescript
// core/interceptors/error.interceptor.ts
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpErrorResponse } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  
  constructor(
    private router: Router,
    private toastr: ToastrService
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler) {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        switch (error.status) {
          case 401:
            this.router.navigate(['/login']);
            this.toastr.error('Sesión expirada. Inicia sesión nuevamente.');
            break;
          case 403:
            this.toastr.error('No tienes permisos para realizar esta acción.');
            break;
          case 404:
            this.toastr.error('Recurso no encontrado.');
            break;
          case 500:
            this.toastr.error('Error interno del servidor. Inténtalo más tarde.');
            break;
          default:
            this.toastr.error('Ha ocurrido un error inesperado.');
        }
        
        return throwError(() => error);
      })
    );
  }
}
```

---

## 🚦 **ROUTING**

### 🗺️ **Admin Routes**
```typescript
// admin/app-routing.module.ts
const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadChildren: () => import('./features/analytics/analytics.module').then(m => m.AnalyticsModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'catalog',
    loadChildren: () => import('./features/catalog/catalog.module').then(m => m.CatalogModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'sales',
    loadChildren: () => import('./features/sales/sales.module').then(m => m.SalesModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'inventory',
    loadChildren: () => import('./features/inventory/inventory.module').then(m => m.InventoryModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'security',
    loadChildren: () => import('./features/security/security.module').then(m => m.SecurityModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'login',
    component: LoginComponent
  }
];
```

### 🏪 **Shopping Routes**
```typescript
// shopping/app-routing.module.ts
const routes: Routes = [
  { path: '', redirectTo: '/catalog', pathMatch: 'full' },
  {
    path: 'catalog',
    loadChildren: () => import('./features/catalog/catalog.module').then(m => m.CatalogModule)
  },
  {
    path: 'product/:id',
    component: ProductDetailComponent
  },
  {
    path: 'cart',
    component: CartComponent
  },
  {
    path: 'checkout',
    loadChildren: () => import('./features/checkout/checkout.module').then(m => m.CheckoutModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'account',
    loadChildren: () => import('./features/account/account.module').then(m => m.AccountModule),
    canActivate: [AuthGuard]
  }
];
```

---

## 🛡️ **AUTH GUARD**

```typescript
// core/guards/auth.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): Observable<boolean> {
    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (user) {
          return true;
        } else {
          this.router.navigate(['/login']);
          return false;
        }
      })
    );
  }
}
```

---

## 🎨 **MATERIAL DESIGN CONFIGURATION**

```typescript
// shared/material.module.ts
import { NgModule } from '@angular/core';
import {
  MatButtonModule,
  MatCardModule,
  MatTableModule,
  MatPaginatorModule,
  MatFormFieldModule,
  MatInputModule,
  MatSelectModule,
  MatCheckboxModule,
  MatIconModule,
  MatToolbarModule,
  MatSidenavModule,
  MatListModule,
  MatGridListModule,
  MatChipsModule,
  MatProgressSpinnerModule,
  MatSnackBarModule,
  MatDialogModule,
  MatTabsModule
} from '@angular/material';

@NgModule({
  exports: [
    MatButtonModule,
    MatCardModule,
    MatTableModule,
    MatPaginatorModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatIconModule,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatGridListModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatTabsModule
  ]
})
export class MaterialModule {}
```

---

## 🚀 **COMANDOS DE DESARROLLO**

```bash
# Crear aplicaciones Angular separadas
ng new admin --routing --style=scss
ng new shopping --routing --style=scss

# Generar módulos de funcionalidad
ng generate module features/catalog --routing
ng generate module features/sales --routing
ng generate module features/inventory --routing

# Generar componentes
ng generate component features/catalog/components/product-list
ng generate component features/catalog/components/product-form

# Generar servicios
ng generate service core/services/api
ng generate service features/catalog/services/product

# Generar guards
ng generate guard core/guards/auth

# Ejecutar en desarrollo
ng serve --port 4200  # Admin
ng serve --port 4201  # Shopping
```

---

## 🎯 **PRÓXIMOS PASOS**

### ✅ **Implementación Prioritaria**
1. **Setup inicial**: Angular CLI, Material Design, NgRx
2. **Core services**: API, Auth, Error handling
3. **Admin MVP**: Dashboard, productos, pedidos
4. **Shopping MVP**: Catálogo, carrito, checkout
5. **Testing**: Unit tests con Jasmine/Karma

### 🚀 **Mejoras Futuras**
1. **PWA**: Service Workers, offline support
2. **i18n**: Internacionalización
3. **Lazy loading**: Optimización de bundles
4. **SSR**: Angular Universal para SEO
5. **E2E**: Cypress o Protractor

---

**🎉 ¡Con esta guía tienes todo lo necesario para desarrollar ambas aplicaciones Angular consumiendo tu backend de manera eficiente!**