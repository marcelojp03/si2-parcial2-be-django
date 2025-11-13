"""
Servicio de integración con VPAY
API de pagos QR de Bolivia
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class VPayService:
    """Cliente para API de VPAY"""
    
    BASE_URL = "https://vpay.com.bo:7778/pro/api"
    
    # Configuración (mover a settings.py en producción)
    VPAY_USER = "selvi.lecaro"
    VPAY_COMPANY = "82"
    VPAY_BANK = "BMSC"
    VPAY_ACCOUNT = "selvi.lecaro"
    
    @classmethod
    def generate_qr_payment(
        cls,
        amount: float,
        gloss: str,
        order_number: str,
        expiration_hours: int = 24
    ) -> Dict:
        """
        Genera un código QR para pago con VPAY.
        
        Args:
            amount: Monto en BOB
            gloss: Descripción del pago
            order_number: Número de pedido (para additionalData)
            expiration_hours: Horas hasta expiración del QR
            
        Returns:
            {
                "success": bool,
                "qr_id": str,           # idQr de VPAY
                "qr_image": str,        # Imagen base64
                "error": str            # Si hubo error
            }
        """
        try:
            # Calcular fecha de expiración
            expiration_date = (
                datetime.now() + timedelta(hours=expiration_hours)
            ).strftime("%Y-%m-%d")
            
            # Preparar payload
            payload = {
                "operation": "VTO041",
                "header": [
                    {"attribute": "currency", "value": "BOB"},
                    {"attribute": "gloss", "value": "SI2-ESHOP"},
                    {"attribute": "amount", "value": str(amount)},
                    {"attribute": "singleUse", "value": "true"},
                    {"attribute": "expirationDate", "value": expiration_date},
                    {"attribute": "additionalData", "value": f"Pedido {order_number}"},
                    {"attribute": "destinationAccountId", "value": cls.VPAY_ACCOUNT},
                    {"attribute": "bank", "value": cls.VPAY_BANK},
                    {"attribute": "user", "value": cls.VPAY_USER},
                    {"attribute": "company", "value": cls.VPAY_COMPANY},
                ]
            }
            
            logger.info(f"🔵 Generando QR VPAY - Order: {order_number}, Amount: {amount}")
            
            # Llamar a API de VPAY
            response = requests.put(
                f"{cls.BASE_URL}/transactions/doPayment",
                json=payload,
                timeout=30,
                verify=True  # Cambiar a False si hay problemas con SSL
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Validar respuesta
            if data.get("status") != "OK":
                logger.error(f"❌ VPAY error: {data.get('message')}")
                return {
                    "success": False,
                    "error": data.get("message", "Error desconocido de VPAY")
                }
            
            # Extraer QR ID e imagen
            response_list = data.get("responseList", [{}])[0].get("response", [])
            qr_id = None
            qr_image = None
            
            for item in response_list:
                if item.get("code") == "idQr":
                    qr_id = item.get("identificator")
                elif item.get("code") == "QR":
                    qr_image = item.get("identificator")
            
            if not qr_id or not qr_image:
                logger.error(f"❌ VPAY respuesta incompleta: {data}")
                return {
                    "success": False,
                    "error": "Respuesta de VPAY incompleta"
                }
            
            logger.info(f"✅ QR generado - ID: {qr_id}")
            
            return {
                "success": True,
                "qr_id": qr_id,
                "qr_image": qr_image,  # Base64
                "expiration_date": expiration_date
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error conectando con VPAY: {e}")
            return {
                "success": False,
                "error": f"Error de conexión con VPAY: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Error generando QR VPAY: {e}")
            return {
                "success": False,
                "error": f"Error interno: {str(e)}"
            }
    
    @classmethod
    def check_qr_status(cls, qr_id: str) -> Dict:
        """
        Consulta el estado de un QR de VPAY.
        
        Args:
            qr_id: ID del QR retornado por generate_qr_payment
            
        Returns:
            {
                "success": bool,
                "status": str,      # "PEN" o "PAG"
                "is_paid": bool,    # True si status == "PAG"
                "error": str
            }
        """
        try:
            payload = {
                "operation": qr_id
            }
            
            logger.info(f"🔍 Consultando estado QR: {qr_id}")
            
            response = requests.post(
                f"{cls.BASE_URL}/operations/statusQr",
                json=payload,
                timeout=15,
                verify=True
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                logger.error(f"❌ VPAY status error: {data.get('message')}")
                return {
                    "success": False,
                    "error": data.get("message", "Error consultando estado")
                }
            
            # Extraer estado del QR
            response_list = data.get("responseList", [{}])[0].get("response", [])
            qr_status = None
            
            for item in response_list:
                if item.get("code") == "statusQr":
                    qr_status = item.get("identificator")
                    break
            
            if not qr_status:
                logger.error(f"❌ VPAY respuesta sin estado: {data}")
                return {
                    "success": False,
                    "error": "Respuesta de VPAY sin estado"
                }
            
            is_paid = qr_status == "PAG"
            
            logger.info(f"📊 QR {qr_id} - Estado: {qr_status} - Pagado: {is_paid}")
            
            return {
                "success": True,
                "status": qr_status,
                "is_paid": is_paid
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error conectando con VPAY: {e}")
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Error consultando estado QR: {e}")
            return {
                "success": False,
                "error": f"Error interno: {str(e)}"
            }


# Funciones helper para usar en views

def generate_vpay_qr(order) -> Dict:
    """
    Genera QR de VPAY para un pedido.
    
    Args:
        order: Instancia de Order
        
    Returns:
        Diccionario con qr_id, qr_image (base64), success, error
    """
    return VPayService.generate_qr_payment(
        amount=float(order.total),
        gloss=f"Pedido {order.order_number}",
        order_number=order.order_number,
        expiration_hours=24
    )


def check_vpay_payment_status(qr_id: str) -> Dict:
    """
    Verifica si el QR de VPAY ha sido pagado.
    
    Args:
        qr_id: ID del QR de VPAY
        
    Returns:
        {"success": bool, "is_paid": bool, "status": str}
    """
    return VPayService.check_qr_status(qr_id)
