from rest_framework import serializers
from .models import Warehouse, Inventory
from catalog.serializers import ProductVariantSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer para Almacenes"""
    total_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'location', 'is_active',
            'total_products', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_total_products(self, obj):
        """Cuenta productos únicos en el almacén"""
        return obj.inventories.filter(stock_on_hand__gt=0).count()


class InventorySerializer(serializers.ModelSerializer):
    """Serializer para Inventario"""
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    variant_code = serializers.CharField(source='variant.code', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    stock_available = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'warehouse', 'warehouse_name', 'variant', 'variant_code',
            'product_name', 'stock_on_hand', 'stock_reserved', 'stock_available',
            'min_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'stock_available']


class InventoryDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado con información de variante"""
    warehouse = WarehouseSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    stock_available = serializers.IntegerField(read_only=True)
    needs_restock = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'warehouse', 'variant', 'stock_on_hand', 'stock_reserved',
            'stock_available', 'min_stock', 'needs_restock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_needs_restock(self, obj):
        """Indica si necesita reabastecimiento"""
        return obj.stock_available < obj.min_stock


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer para ajustes de stock"""
    quantity = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255, required=False)


class StockReservationSerializer(serializers.Serializer):
    """Serializer para reservas de stock"""
    warehouse_id = serializers.IntegerField()
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate(self, attrs):
        """Valida que haya stock disponible"""
        try:
            inventory = Inventory.objects.get(
                warehouse_id=attrs['warehouse_id'],
                variant_id=attrs['variant_id']
            )
            if inventory.stock_available < attrs['quantity']:
                raise serializers.ValidationError({
                    'quantity': f'Stock insuficiente. Disponible: {inventory.stock_available}'
                })
        except Inventory.DoesNotExist:
            raise serializers.ValidationError('Inventario no encontrado')
        
        return attrs
