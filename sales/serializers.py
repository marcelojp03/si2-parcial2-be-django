from rest_framework import serializers
from .models import Customer, Address, Cart, CartItem, Order, OrderItem, Payment
from catalog.serializers import ProductVariantSerializer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer para Clientes"""
    total_orders = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'ci_nit', 'first_name', 'last_name', 'email',
            'phone', 'total_orders', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_total_orders(self, obj):
        return obj.orders.count()


class AddressSerializer(serializers.ModelSerializer):
    """Serializer para Direcciones"""
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'customer', 'customer_name', 'address_line', 'city',
            'state', 'postal_code', 'country', 'is_default', 'created_at'
        ]
        read_only_fields = ['created_at']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para Items del Carrito"""
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'variant', 'variant_id', 'product_name',
            'quantity', 'price', 'subtotal', 'created_at'
        ]
        read_only_fields = ['cart', 'price', 'created_at']
    
    def get_subtotal(self, obj):
        return obj.quantity * obj.price


class CartSerializer(serializers.ModelSerializer):
    """Serializer para Carrito"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'customer', 'customer_name', 'items', 'total_items',
            'total_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.items.count()
    
    def get_total_amount(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para Items de Pedido"""
    variant_code = serializers.CharField(source='variant.code', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'variant', 'variant_code', 'product_name',
            'quantity', 'price', 'subtotal'
        ]
    
    def get_subtotal(self, obj):
        return obj.quantity * obj.price


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para Pagos"""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'method', 'provider', 'provider_transaction_id',
            'amount', 'status', 'paid_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'paid_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer para Pedidos"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'shipping_address', 'status', 'payment_status',
            'subtotal', 'tax', 'shipping_cost', 'discount', 'total',
            'items', 'payment', 'total_items', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.items.count()


class OrderCreateSerializer(serializers.Serializer):
    """Serializer para crear pedido desde carrito"""
    customer_id = serializers.IntegerField()
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=['CARD', 'CASH', 'TRANSFER', 'QR'])
    payment_provider = serializers.ChoiceField(
        choices=['STRIPE', 'PAYPAL', 'MOCK', 'QR'],
        required=False,
        default='MOCK'
    )
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AddToCartSerializer(serializers.Serializer):
    """Serializer para agregar items al carrito"""
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
