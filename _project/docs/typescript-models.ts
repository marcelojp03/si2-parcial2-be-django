/**
 * Modelos TypeScript para E-Commerce Backend API
 * Versión: 2.0 (JWT + AI Reports)
 * Fecha: 9 de Noviembre, 2025
 * 
 * Copiar este archivo a: src/app/core/models/
 */

// ============================================================================
// AUTENTICACIÓN
// ============================================================================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;  // JWT access token (1 hora)
  refresh: string; // JWT refresh token (7 días)
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  avatar: string;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  role_name: string | null;
}

// ============================================================================
// RESPUESTAS API
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  meta?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ErrorResponse {
  detail?: string;
  success?: boolean;
  message?: string;
  errors?: Record<string, string[]>;
}

// ============================================================================
// CATÁLOGO
// ============================================================================

export type CategoryStatus = 'ACTIVE' | 'INACTIVE';

export interface Category {
  id: number;
  name: string;
  parent: number | null;
  children: Category[];
  status: CategoryStatus;
  created_at: string;
}

export interface Attribute {
  id: number;
  name: string;
  code: string;
  type: 'TEXT' | 'NUMBER' | 'BOOLEAN' | 'SELECT';
  values: AttributeValue[];
}

export interface AttributeValue {
  id: number;
  attribute: number;
  value: string;
}

export type ProductStatus = 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';

export interface Product {
  id: number;
  name: string;
  description: string;
  base_price: number;
  categories: Category[];
  variants: ProductVariant[];
  images: ProductImage[];
  is_featured: boolean;
  status: ProductStatus;
  created_at: string;
  updated_at: string;
}

export interface ProductVariant {
  id: number;
  product: number;
  code: string;
  sku: string;
  price: number;
  stock: number;
  attributes: VariantAttribute[];
}

export interface VariantAttribute {
  attribute_name: string;
  attribute_value: string;
}

export interface ProductImage {
  id: number;
  image: string;
  is_primary: boolean;
  order: number;
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

// ============================================================================
// VENTAS
// ============================================================================

export interface Customer {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  ci_nit: string;
  full_name: string;
}

export interface Address {
  id: number;
  customer: number;
  street: string;
  number: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  is_default: boolean;
}

export interface Cart {
  id: number;
  items: CartItem[];
  subtotal: number;
  tax: number;
  total_amount: number;
  created_at: string;
  updated_at: string;
}

export interface CartItem {
  id: number;
  variant: ProductVariant;
  quantity: number;
  price: number;
  subtotal: number;
}

export interface AddToCartRequest {
  variant_id: number;
  quantity: number;
}

export type OrderStatus = 
  | 'CREATED' 
  | 'PAID' 
  | 'PROCESSING' 
  | 'SHIPPED' 
  | 'DELIVERED' 
  | 'CANCELLED';

export interface Order {
  id: number;
  order_number: string;
  customer: Customer;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  total: number;
  status: OrderStatus;
  shipping_address: Address;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id: number;
  variant: ProductVariant;
  quantity: number;
  price: number;
  subtotal: number;
}

export interface CheckoutRequest {
  customer_id: number;
  shipping_address_id: number;
  payment_method: string;
  payment_provider: string;
  notes?: string;
}

export interface PaymentRequest {
  idempotency_key: string;
  payment_method: string;
  amount: number;
  provider_ref?: string;
}

export interface OrderFilters {
  customer?: number;
  status?: OrderStatus;
  search?: string;
  page?: number;
  page_size?: number;
}

// ============================================================================
// INVENTARIO
// ============================================================================

export interface Warehouse {
  id: number;
  code: string;
  name: string;
  location: string;
  is_active: boolean;
}

export interface Inventory {
  id: number;
  warehouse: Warehouse;
  variant: ProductVariant;
  stock_on_hand: number;
  stock_reserved: number;
  stock_available: number;
  min_stock: number;
  max_stock: number;
  reorder_point: number;
}

export interface StockAdjustment {
  quantity: number;
  reason?: string;
}

// ============================================================================
// ANALYTICS
// ============================================================================

export interface SaleFact {
  id: number;
  date: string;
  order_id: number;
  customer_id: number;
  product_id: number;
  category_id: number;
  warehouse_id: number;
  product_name: string;
  category_name: string;
  qty: number;
  unit_price: number;
  discount: number;
  tax: number;
  revenue: number;
}

export interface DashboardStats {
  period: string;
  total_revenue: number;
  total_orders: number;
  avg_order_value: number;
  total_customers: number;
  revenue_by_date: RevenueByDate[];
  top_products: TopProduct[];
  top_categories: TopCategory[];
}

export interface RevenueByDate {
  date: string;
  revenue: number;
}

export interface TopProduct {
  product: string;
  quantity: number;
  revenue: number;
}

export interface TopCategory {
  category: string;
  revenue: number;
}

// ============================================================================
// REPORTES CON IA (NUEVO)
// ============================================================================

export type ReportFormat = 'json' | 'csv' | 'excel' | 'pdf';

export interface AIReportRequest {
  query: string;           // Consulta en lenguaje natural
  format: ReportFormat;    // Formato de salida
  limit?: number;          // Límite de resultados (default: 100)
  dry_run?: boolean;       // Solo generar SQL sin ejecutar
}

export interface AIReportResponse {
  success: boolean;
  message: string;
  data: {
    sql: string;
    columns: string[];
    rows: any[][];
    interpretation: string;
    summary: {
      total_rows: number;
      execution_time_ms: number;
    };
    export_options: ReportFormat[];
  };
}

export interface AIReportDryRunResponse {
  success: boolean;
  message: string;
  data: {
    sql: string;
  };
}

// ============================================================================
// EJEMPLOS DE QUERIES PARA AI REPORTS
// ============================================================================

export const AI_REPORT_EXAMPLES = [
  'Muéstrame las ventas de los últimos 30 días',
  'Top 10 productos más vendidos',
  'Total de ingresos por categoría',
  'Clientes con más compras este mes',
  'Productos con stock bajo de 10 unidades',
  'Ventas por día de la última semana',
  'Categorías más rentables',
  'Promedio de valor de pedido por mes'
];

// ============================================================================
// GUARDS Y ROUTING
// ============================================================================

export interface MenuItem {
  id: number;
  name: string;
  path: string;
  icon: string;
  order: number;
  parent: MenuItem | null;
  children: MenuItem[];
}

// ============================================================================
// UTILIDADES
// ============================================================================

export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp < Date.now() / 1000;
  } catch {
    return true;
  }
}

export function getTokenPayload(token: string): any {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-BO', {
    style: 'currency',
    currency: 'BOB'
  }).format(amount);
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('es-BO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}
