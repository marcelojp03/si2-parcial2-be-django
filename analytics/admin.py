from django.contrib import admin
from .models import SaleFact, ForecastModel, Report


@admin.register(SaleFact)
class SaleFactAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'product_name', 'category_name', 'variant_code',
        'customer_name', 'qty', 'revenue', 'discount', 'created_at'
    ]
    list_filter = ['date', 'category_name']
    search_fields = ['product_name', 'customer_name', 'variant_code']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']


@admin.register(ForecastModel)
class ForecastModelAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'model_type', 'mae', 'rmse', 'r2_score',
        'is_active', 'created_at'
    ]
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type', 'format', 'generated_by',
        'file_size', 'created_at'
    ]
    list_filter = ['report_type', 'format', 'created_at']
    search_fields = ['title', 'description', 'generated_by']
    readonly_fields = ['created_at', 'file_size']
    date_hierarchy = 'created_at'

