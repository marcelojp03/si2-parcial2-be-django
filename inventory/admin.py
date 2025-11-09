from django.contrib import admin
from .models import Warehouse, Inventory


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'location']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        'variant', 'warehouse', 'stock_on_hand', 
        'stock_reserved', 'stock_available', 'min_stock', 'updated_at'
    ]
    list_filter = ['warehouse']
    search_fields = ['variant__code', 'variant__product__name', 'warehouse__name']
    readonly_fields = ['stock_available', 'updated_at']
    
    def stock_available(self, obj):
        return obj.stock_available
    stock_available.short_description = 'Stock Disponible'

