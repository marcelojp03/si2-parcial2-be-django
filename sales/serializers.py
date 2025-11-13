from rest_framework import serializers
from .models import Address, Cart, CartItem, Order, OrderItem, Payment
from customers.models import Customer
from customers.serializers import CustomerSerializer as CustomersCustomerSerializer
from catalog.serializers import ProductVariantSerializer


class AddressSerializer(serializers.ModelSerializer):
    """Serializer para Direcciones"""
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'customer', 'customer_name', 'line1', 'city',
            'state', 'zip', 'notes', 'is_default'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para Items del Carrito"""
    variant_id = serializers.IntegerField(write_only=True, required=False)
    subtotal = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    variant_code = serializers.SerializerMethodField()
    variant_price = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(source='qty', read_only=True)
    price = serializers.DecimalField(source='unit_price', max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'variant', 'variant_id', 'variant_code',
            'product_name', 'product_image', 'variant_price', 'quantity', 'price', 
            'subtotal', 'added_at'
        ]
        read_only_fields = ['cart', 'variant', 'added_at']
    
    def get_subtotal(self, obj):
        return obj.qty * obj.unit_price
    
    def get_product_name(self, obj):
        if obj.variant and obj.variant.product:
            return obj.variant.product.name
        return None
    
    def get_product_image(self, obj):
        """Retorna la URL firmada de la imagen principal del producto"""
        if obj.variant and obj.variant.product:
            # Obtener la imagen principal o la primera imagen
            first_image = obj.variant.product.images.filter(is_main=True).first()
            if not first_image:
                first_image = obj.variant.product.images.first()
            
            if first_image:
                # Usar el método get_image_url que genera presigned URLs automáticamente
                # Expira en 1 hora (3600 segundos)
                return first_image.get_image_url(expiration=3600)
        return None
    
    def get_variant_code(self, obj):
        if obj.variant:
            return obj.variant.code
        return None
    
    def get_variant_price(self, obj):
        if obj.variant:
            return str(obj.variant.price)
        return None


class CartSerializer(serializers.ModelSerializer):
    """Serializer para Carrito"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    customer = CustomersCustomerSerializer(read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'customer', 'items', 'total_items',
            'subtotal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.items.count()
    
    def get_subtotal(self, obj):
        return sum(item.qty * item.unit_price for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer para Items de Pedido"""
    variant_code = serializers.CharField(source='variant.code', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'variant', 'variant_code', 'product_name',
            'qty', 'unit_price', 'discount', 'subtotal'
        ]
    
    def get_subtotal(self, obj):
        return (obj.qty * obj.unit_price) - obj.discount


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para Pagos"""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'provider', 'provider_ref',
            'amount', 'status', 'paid_at', 'created_at', 'idempotency_key'
        ]
        read_only_fields = ['created_at', 'paid_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer para Pedidos"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'shipping_address', 'status', 'payment_status', 'currency',
            'subtotal', 'discount_total', 'shipping_total', 'total',
            'items', 'payment', 'total_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.items.count()


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer para crear pedido desde carrito.
    Acepta OPCIÓN 1: shipping_address_id (dirección existente)
    o OPCIÓN 2: shipping_address (crear nueva dirección)
    """
    customer_id = serializers.IntegerField()
    
    # Opción 1: ID de dirección existente
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Opción 2: Datos para crear nueva dirección
    shipping_address = serializers.DictField(required=False, allow_null=True)
    
    payment_method = serializers.ChoiceField(choices=['CARD', 'CASH', 'TRANSFER', 'QR'])
    payment_provider = serializers.ChoiceField(
        choices=['STRIPE', 'PAYPAL', 'VPAY', 'MOCK', 'QR'],
        required=False,
        default='MOCK'
    )
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, data):
        """Validar que se proporcione shipping_address_id O shipping_address"""
        shipping_address_id = data.get('shipping_address_id')
        shipping_address = data.get('shipping_address')
        
        if not shipping_address_id and not shipping_address:
            raise serializers.ValidationError(
                'Debe proporcionar shipping_address_id o shipping_address'
            )
        
        if shipping_address_id and shipping_address:
            raise serializers.ValidationError(
                'Proporcione solo shipping_address_id O shipping_address, no ambos'
            )
        
        # Validar estructura de shipping_address si se proporciona
        if shipping_address:
            required_fields = ['line1', 'city']
            missing_fields = [field for field in required_fields if not shipping_address.get(field)]
            if missing_fields:
                raise serializers.ValidationError(
                    f'shipping_address requiere los campos: {", ".join(missing_fields)}'
                )
        
        return data


class AddToCartSerializer(serializers.Serializer):
    """Serializer para agregar items al carrito"""
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
