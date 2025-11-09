"""
Healthcheck endpoint para verificar el estado del sistema.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Healthcheck del sistema",
    description="Verifica el estado de la base de datos y servicios críticos",
    tags=['System']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def healthcheck(request):
    """
    Endpoint de healthcheck para monitoreo.
    Verifica:
    - Conexión a base de datos
    - Capacidad de ejecutar queries
    - Estado general del sistema
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Check 1: Database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'ok',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }
    
    # Check 2: Database schema
    try:
        from django.apps import apps
        model_count = len(apps.get_models())
        health_status['checks']['models'] = {
            'status': 'ok',
            'message': f'{model_count} models loaded'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['models'] = {
            'status': 'error',
            'message': f'Models error: {str(e)}'
        }
    
    # Check 3: Critical tables exist
    try:
        from sales.models import Order
        from inventory.models import Inventory
        from catalog.models import Product
        
        Order.objects.exists()
        Inventory.objects.exists()
        Product.objects.exists()
        
        health_status['checks']['tables'] = {
            'status': 'ok',
            'message': 'Critical tables accessible'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['tables'] = {
            'status': 'error',
            'message': f'Tables error: {str(e)}'
        }
    
    # Determinar status code HTTP
    http_status = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_status, status=http_status)
