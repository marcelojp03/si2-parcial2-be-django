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
    
    # Token de autorización
    AUTH_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJTRUNVUklUWSIsImlzcyI6IlZFQ09NIiwiY29tcGFueSI6IjI2NiIsImxvZ2luIjoibnV0cmlzZXIifQ.tNBl8PIf4AmK0eqSHj6U9-MOlcrCfpxHYqOPUrvciGU"
    
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
            # Redondear monto a 2 decimales (evitar problemas con decimales largos)
            amount = round(float(amount), 2)
            
            # Calcular fecha de expiración (usar fecha de hoy + días)
            # VPAY parece necesitar formato YYYY-MM-DD
            from datetime import date
            expiration_date = (
                date.today() + timedelta(days=1)
            ).strftime("%Y-%m-%d")
            
            # Preparar payload - VPAY requiere el campo "detail" obligatorio
            payload = {
                "operation": "VTO041",
                "header": [
                    {"attribute": "currency", "value": "BOB"},
                    {"attribute": "gloss", "value": "COBRO SERVICIO SI2-ESHOP"},
                    {"attribute": "amount", "value": f"{amount:.2f}"},
                    {"attribute": "singleUse", "value": "true"},
                    {"attribute": "expirationDate", "value": expiration_date},
                    {"attribute": "additionalData", "value": f"Cobro Pedido {order_number}"},
                    {"attribute": "destinationAccountId", "value": cls.VPAY_ACCOUNT},
                    {"attribute": "bank", "value": cls.VPAY_BANK},
                    {"attribute": "user", "value": cls.VPAY_USER},
                    {"attribute": "company", "value": cls.VPAY_COMPANY},
                ],
                "detail": [
                    {
                        "items": []
                    }
                ]
            }
            
            logger.info(f"🔵 Generando QR VPAY - Order: {order_number}, Amount: {amount}")
            logger.info(f"📤 VPAY URL: {cls.BASE_URL}/transactions/doPayment")
            logger.info(f"📤 VPAY Payload: {payload}")
            logger.info(f"📤 VPAY Headers: Authorization={cls.AUTH_TOKEN[:20]}...")
            
            # Print para debug (aparecerá en consola)
            print(f"\n{'='*60}")
            print(f"🔵 GENERANDO QR VPAY")
            print(f"{'='*60}")
            print(f"Order: {order_number}")
            print(f"Amount: {amount} BOB")
            print(f"Expiration: {expiration_date}")
            print(f"URL: {cls.BASE_URL}/transactions/doPayment")
            print(f"Payload: {payload}")
            print(f"Headers: Authorization={cls.AUTH_TOKEN[:30]}...")
            print(f"{'='*60}\n")
            
            # Headers con token de autorización
            headers = {
                "Authorization": cls.AUTH_TOKEN,
                "Content-Type": "application/json"
            }
            
            # Llamar a API de VPAY
            response = requests.put(
                f"{cls.BASE_URL}/transactions/doPayment",
                json=payload,
                headers=headers,
                timeout=30,
                verify=True  # Cambiar a False si hay problemas con SSL
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"📥 VPAY Response Status: {response.status_code}")
            logger.info(f"📥 VPAY Response Data: {data}")
            
            print(f"\n{'='*60}")
            print(f"📥 RESPUESTA DE VPAY")
            print(f"{'='*60}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {data}")
            print(f"VPAY Status: {data.get('status')}")
            print(f"VPAY Message: {data.get('message')}")
            print(f"{'='*60}\n")
            
            # Validar respuesta - Si status != "OK", es error
            if data.get("status") != "OK":
                logger.error(f"❌ VPAY error: {data.get('message')}")
                print(f"❌ VPAY rechazó la transacción: {data.get('message')}")
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
            
            logger.info(f"✅ QR generado exitosamente - ID: {qr_id}")
            
            return {
                "success": True,
                "qr_id": qr_id,
                "qr_image": qr_image,  # Base64
                "expiration_date": expiration_date
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error conectando con VPAY: {e}")
            logger.error(f"❌ Request details - URL: {cls.BASE_URL}/transactions/doPayment")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"❌ Response status: {e.response.status_code}")
                logger.error(f"❌ Response body: {e.response.text}")
            return {
                "success": False,
                "error": f"Error de conexión con VPAY: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Error generando QR VPAY: {e}")
            logger.exception("Full traceback:")
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
            
            # Headers con token de autorización
            headers = {
                "Authorization": cls.AUTH_TOKEN,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{cls.BASE_URL}/operations/statusQr",
                json=payload,
                headers=headers,
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
