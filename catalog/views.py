from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Category, Attribute, Product
from .serializers import (
    CategorySerializer,
    AttributeSerializer,
    ProductListSerializer,
    ProductDetailSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar categorías",
        description="Obtiene todas las categorías con su jerarquía",
        tags=['Catalog']
    ),
    retrieve=extend_schema(
        summary="Obtener categoría",
        description="Obtiene los detalles de una categoría específica",
        tags=['Catalog']
    ),
    create=extend_schema(
        summary="Crear categoría",
        description="Crea una nueva categoría",
        tags=['Catalog']
    ),
    update=extend_schema(
        summary="Actualizar categoría",
        description="Actualiza una categoría existente",
        tags=['Catalog']
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente categoría",
        description="Actualiza parcialmente una categoría existente",
        tags=['Catalog']
    ),
    destroy=extend_schema(
        summary="Eliminar categoría",
        description="Elimina una categoría",
        tags=['Catalog']
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de productos.
    Permite operaciones CRUD completas sobre categorías.
    """
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @extend_schema(
        summary="Obtener categorías raíz",
        description="Obtiene solo las categorías de nivel superior (sin padre)",
        tags=['Catalog']
    )
    @action(detail=False, methods=['get'])
    def root(self, request):
        """Obtiene solo las categorías raíz"""
        root_categories = self.get_queryset()
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Listar atributos",
        description="Obtiene todos los atributos con sus valores",
        tags=['Catalog']
    ),
    retrieve=extend_schema(
        summary="Obtener atributo",
        description="Obtiene los detalles de un atributo específico",
        tags=['Catalog']
    )
)
class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para atributos.
    Los atributos son gestionados por administradores desde el panel admin.
    """
    queryset = Attribute.objects.all().prefetch_related('values')
    serializer_class = AttributeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="Listar productos",
        description="Obtiene la lista de productos activos con paginación",
        tags=['Catalog'],
        parameters=[
            OpenApiParameter(
                name='category',
                description='Filtrar por slug de categoría',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='search',
                description='Buscar por nombre o descripción',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='min_price',
                description='Precio mínimo',
                required=False,
                type=OpenApiTypes.FLOAT
            ),
            OpenApiParameter(
                name='max_price',
                description='Precio máximo',
                required=False,
                type=OpenApiTypes.FLOAT
            ),
        ]
    ),
    retrieve=extend_schema(
        summary="Obtener producto",
        description="Obtiene los detalles completos de un producto con sus variantes",
        tags=['Catalog']
    )
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para productos.
    Permite listar y ver detalles de productos con sus variantes.
    """
    queryset = Product.objects.filter(status='ACTIVE').prefetch_related(
        'categories',
        'variants',
        'images'
    )
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por categoría
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(categories__name__icontains=category_slug)
        
        # Filtrar por rango de precio
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(variants__price__gte=min_price).distinct()
        if max_price:
            queryset = queryset.filter(variants__price__lte=max_price).distinct()
        
        return queryset
    
    @extend_schema(
        summary="Productos destacados",
        description="Obtiene los productos más recientes o destacados",
        tags=['Catalog']
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Obtiene productos destacados (últimos 10 productos)"""
        featured = self.get_queryset()[:10]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
