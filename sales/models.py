from django.db import models
from django.conf import settings
from catalog.models import ProductVariant


class Address(models.Model):
    """
    Dirección de envío/facturación de un cliente.
    """
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name="addresses")
    line1 = models.CharField(max_length=200, verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, blank=True, verbose_name="Departamento")
    zip = models.CharField(max_length=20, blank=True, verbose_name="Código Postal")
    notes = models.CharField(max_length=200, blank=True, verbose_name="Referencia")
    is_default = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sales_address'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return f"{self.customer.full_name} - {self.city}"


class Cart(models.Model):
    """
    Carrito de compras de un cliente.
    """
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_cart'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        return f"Carrito de {self.customer.user.get_full_name()}"


class CartItem(models.Model):
    """
    Item del carrito de compras.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sales_cart_item'
        unique_together = ('cart', 'variant')
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'

    def __str__(self):
        return f"{self.variant.code} x{self.qty}"
    
    @property
    def subtotal(self):
        return self.qty * self.unit_price


class Order(models.Model):
    """
    Pedido/Orden de compra.
    Desacoplado del pago para permitir múltiples flujos.
    """
    STATUS_CHOICES = [
        ('CREATED', 'Creado'),
        ('PAID', 'Pagado'),
        ('PROCESSING', 'En Proceso'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('FAILED', 'Fallido'),
        ('REFUNDED', 'Reembolsado'),
    ]
    
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name="orders")
    order_number = models.CharField(max_length=20, unique=True)
    currency = models.CharField(max_length=8, default="BOB")
    status = models.CharField(max_length=20, default="CREATED", choices=STATUS_CHOICES)
    
    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    payment_status = models.CharField(max_length=20, default="PENDING", choices=PAYMENT_STATUS_CHOICES)
    
    # Dirección de envío
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_order'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Pedido {self.order_number} - {self.customer.user.get_full_name()}"


class OrderItem(models.Model):
    """
    Item individual de un pedido.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'sales_order_item'
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'

    def __str__(self):
        return f"{self.order.order_number} - {self.variant.code}"
    
    @property
    def subtotal(self):
        return (self.qty * self.unit_price) - self.discount


class Payment(models.Model):
    """
    Pago asociado a un pedido.
    Desacoplado para soportar múltiples proveedores.
    """
    STATUS_CHOICES = [
        ('INIT', 'Iniciado'),
        ('PENDING', 'Pendiente'),
        ('SUCCESS', 'Exitoso'),
        ('FAILED', 'Fallido'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=30, help_text="STRIPE, PAYPAL, MOCK, QR")
    provider_ref = models.CharField(max_length=120, blank=True, help_text="ID de transacción del proveedor")
    status = models.CharField(max_length=20, default="INIT", choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    idempotency_key = models.CharField(max_length=120, blank=True, db_index=True, help_text="Clave de idempotencia para evitar pagos duplicados")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sales_payment'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago {self.provider} - {self.order.order_number}"

