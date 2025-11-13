from django.contrib import admin
from .models import Address, Cart, CartItem, Order, OrderItem, Payment


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'city', 'state', 'is_default']
    list_filter = ['city', 'state', 'is_default']
    search_fields = ['customer__user__username', 'customer__user__email', 'city', 'line1']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'created_at', 'updated_at']
    search_fields = ['customer__user__username', 'customer__user__email']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'variant', 'qty', 'unit_price', 'subtotal', 'added_at']
    search_fields = ['cart__customer__user__username', 'cart__customer__user__email', 'variant__code']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'status', 'payment_status',
        'total', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer__user__username', 'customer__user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'variant', 'qty', 'unit_price', 'discount', 'subtotal']
    search_fields = ['order__order_number', 'variant__code']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'provider', 'status', 'amount', 'paid_at', 'created_at']
    list_filter = ['provider', 'status']
    search_fields = ['order__order_number', 'provider_ref']
    readonly_fields = ['created_at']

