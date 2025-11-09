from django.db import models


class SaleFact(models.Model):
    """
    Tabla de hechos para análisis de ventas y forecasting.
    Desnormalizada para optimizar consultas de reportes.
    """
    date = models.DateField(db_index=True)
    
    # IDs de dimensiones (desnormalizados)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=160, blank=True)
    category_id = models.IntegerField(null=True, blank=True)
    category_name = models.CharField(max_length=120, blank=True)
    variant_id = models.IntegerField(null=True, blank=True)
    variant_code = models.CharField(max_length=64, blank=True)
    customer_id = models.IntegerField(null=True, blank=True)
    customer_name = models.CharField(max_length=160, blank=True)
    
    # Métricas
    qty = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Metadata
    order_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_sale_fact'
        verbose_name = 'Hecho de Venta'
        verbose_name_plural = 'Hechos de Ventas'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['product_id', 'date']),
            models.Index(fields=['category_id', 'date']),
            models.Index(fields=['customer_id', 'date']),
            models.Index(fields=['date', 'product_id', 'variant_id']),
        ]

    def __str__(self):
        return f"{self.date} - {self.product_name} (Qty: {self.qty}, Revenue: {self.revenue})"


class ForecastModel(models.Model):
    """
    Registro de modelos de forecasting entrenados.
    Guarda metadata sobre cada modelo generado.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=50, default="RandomForest")
    file_path = models.CharField(max_length=400, help_text="Path al archivo .joblib del modelo")
    
    # Métricas de evaluación
    mae = models.FloatField(null=True, blank=True, verbose_name="Mean Absolute Error")
    rmse = models.FloatField(null=True, blank=True, verbose_name="Root Mean Squared Error")
    r2_score = models.FloatField(null=True, blank=True, verbose_name="R² Score")
    
    # Configuración del entrenamiento
    training_date_from = models.DateField(null=True, blank=True)
    training_date_to = models.DateField(null=True, blank=True)
    features_used = models.TextField(blank=True, help_text="JSON de features usadas")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_forecast_model'
        verbose_name = 'Modelo de Predicción'
        verbose_name_plural = 'Modelos de Predicción'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.model_type})"


class Report(models.Model):
    """
    Registro de reportes generados.
    Permite auditar qué reportes se generaron y cuándo.
    """
    REPORT_TYPES = [
        ('SALES_BY_DATE', 'Ventas por Fecha'),
        ('SALES_BY_PRODUCT', 'Ventas por Producto'),
        ('SALES_BY_CATEGORY', 'Ventas por Categoría'),
        ('SALES_BY_CUSTOMER', 'Ventas por Cliente'),
        ('INVENTORY_STATUS', 'Estado de Inventario'),
        ('CUSTOM', 'Personalizado'),
    ]
    
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
    ]
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    
    # Filtros aplicados (JSON)
    filters = models.TextField(blank=True, help_text="JSON con filtros aplicados")
    
    # Usuario que generó el reporte
    generated_by = models.CharField(max_length=150, blank=True)
    
    # Archivo generado
    file_path = models.CharField(max_length=400, blank=True)
    file_size = models.IntegerField(null=True, blank=True, help_text="Tamaño en bytes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_report'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.format}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

