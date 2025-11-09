from rest_framework import serializers
from .models import SaleFact, ForecastModel, Report


class SaleFactSerializer(serializers.ModelSerializer):
    """Serializer para Hechos de Venta"""
    
    class Meta:
        model = SaleFact
        fields = [
            'id', 'date', 'product_id', 'product_name', 'category_id',
            'category_name', 'variant_id', 'variant_code', 'customer_id',
            'customer_name', 'quantity', 'revenue', 'cost', 'discount',
            'order_id', 'created_at'
        ]
        read_only_fields = ['created_at']


class ForecastModelSerializer(serializers.ModelSerializer):
    """Serializer para Modelos de Forecasting"""
    
    class Meta:
        model = ForecastModel
        fields = [
            'id', 'name', 'description', 'model_type', 'model_file',
            'mae', 'rmse', 'r2_score', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer para Reportes"""
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'format', 'file_path',
            'filters', 'generated_by', 'created_at'
        ]
        read_only_fields = ['created_at', 'file_path']


class SalesReportRequestSerializer(serializers.Serializer):
    """Serializer para solicitar reporte de ventas"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    category_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)
    format = serializers.ChoiceField(choices=['PDF', 'EXCEL', 'CSV', 'JSON'], default='JSON')


class ForecastRequestSerializer(serializers.Serializer):
    """Serializer para solicitar forecasting"""
    product_id = serializers.IntegerField()
    periods = serializers.IntegerField(min_value=1, max_value=365, default=30)
    model_type = serializers.ChoiceField(
        choices=['RANDOM_FOREST', 'LINEAR_REGRESSION', 'ARIMA'],
        default='RANDOM_FOREST'
    )
