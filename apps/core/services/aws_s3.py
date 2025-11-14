"""
Servicio para gestión de archivos en AWS S3
Bucket: si2-proyectos
Carpeta de imágenes de productos: si2-ecommerce-images/

Basado en el proyecto Flask pero adaptado para Django.
"""
import boto3
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Tuple
from django.conf import settings
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Configuración de boto3
AWS_CONFIG = Config(
    max_pool_connections=50,
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    },
    connect_timeout=10,
    read_timeout=120
)

# Bucket y carpeta de productos
BUCKET_NAME = 'si2-proyectos'
PRODUCTS_BASE_PATH = 'si2-ecommerce-images'


def _get_s3_client():
    """
    Crea y retorna un cliente S3 configurado.
    Usa IAM Role en producción (App Runner/EC2) o AWS profile local.
    """
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        profile = os.getenv('AWS_PROFILE')
        
        # En producción (App Runner/Lambda/EC2): usar IAM Role (no profile)
        # En desarrollo local: usar profile
        if profile:
            logger.info(f"🔧 Usando AWS profile: {profile}")
            session = boto3.Session(profile_name=profile, region_name=region)
            s3_client = session.client('s3', config=AWS_CONFIG)
        else:
            # Sin profile = usar credenciales del IAM Role automáticamente
            logger.info(f"🔧 Usando IAM Role (credenciales automáticas)")
            s3_client = boto3.client('s3', region_name=region, config=AWS_CONFIG)
        
        return s3_client
        
    except Exception as e:
        logger.error(f"Error creando cliente S3: {e}")
        raise


def upload_product_image(
    imagen_bytes: bytes,
    product_sku: str,
    filename: str,
    extension: str = 'jpg',
    max_reintentos: int = 3
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Sube una imagen de producto a S3 con reintentos automáticos.
    
    Args:
        imagen_bytes: Bytes de la imagen
        product_sku: SKU del producto (para organizar en carpetas)
        filename: Nombre base del archivo
        extension: Extensión del archivo (jpg, png, webp, etc.)
        max_reintentos: Número máximo de intentos (default: 3)
    
    Returns:
        (s3_bucket, s3_key, error_msg)
        Si success: (bucket, key, None)
        Si error después de reintentos: (None, None, error_msg)
    
    Ejemplo de estructura en S3:
        si2-proyectos/si2-ecommerce-images/SKU-12345/main.jpg
        si2-proyectos/si2-ecommerce-images/SKU-12345/variant-1.jpg
    """
    import time
    
    # Normalizar SKU para usar en path (quitar caracteres especiales)
    sku_normalizado = ''.join(c if c.isalnum() or c in ('-', '_') else '-' for c in product_sku)
    
    # Generar timestamp y UUID para evitar colisiones
    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    
    # Construir S3 key
    # Ejemplo: si2-ecommerce-images/SKU-12345/20251111-153045_8f2c0c7a_main.jpg
    filename_safe = filename.replace(' ', '-').lower()
    s3_key = f"{PRODUCTS_BASE_PATH}/{sku_normalizado}/{timestamp}_{unique_id}_{filename_safe}.{extension}"
    
    ultimo_error = None
    s3_client = _get_s3_client()
    
    for intento in range(1, max_reintentos + 1):
        try:
            logger.info(f"📤 Subiendo imagen a S3 (intento {intento}/{max_reintentos}): {BUCKET_NAME}/{s3_key}")
            
            # Determinar Content-Type
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'webp': 'image/webp',
                'gif': 'image/gif'
            }
            content_type = content_type_map.get(extension.lower(), 'application/octet-stream')
            
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=imagen_bytes,
                ContentType=content_type,
                Metadata={
                    'product_sku': sku_normalizado,
                    'uploaded_at': timestamp,
                    'original_filename': filename
                }
            )
            
            logger.info(f"✅ Imagen subida exitosamente en intento {intento}: {s3_key}")
            return BUCKET_NAME, s3_key, None
            
        except ClientError as e:
            ultimo_error = str(e)
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"❌ Error AWS en intento {intento}/{max_reintentos} [{error_code}]: {e}")
            
            # Si no es el último intento, esperar antes de reintentar
            if intento < max_reintentos:
                tiempo_espera = intento * 2  # Backoff exponencial: 2s, 4s, 6s
                logger.info(f"⏳ Esperando {tiempo_espera}s antes del siguiente intento...")
                time.sleep(tiempo_espera)
        
        except Exception as e:
            ultimo_error = str(e)
            logger.error(f"❌ Error inesperado en intento {intento}/{max_reintentos}: {e}", exc_info=True)
            
            if intento < max_reintentos:
                tiempo_espera = intento * 2
                logger.info(f"⏳ Esperando {tiempo_espera}s antes del siguiente intento...")
                time.sleep(tiempo_espera)
    
    # Si llegamos aquí, todos los intentos fallaron
    error_final = f"Falló después de {max_reintentos} intentos. Último error: {ultimo_error}"
    logger.error(f"❌ Upload a S3 FALLÓ DEFINITIVAMENTE: {error_final}")
    return None, None, error_final


def download_image_from_s3(s3_bucket: str, s3_key: str) -> Optional[bytes]:
    """
    Descarga una imagen desde S3
    
    Args:
        s3_bucket: Nombre del bucket
        s3_key: Key del objeto en S3
    
    Returns:
        bytes de la imagen o None si error
    """
    try:
        logger.info(f"📥 Descargando imagen desde S3: {s3_bucket}/{s3_key}")
        
        s3_client = _get_s3_client()
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        imagen_bytes = response['Body'].read()
        
        logger.info(f"✅ Imagen descargada: {len(imagen_bytes)} bytes")
        return imagen_bytes
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"❌ Error AWS descargando imagen [{error_code}]: {e}")
        return None
    
    except Exception as e:
        logger.error(f"❌ Error descargando imagen desde S3: {e}", exc_info=True)
        return None


def delete_image_from_s3(s3_bucket: str, s3_key: str) -> Tuple[bool, Optional[str]]:
    """
    Elimina una imagen de S3
    
    Args:
        s3_bucket: Nombre del bucket
        s3_key: Key del objeto en S3
    
    Returns:
        (success, error_msg)
    """
    try:
        logger.info(f"🗑️ Eliminando imagen de S3: {s3_bucket}/{s3_key}")
        
        s3_client = _get_s3_client()
        s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
        
        logger.info(f"✅ Imagen eliminada exitosamente")
        return True, None
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = f"Error AWS [{error_code}]: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg
    
    except Exception as e:
        logger.error(f"❌ Error eliminando imagen de S3: {e}", exc_info=True)
        return False, str(e)


def generate_presigned_url(s3_bucket: str, s3_key: str, expiration: int = 3600) -> Optional[str]:
    """
    Genera una URL firmada (presigned URL) para acceder temporalmente a una imagen
    
    Args:
        s3_bucket: Nombre del bucket
        s3_key: Key del objeto en S3
        expiration: Tiempo de expiración en segundos (default: 1 hora)
    
    Returns:
        URL firmada o None si error
    """
    try:
        s3_client = _get_s3_client()
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket, 'Key': s3_key},
            ExpiresIn=expiration
        )
        
        return url
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"❌ Error AWS generando URL firmada [{error_code}]: {e}")
        return None
    
    except Exception as e:
        logger.error(f"❌ Error generando URL firmada: {e}", exc_info=True)
        return None


def batch_generate_presigned_urls(
    image_list: list[dict],
    expiration: int = 3600
) -> dict:
    """
    Genera presigned URLs para múltiples imágenes a la vez.
    Útil para cargar listas de productos con imágenes.
    
    Args:
        image_list: Lista de dicts con keys: id, s3_bucket, s3_key
        expiration: Tiempo de expiración en segundos
    
    Returns:
        {
            'urls': {id: url, ...},
            'errors': {id: error_msg, ...}
        }
    """
    urls = {}
    errors = {}
    s3_client = _get_s3_client()
    
    for img in image_list:
        img_id = img.get('id')
        s3_bucket = img.get('s3_bucket')
        s3_key = img.get('s3_key')
        
        if not all([img_id, s3_bucket, s3_key]):
            errors[str(img_id)] = "Datos incompletos (id, s3_bucket o s3_key faltantes)"
            continue
        
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': s3_bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            urls[str(img_id)] = url
            
        except Exception as e:
            errors[str(img_id)] = str(e)
            logger.warning(f"Error generando URL para imagen id={img_id}: {e}")
    
    logger.info(f"✅ Presigned URLs generadas: {len(urls)} exitosas, {len(errors)} errores")
    
    return {
        'urls': urls,
        'errors': errors if errors else None,
        'total_requested': len(image_list),
        'total_success': len(urls),
        'total_errors': len(errors)
    }
