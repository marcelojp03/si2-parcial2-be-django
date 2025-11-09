from django.db import models
from catalog.models import ProductVariant


class Warehouse(models.Model):
    """
    Almacén o bodega.
    Soporta múltiples ubicaciones de inventario.
    """
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=200, blank=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_warehouse'
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Inventory(models.Model):
    """
    Inventario por variante y almacén.
    Permite gestionar stock disponible y reservado por ubicación.
    """
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name="inventories"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name="inventories"
    )
    stock_on_hand = models.IntegerField(default=0, help_text="Stock físico disponible")
    stock_reserved = models.IntegerField(default=0, help_text="Stock reservado en pedidos")
    min_stock = models.IntegerField(default=0, help_text="Stock mínimo para alertas")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_inventory'
        unique_together = ("variant", "warehouse")
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        indexes = [
            models.Index(fields=['variant', 'warehouse']),
        ]

    def __str__(self):
        return f"{self.variant.code} @ {self.warehouse.code}: {self.stock_on_hand}"
    
    @property
    def stock_available(self):
        """Stock disponible para venta (físico - reservado)"""
        return self.stock_on_hand - self.stock_reserved
    
    def reserve_stock(self, quantity):
        """Reserva stock para un pedido"""
        if self.stock_available >= quantity:
            self.stock_reserved += quantity
            self.save()
            return True
        return False
    
    def release_stock(self, quantity):
        """Libera stock reservado (cancelación)"""
        self.stock_reserved = max(0, self.stock_reserved - quantity)
        self.save()
    
    def confirm_sale(self, quantity):
        """Confirma venta y descuenta del stock físico"""
        self.stock_on_hand = max(0, self.stock_on_hand - quantity)
        self.stock_reserved = max(0, self.stock_reserved - quantity)
        self.save()

