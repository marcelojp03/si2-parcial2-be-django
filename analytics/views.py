from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from .models import SaleFact, ForecastModel, Report
from .serializers import (
    SaleFactSerializer,
    ForecastModelSerializer,
    ReportSerializer,
    SalesReportRequestSerializer,
    ForecastRequestSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar ventas",
        description="Obtiene los hechos de venta",
        tags=['Analytics']
    ),
    retrieve=extend_schema(
        summary="Obtener venta",
        tags=['Analytics']
    )
)
class SaleFactViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar hechos de venta"""
    queryset = SaleFact.objects.all().order_by('-date')
    serializer_class = SaleFactSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        product_id = self.request.query_params.get('product_id')
        category_id = self.request.query_params.get('category_id')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
    
    @extend_schema(
        summary="Dashboard de ventas",
        description="Obtiene métricas clave de ventas",
        tags=['Analytics']
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Métricas principales del dashboard"""
        # Últimos 30 días
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        metrics = SaleFact.objects.filter(date__gte=thirty_days_ago).aggregate(
            total_revenue=Sum('revenue'),
            total_orders=Count('order_id', distinct=True),
            total_units=Sum('quantity'),
            avg_order_value=Avg('revenue')
        )
        
        # Ventas por día (últimos 30 días)
        daily_sales = SaleFact.objects.filter(
            date__gte=thirty_days_ago
        ).annotate(
            day=TruncDate('date')
        ).values('day').annotate(
            revenue=Sum('revenue'),
            orders=Count('order_id', distinct=True)
        ).order_by('day')
        
        # Top productos
        top_products = SaleFact.objects.filter(
            date__gte=thirty_days_ago
        ).values(
            'product_id', 'product_name'
        ).annotate(
            revenue=Sum('revenue'),
            units_sold=Sum('quantity')
        ).order_by('-revenue')[:10]
        
        # Top categorías
        top_categories = SaleFact.objects.filter(
            date__gte=thirty_days_ago
        ).values(
            'category_id', 'category_name'
        ).annotate(
            revenue=Sum('revenue')
        ).order_by('-revenue')[:5]
        
        return Response({
            'period': '30_days',
            'metrics': metrics,
            'daily_sales': list(daily_sales),
            'top_products': list(top_products),
            'top_categories': list(top_categories)
        })
    
    @extend_schema(
        summary="Generar reporte de ventas",
        request=SalesReportRequestSerializer,
        tags=['Analytics']
    )
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Genera un reporte de ventas"""
        serializer = SalesReportRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar ventas
        sales = SaleFact.objects.filter(
            date__gte=serializer.validated_data['start_date'],
            date__lte=serializer.validated_data['end_date']
        )
        
        if serializer.validated_data.get('category_id'):
            sales = sales.filter(category_id=serializer.validated_data['category_id'])
        
        if serializer.validated_data.get('product_id'):
            sales = sales.filter(product_id=serializer.validated_data['product_id'])
        
        # Agregar datos
        report_data = {
            'period': {
                'start': serializer.validated_data['start_date'],
                'end': serializer.validated_data['end_date']
            },
            'summary': sales.aggregate(
                total_revenue=Sum('revenue'),
                total_cost=Sum('cost'),
                total_discount=Sum('discount'),
                total_units=Sum('quantity'),
                total_orders=Count('order_id', distinct=True),
                avg_order_value=Avg('revenue')
            ),
            'by_product': list(sales.values(
                'product_name'
            ).annotate(
                revenue=Sum('revenue'),
                units=Sum('quantity')
            ).order_by('-revenue')[:20]),
            'by_date': list(sales.annotate(
                day=TruncDate('date')
            ).values('day').annotate(
                revenue=Sum('revenue')
            ).order_by('day'))
        }
        
        return Response(report_data)


@extend_schema_view(
    list=extend_schema(
        summary="Listar modelos de forecasting",
        tags=['Analytics']
    ),
    retrieve=extend_schema(
        summary="Obtener modelo",
        tags=['Analytics']
    ),
    create=extend_schema(
        summary="Crear modelo",
        tags=['Analytics']
    )
)
class ForecastModelViewSet(viewsets.ModelViewSet):
    """ViewSet para modelos de forecasting"""
    queryset = ForecastModel.objects.all().order_by('-created_at')
    serializer_class = ForecastModelSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Predecir ventas",
        request=ForecastRequestSerializer,
        tags=['Analytics']
    )
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Genera predicción de ventas (Simulado)"""
        serializer = ForecastRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        periods = serializer.validated_data['periods']
        
        # Obtener datos históricos
        historical_data = SaleFact.objects.filter(
            product_id=product_id
        ).values('date').annotate(
            units=Sum('quantity')
        ).order_by('date')
        
        if not historical_data.exists():
            return Response(
                {'error': 'No hay datos históricos para este producto'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Simulación simple de forecasting
        # En producción, usar modelos ML reales
        avg_sales = historical_data.aggregate(avg=Avg('units'))['avg'] or 0
        
        predictions = []
        start_date = datetime.now().date()
        
        for i in range(periods):
            date = start_date + timedelta(days=i)
            # Simulación con variación aleatoria
            import random
            predicted_units = max(0, int(avg_sales * random.uniform(0.8, 1.2)))
            
            predictions.append({
                'date': date,
                'predicted_units': predicted_units,
                'confidence': 0.85
            })
        
        return Response({
            'product_id': product_id,
            'model_type': serializer.validated_data['model_type'],
            'historical_avg': avg_sales,
            'predictions': predictions
        })


@extend_schema_view(
    list=extend_schema(
        summary="Listar reportes",
        tags=['Analytics']
    ),
    retrieve=extend_schema(
        summary="Obtener reporte",
        tags=['Analytics']
    )
)
class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para historial de reportes"""
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]
