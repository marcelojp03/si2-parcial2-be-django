"""
Sistema de respuestas personalizadas para la API
Adaptado del sistema Flask a Django REST Framework
"""
from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """
    Clase para generar respuestas consistentes en la API
    Similar al sistema de Flask pero adaptado a Django REST Framework
    """
    
    @staticmethod
    def success(data=None, message="OK", meta=None, http_code=200):
        """
        Respuesta exitosa
        
        Args:
            data: payload (objeto o lista)
            message: mensaje descriptivo
            meta: dict opcional (paginación, filtros, etc.)
            http_code: código HTTP (default: 200)
        """
        body = {
            "success": True,
            "message": message,
            "data": data
        }
        if meta is not None:
            body["meta"] = meta
        
        return Response(body, status=http_code)
    
    @staticmethod
    def paginated(items, total, page, page_size, message="OK", http_code=200):
        """
        Respuesta paginada
        
        Args:
            items: lista de elementos de la página actual
            total: total de elementos
            page: página actual
            page_size: tamaño de página
            message: mensaje descriptivo
            http_code: código HTTP (default: 200)
        """
        meta = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }
        return ApiResponse.success(data=items, message=message, meta=meta, http_code=http_code)
    
    @staticmethod
    def error(message="Error", http_code=400, code=None, details=None):
        """
        Respuesta de error
        
        Args:
            message: mensaje de error
            http_code: código HTTP (default: 400)
            code: string corta para tipo de error (ej. 'VALIDATION_ERROR', 'NOT_FOUND')
            details: dict/list con campos inválidos o info extra
        """
        body = {
            "success": False,
            "message": message,
            "data": None
        }
        if code is not None:
            body["code"] = code
        if details is not None:
            body["details"] = details
        
        return Response(body, status=http_code)
    
    @staticmethod
    def from_exception(ex, http_code=500, code="INTERNAL_ERROR"):
        """
        Respuesta desde una excepción
        
        Args:
            ex: excepción capturada
            http_code: código HTTP (default: 500)
            code: código de error
        """
        return ApiResponse.error(message=str(ex), http_code=http_code, code=code)
    
    @staticmethod
    def validation_error(errors, message="Errores de validación"):
        """
        Respuesta para errores de validación
        
        Args:
            errors: dict con errores de validación (serializer.errors)
            message: mensaje descriptivo
        """
        return ApiResponse.error(
            message=message,
            http_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            details=errors
        )
    
    @staticmethod
    def not_found(message="Recurso no encontrado", resource=None):
        """
        Respuesta para recurso no encontrado
        
        Args:
            message: mensaje descriptivo
            resource: nombre del recurso no encontrado
        """
        details = {"resource": resource} if resource else None
        return ApiResponse.error(
            message=message,
            http_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            details=details
        )
    
    @staticmethod
    def unauthorized(message="No autorizado"):
        """
        Respuesta para acceso no autorizado
        """
        return ApiResponse.error(
            message=message,
            http_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED"
        )
    
    @staticmethod
    def forbidden(message="Acceso denegado"):
        """
        Respuesta para acceso prohibido
        """
        return ApiResponse.error(
            message=message,
            http_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN"
        )
    
    @staticmethod
    def conflict(message="Conflicto", details=None):
        """
        Respuesta para conflictos (ej. recurso duplicado)
        """
        return ApiResponse.error(
            message=message,
            http_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            details=details
        )
    
    @staticmethod
    def rate_limit_exceeded(message="Límite de peticiones excedido"):
        """
        Respuesta para límite de tasa excedido
        """
        return ApiResponse.error(
            message=message,
            http_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED"
        )


# Alias para compatibilidad
Responses = ApiResponse
