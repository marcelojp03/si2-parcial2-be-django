# 🛒 Servicio de Carrito con LocalStorage

## Descripción

Sistema de carrito que funciona para usuarios **autenticados** y **no autenticados**:

- **Usuario NO autenticado**: Carrito en `localStorage` (temporal)
- **Usuario autenticado**: Carrito en el backend (persistente)
- **Al hacer login**: Sincroniza automáticamente el carrito temporal con el backend

---

## 📁 Estructura de Archivos

```
src/
├── services/
│   └── cartService.js          # Servicio principal del carrito
├── utils/
│   └── api.js                  # Cliente HTTP (fetch/axios)
└── components/
    └── Cart/
        ├── CartButton.jsx      # Botón del carrito con contador
        └── CartDrawer.jsx      # Panel lateral del carrito
```

---

## 🔧 Implementación

### 1. **API Client** (`utils/api.js`)

```javascript
// utils/api.js
const API_BASE_URL = 'http://127.0.0.1:8000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getHeaders(includeAuth = false) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = localStorage.getItem('accessToken');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(options.auth),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Request failed');
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Métodos de conveniencia
  get(endpoint, auth = false) {
    return this.request(endpoint, { method: 'GET', auth });
  }

  post(endpoint, data, auth = false) {
    return this.request(endpoint, {
      method: 'POST',
      auth,
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data, auth = false) {
    return this.request(endpoint, {
      method: 'PUT',
      auth,
      body: JSON.stringify(data),
    });
  }

  delete(endpoint, auth = false) {
    return this.request(endpoint, { method: 'DELETE', auth });
  }
}

export const api = new ApiClient();
```

---

### 2. **Cart Service** (`services/cartService.js`)

```javascript
// services/cartService.js
import { api } from '../utils/api';

class CartService {
  constructor() {
    this.GUEST_CART_KEY = 'guestCart';
    this.CART_ID_KEY = 'cartId';
  }

  // ============================================
  // HELPERS
  // ============================================

  isAuthenticated() {
    return !!localStorage.getItem('accessToken');
  }

  getCartId() {
    return localStorage.getItem(this.CART_ID_KEY);
  }

  setCartId(cartId) {
    localStorage.setItem(this.CART_ID_KEY, cartId);
  }

  clearCartId() {
    localStorage.removeItem(this.CART_ID_KEY);
  }

  // ============================================
  // CARRITO DE INVITADO (LocalStorage)
  // ============================================

  getGuestCart() {
    const cart = localStorage.getItem(this.GUEST_CART_KEY);
    return cart ? JSON.parse(cart) : [];
  }

  saveGuestCart(cart) {
    localStorage.setItem(this.GUEST_CART_KEY, JSON.stringify(cart));
  }

  clearGuestCart() {
    localStorage.removeItem(this.GUEST_CART_KEY);
  }

  addToGuestCart(variantId, quantity = 1, product = null) {
    const cart = this.getGuestCart();
    const existingItem = cart.find(item => item.variant_id === variantId);

    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      cart.push({
        variant_id: variantId,
        quantity,
        // Información adicional para mostrar en el UI
        product: product ? {
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image,
        } : null,
        added_at: new Date().toISOString(),
      });
    }

    this.saveGuestCart(cart);
    return cart;
  }

  removeFromGuestCart(variantId) {
    let cart = this.getGuestCart();
    cart = cart.filter(item => item.variant_id !== variantId);
    this.saveGuestCart(cart);
    return cart;
  }

  updateGuestCartQuantity(variantId, quantity) {
    const cart = this.getGuestCart();
    const item = cart.find(item => item.variant_id === variantId);

    if (item) {
      if (quantity <= 0) {
        return this.removeFromGuestCart(variantId);
      }
      item.quantity = quantity;
      this.saveGuestCart(cart);
    }

    return cart;
  }

  getGuestCartCount() {
    const cart = this.getGuestCart();
    return cart.reduce((total, item) => total + item.quantity, 0);
  }

  // ============================================
  // CARRITO DEL BACKEND (Usuario autenticado)
  // ============================================

  async getBackendCart() {
    const cartId = this.getCartId();
    if (!cartId) {
      throw new Error('No cart ID found. User must be authenticated.');
    }

    return await api.get(`/sales/carts/${cartId}/`);
  }

  async addToBackendCart(variantId, quantity = 1) {
    const cartId = this.getCartId();
    if (!cartId) {
      throw new Error('No cart ID found. User must be authenticated.');
    }

    return await api.post(`/sales/carts/${cartId}/add_item/`, {
      variant_id: variantId,
      quantity,
    });
  }

  async removeFromBackendCart(itemId) {
    const cartId = this.getCartId();
    if (!cartId) {
      throw new Error('No cart ID found.');
    }

    return await api.post(`/sales/carts/${cartId}/remove-item/${itemId}/`);
  }

  async updateBackendCartItem(itemId, quantity) {
    if (quantity <= 0) {
      return await this.removeFromBackendCart(itemId);
    }

    return await api.put(`/sales/cart-items/${itemId}/`, { quantity });
  }

  async clearBackendCart() {
    const cartId = this.getCartId();
    if (!cartId) {
      throw new Error('No cart ID found.');
    }

    return await api.post(`/sales/carts/${cartId}/clear/`);
  }

  async getBackendCartCount() {
    try {
      const cart = await this.getBackendCart();
      return cart.total_items || 0;
    } catch (error) {
      console.error('Error getting cart count:', error);
      return 0;
    }
  }

  // ============================================
  // API UNIFICADA (Auto-detecta guest vs authenticated)
  // ============================================

  /**
   * Agrega un producto al carrito (guest o backend según autenticación)
   */
  async addToCart(variantId, quantity = 1, product = null) {
    if (this.isAuthenticated()) {
      return await this.addToBackendCart(variantId, quantity);
    } else {
      return this.addToGuestCart(variantId, quantity, product);
    }
  }

  /**
   * Obtiene el carrito actual (guest o backend)
   */
  async getCart() {
    if (this.isAuthenticated()) {
      return await this.getBackendCart();
    } else {
      return {
        items: this.getGuestCart(),
        total_items: this.getGuestCartCount(),
        is_guest: true,
      };
    }
  }

  /**
   * Obtiene el contador de items en el carrito
   */
  async getCartCount() {
    if (this.isAuthenticated()) {
      return await this.getBackendCartCount();
    } else {
      return this.getGuestCartCount();
    }
  }

  /**
   * Elimina un item del carrito
   */
  async removeItem(itemId, variantId = null) {
    if (this.isAuthenticated()) {
      return await this.removeFromBackendCart(itemId);
    } else {
      // Para guest cart, usamos variantId
      return this.removeFromGuestCart(variantId);
    }
  }

  /**
   * Actualiza la cantidad de un item
   */
  async updateQuantity(itemId, quantity, variantId = null) {
    if (this.isAuthenticated()) {
      return await this.updateBackendCartItem(itemId, quantity);
    } else {
      return this.updateGuestCartQuantity(variantId, quantity);
    }
  }

  /**
   * Vacía el carrito
   */
  async clearCart() {
    if (this.isAuthenticated()) {
      return await this.clearBackendCart();
    } else {
      this.clearGuestCart();
      return { items: [], total_items: 0 };
    }
  }

  // ============================================
  // SINCRONIZACIÓN (Guest → Backend)
  // ============================================

  /**
   * Sincroniza el carrito de invitado con el backend después del login
   */
  async syncGuestCartToBackend() {
    const guestCart = this.getGuestCart();
    
    if (guestCart.length === 0) {
      console.log('No guest cart items to sync');
      return;
    }

    const cartId = this.getCartId();
    if (!cartId) {
      throw new Error('No cart ID found after login');
    }

    console.log(`Syncing ${guestCart.length} items from guest cart to backend...`);

    try {
      // Transferir cada item al backend
      for (const item of guestCart) {
        await api.post(`/sales/carts/${cartId}/add_item/`, {
          variant_id: item.variant_id,
          quantity: item.quantity,
        });
      }

      // Limpiar el carrito de invitado después de sincronizar
      this.clearGuestCart();
      console.log('✅ Guest cart synced successfully');
      
      // Retornar el carrito actualizado del backend
      return await this.getBackendCart();
    } catch (error) {
      console.error('❌ Error syncing guest cart:', error);
      throw error;
    }
  }

  /**
   * Maneja el login del usuario (guarda cart_id y sincroniza)
   */
  async handleLogin(loginResponse) {
    const { cart_id, tokens } = loginResponse;

    // Guardar tokens
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);

    // Guardar cart_id
    this.setCartId(cart_id);

    // Sincronizar carrito de invitado
    await this.syncGuestCartToBackend();

    return await this.getBackendCart();
  }

  /**
   * Maneja el logout del usuario
   */
  handleLogout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    this.clearCartId();
    // Opcionalmente, puedes mantener el guest cart o limpiarlo
    // this.clearGuestCart();
  }

  // ============================================
  // CHECKOUT
  // ============================================

  /**
   * Crear orden desde el carrito (solo usuarios autenticados)
   */
  async checkout(checkoutData) {
    if (!this.isAuthenticated()) {
      throw new Error('User must be authenticated to checkout');
    }

    const cartId = this.getCartId();
    if (!cartId) {
      throw new Error('No cart ID found');
    }

    // checkoutData: { customer_id, shipping_address_id, payment_method, payment_provider, notes }
    return await api.post(`/sales/carts/${cartId}/checkout/`, checkoutData, true);
  }
}

// Exportar instancia única (Singleton)
export const cartService = new CartService();
```

---

## 📱 Componentes React (Ejemplos)

### 3. **Cart Button** (`components/Cart/CartButton.jsx`)

```jsx
// components/Cart/CartButton.jsx
import React, { useState, useEffect } from 'react';
import { cartService } from '../../services/cartService';

export const CartButton = ({ onClick }) => {
  const [itemCount, setItemCount] = useState(0);

  useEffect(() => {
    loadCartCount();

    // Escuchar eventos de actualización del carrito
    window.addEventListener('cartUpdated', loadCartCount);
    
    return () => {
      window.removeEventListener('cartUpdated', loadCartCount);
    };
  }, []);

  const loadCartCount = async () => {
    try {
      const count = await cartService.getCartCount();
      setItemCount(count);
    } catch (error) {
      console.error('Error loading cart count:', error);
    }
  };

  return (
    <button 
      onClick={onClick}
      className="cart-button"
      aria-label={`Shopping cart with ${itemCount} items`}
    >
      <svg className="cart-icon" viewBox="0 0 24 24" width="24" height="24">
        <path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/>
      </svg>
      {itemCount > 0 && (
        <span className="cart-badge">{itemCount}</span>
      )}
    </button>
  );
};
```

---

### 4. **Product Card - Add to Cart** (Ejemplo)

```jsx
// components/Product/ProductCard.jsx
import React, { useState } from 'react';
import { cartService } from '../../services/cartService';

export const ProductCard = ({ product }) => {
  const [loading, setLoading] = useState(false);

  const handleAddToCart = async () => {
    setLoading(true);
    try {
      const variantId = product.variants[0].id; // Primera variante
      
      await cartService.addToCart(variantId, 1, {
        id: product.id,
        name: product.name,
        price: product.variants[0].price,
        image: product.images[0]?.image_url,
      });

      // Notificar al CartButton que se actualizó el carrito
      window.dispatchEvent(new Event('cartUpdated'));
      
      alert('✅ Producto agregado al carrito');
    } catch (error) {
      console.error('Error adding to cart:', error);
      alert('❌ Error al agregar al carrito');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-card">
      <img src={product.images[0]?.image_url} alt={product.name} />
      <h3>{product.name}</h3>
      <p className="price">${product.variants[0]?.price}</p>
      <button 
        onClick={handleAddToCart}
        disabled={loading}
        className="add-to-cart-btn"
      >
        {loading ? 'Agregando...' : 'Agregar al Carrito'}
      </button>
    </div>
  );
};
```

---

### 5. **Login Component** (Sincronización automática)

```jsx
// components/Auth/Login.jsx
import React, { useState } from 'react';
import { api } from '../../utils/api';
import { cartService } from '../../services/cartService';

export const Login = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 1. Login
      const loginResponse = await api.post('/customers/login/', {
        username: email,
        password,
      });

      console.log('Login exitoso:', loginResponse);

      // 2. Guardar tokens y sincronizar carrito
      const cart = await cartService.handleLogin(loginResponse);
      
      console.log('Carrito sincronizado:', cart);

      // Notificar al resto de la app
      window.dispatchEvent(new Event('cartUpdated'));
      window.dispatchEvent(new Event('userLoggedIn'));

      alert(`✅ Bienvenido! Carrito: ${cart.total_items} items`);
      
      onLoginSuccess?.(loginResponse);
    } catch (error) {
      console.error('Login error:', error);
      alert('❌ Credenciales inválidas');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>
  );
};
```

---

## 🔄 Flujo Completo

### **Escenario 1: Usuario NO autenticado**

```javascript
// 1. Agregar producto al carrito
await cartService.addToCart(15, 2, {
  id: 1,
  name: 'Google Pixel 6',
  price: '599.00',
  image: 'https://...'
});

// 2. Ver carrito
const cart = await cartService.getCart();
console.log(cart);
// {
//   items: [{ variant_id: 15, quantity: 2, product: {...} }],
//   total_items: 2,
//   is_guest: true
// }

// 3. Hacer login
const loginResponse = await api.post('/customers/login/', {...});
await cartService.handleLogin(loginResponse);

// ✅ El carrito del localStorage se sincroniza automáticamente con el backend
```

---

### **Escenario 2: Usuario autenticado**

```javascript
// 1. Login (obtiene cart_id)
const loginResponse = await api.post('/customers/login/', {...});
await cartService.handleLogin(loginResponse);

// 2. Agregar productos
await cartService.addToCart(15, 2); // Directo al backend

// 3. Ver carrito
const cart = await cartService.getCart();
console.log(cart);
// {
//   id: 1,
//   customer: {...},
//   items: [...],
//   total_items: 2,
//   subtotal: "1198.00"
// }

// 4. Checkout
const order = await cartService.checkout({
  customer_id: 4,
  shipping_address_id: 1,
  payment_method: 'CREDIT_CARD',
  payment_provider: 'STRIPE'
});
```

---

## 🎯 Ventajas de esta Implementación

✅ **Transparente**: La API unificada detecta automáticamente si usar guest cart o backend  
✅ **Sin pérdida de datos**: El carrito guest se sincroniza automáticamente al hacer login  
✅ **Optimista**: No requiere autenticación para empezar a comprar  
✅ **Eficiente**: Minimiza requests al servidor para usuarios no autenticados  
✅ **Escalable**: Fácil de extender con funcionalidades adicionales  

---

## 📌 Notas Importantes

1. **El `cart_id` se obtiene del login response** y se guarda en `localStorage`
2. **El carrito guest se limpia automáticamente** después de sincronizarse
3. **El contador del carrito se actualiza** mediante eventos personalizados (`cartUpdated`)
4. **Solo usuarios autenticados pueden hacer checkout**
5. **El carrito backend es persistente**, el guest cart es temporal

---

## 🚀 Próximos Pasos

1. Implementar el UI del carrito (drawer/modal)
2. Agregar validación de stock antes de agregar items
3. Implementar el flujo de checkout completo
4. Agregar manejo de errores más robusto
5. Implementar refresh token automático
