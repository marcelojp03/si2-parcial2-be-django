from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Sum, F
from .models import Warehouse, Inventory
from .serializers import (
    WarehouseSerializer,
    InventorySerializer,
    InventoryDetailSerializer,
    StockAdjustmentSerializer,
    StockReservationSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar almacenes",
        description="Obtiene todos los almacenes activos",
        tags=['Inventory']
    ),
    retrieve=extend_schema(
        summary="Obtener almacén",
        description="Obtiene los detalles de un almacén específico",
        tags=['Inventory']
    ),
    create=extend_schema(
        summary="Crear almacén",
        description="Crea un nuevo almacén",
        tags=['Inventory']
    ),
    update=extend_schema(
        summary="Actualizar almacén",
        description="Actualiza un almacén existente",
        tags=['Inventory']
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente almacén",
        description="Actualiza parcialmente un almacén",
        tags=['Inventory']
    )
)
class WarehouseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar almacenes.
    Permite CRUD completo sobre almacenes.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'location']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    @extend_schema(
        summary="Inventario del almacén",
        description="Obtiene todo el inventario de un almacén",
        tags=['Inventory']
    )
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Obtiene el inventario completo de un almacén"""
        warehouse = self.get_object()
        inventories = warehouse.inventories.select_related('variant__product').all()
        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Productos con stock bajo",
        description="Productos que necesitan reabastecimiento",
        tags=['Inventory']
    )
    @action(detail=True, methods=['get'])
    def low_stock(self, request, pk=None):
        """Productos con stock por debajo del mínimo"""
        warehouse = self.get_object()
        low_stock = warehouse.inventories.filter(
            stock_on_hand__lte=F('min_stock')
        ).select_related('variant__product')
        serializer = InventorySerializer(low_stock, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Listar inventario",
        description="Obtiene el inventario con filtros",
        tags=['Inventory'],
        parameters=[
            OpenApiParameter(
                name='warehouse',
                description='Filtrar por ID de almacén',
                required=False,
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name='variant',
                description='Filtrar por ID de variante',
                required=False,
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name='low_stock',
                description='Mostrar solo stock bajo (true/false)',
                required=False,
                type=OpenApiTypes.BOOL
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Obtener inventario",
        description="Obtiene los detalles de un registro de inventario",
        tags=['Inventory']
    ),
    create=extend_schema(
        summary="Crear inventario",
        description="Crea un nuevo registro de inventario",
        tags=['Inventory']
    ),
    update=extend_schema(
        summary="Actualizar inventario",
        description="Actualiza un registro de inventario",
        tags=['Inventory']
    )
)
class InventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar inventario.
    Permite gestión de stock por almacén y variante.
    """
    queryset = Inventory.objects.select_related(
        'warehouse',
        'variant__product'
    ).all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['variant__code', 'variant__product__name', 'warehouse__name']
    ordering_fields = ['stock_on_hand', 'stock_available', 'min_stock']
    ordering = ['-stock_on_hand']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryDetailSerializer
        return InventorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por almacén
        warehouse_id = self.request.query_params.get('warehouse')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        # Filtrar por variante
        variant_id = self.request.query_params.get('variant')
        if variant_id:
            queryset = queryset.filter(variant_id=variant_id)
        
        # Filtrar stock bajo
        low_stock = self.request.query_params.get('low_stock')
        if low_stock and low_stock.lower() == 'true':
            queryset = queryset.filter(stock_on_hand__lte=F('min_stock'))
        
        return queryset
    
    @extend_schema(
        summary="Ajustar stock",
        description="Incrementa o decrementa el stock disponible",
        request=StockAdjustmentSerializer,
        tags=['Inventory']
    )
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Ajusta el stock manualmente (entrada/salida)"""
        inventory = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            reason = serializer.validated_data.get('reason', 'Ajuste manual')
            
            # Incrementar stock
            inventory.stock_on_hand += quantity
            inventory.save()
            
            return Response({
                'message': f'Stock ajustado: +{quantity}',
                'reason': reason,
                'new_stock': inventory.stock_on_hand,
                'available': inventory.stock_available
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Reservar stock",
        description="Reserva stock para un pedido",
        request=StockReservationSerializer,
        tags=['Inventory']
    )
    @action(detail=False, methods=['post'])
    def reserve(self, request):
        """Reserva stock para un pedido"""
        serializer = StockReservationSerializer(data=request.data)
        
        if serializer.is_valid():
            inventory = Inventory.objects.get(
                warehouse_id=serializer.validated_data['warehouse_id'],
                variant_id=serializer.validated_data['variant_id']
            )
            
            quantity = serializer.validated_data['quantity']
            inventory.reserve_stock(quantity)
            
            return Response({
                'message': f'Stock reservado: {quantity} unidades',
                'reserved': inventory.stock_reserved,
                'available': inventory.stock_available
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Confirmar venta",
        description="Confirma una venta y reduce el stock reservado",
        request=StockAdjustmentSerializer,
        tags=['Inventory']
    )
    @action(detail=True, methods=['post'])
    def confirm_sale(self, request, pk=None):
        """Confirma una venta y reduce stock reservado"""
        inventory = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            inventory.confirm_sale(quantity)
            
            return Response({
                'message': f'Venta confirmada: {quantity} unidades',
                'stock_on_hand': inventory.stock_on_hand,
                'stock_reserved': inventory.stock_reserved,
                'available': inventory.stock_available
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Liberar stock",
        description="Libera stock reservado (cancelación de pedido)",
        request=StockAdjustmentSerializer,
        tags=['Inventory']
    )
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Libera stock reservado (cancelación)"""
        inventory = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            inventory.release_stock(quantity)
            
            return Response({
                'message': f'Stock liberado: {quantity} unidades',
                'stock_reserved': inventory.stock_reserved,
                'available': inventory.stock_available
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
