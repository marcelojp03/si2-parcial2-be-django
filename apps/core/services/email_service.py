"""
Servicio de envío de correos electrónicos
Utiliza Turbo SMTP configurado en settings.py
"""
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order, customer_email=None):
    """
    Envía correo de confirmación de pedido al cliente.
    
    Args:
        order: Instancia de Order
        customer_email: Email del cliente (opcional, usa order.customer.user.email por defecto)
    
    Returns:
        bool: True si se envió correctamente, False si hubo error
    """
    try:
        # Obtener email del cliente
        if not customer_email:
            customer_email = order.customer.user.email
        
        if not customer_email:
            logger.warning(f"Order {order.order_number} - Cliente sin email")
            return False
        
        # Datos del pedido
        subject = f'✅ Pedido Confirmado #{order.order_number}'
        
        # Construir mensaje HTML
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .order-details {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
                .item {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .total {{ font-size: 1.2em; font-weight: bold; color: #4CAF50; margin-top: 15px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Gracias por tu compra!</h1>
                </div>
                
                <div class="content">
                    <h2>Hola {order.customer.user.get_full_name()},</h2>
                    <p>Tu pedido ha sido <strong>confirmado exitosamente</strong>.</p>
                    
                    <div class="order-details">
                        <h3>📦 Detalles del Pedido</h3>
                        <p><strong>Número de Pedido:</strong> {order.order_number}</p>
                        <p><strong>Fecha:</strong> {order.created_at.strftime('%d/%m/%Y %H:%M')}</p>
                        <p><strong>Estado:</strong> {order.get_status_display()}</p>
                        <p><strong>Estado de Pago:</strong> {order.get_payment_status_display()}</p>
                        
                        <h4 style="margin-top: 20px;">📋 Productos:</h4>
        """
        
        # Agregar items del pedido
        for item in order.items.all():
            html_message += f"""
                        <div class="item">
                            <strong>{item.variant.product.name}</strong> ({item.variant.code})<br>
                            Cantidad: {item.qty} x Bs. {item.unit_price} = <strong>Bs. {item.subtotal}</strong>
                        </div>
            """
        
        # Totales
        html_message += f"""
                        <div class="total">
                            <p>Subtotal: Bs. {order.subtotal}</p>
                            <p>Envío: Bs. {order.shipping_total}</p>
                            <p style="font-size: 1.3em; color: #2E7D32;">TOTAL: Bs. {order.total}</p>
                        </div>
                    </div>
                    
                    <div class="order-details">
                        <h3>📍 Dirección de Envío</h3>
        """
        
        # Dirección de envío
        if order.shipping_address:
            html_message += f"""
                        <p>{order.shipping_address.line1}</p>
                        <p>{order.shipping_address.city}, {order.shipping_address.state}</p>
                        <p>Referencia: {order.shipping_address.notes or 'N/A'}</p>
            """
        else:
            html_message += "<p>Sin dirección especificada</p>"
        
        html_message += """
                    </div>
                    
                    <p style="margin-top: 20px;">
                        Nos pondremos en contacto contigo pronto para coordinar la entrega.
                    </p>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                </div>
                
                <div class="footer">
                    <p>E-commerce SI2 - Sistema de Información 2</p>
                    <p>Este es un correo automático, por favor no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Mensaje de texto plano (fallback)
        plain_message = f"""
¡Gracias por tu compra!

Hola {order.customer.user.get_full_name()},

Tu pedido ha sido confirmado exitosamente.

DETALLES DEL PEDIDO
===================
Número de Pedido: {order.order_number}
Fecha: {order.created_at.strftime('%d/%m/%Y %H:%M')}
Estado: {order.get_status_display()}
Estado de Pago: {order.get_payment_status_display()}

PRODUCTOS
=========
"""
        
        for item in order.items.all():
            plain_message += f"{item.variant.product.name} ({item.variant.code}) - {item.qty} x Bs. {item.unit_price} = Bs. {item.subtotal}\n"
        
        plain_message += f"""
Subtotal: Bs. {order.subtotal}
Envío: Bs. {order.shipping_total}
TOTAL: Bs. {order.total}

DIRECCIÓN DE ENVÍO
==================
"""
        
        if order.shipping_address:
            plain_message += f"{order.shipping_address.line1}\n{order.shipping_address.city}, {order.shipping_address.state}\n"
        else:
            plain_message += "Sin dirección especificada\n"
        
        plain_message += """
Nos pondremos en contacto contigo pronto para coordinar la entrega.

--
E-commerce SI2 - Sistema de Información 2
Este es un correo automático, por favor no responder.
        """
        
        # Enviar correo
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email],
        )
        email.content_subtype = "html"
        email.body = html_message
        
        email.send(fail_silently=False)
        
        logger.info(f"✅ Email enviado a {customer_email} para pedido {order.order_number}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email para pedido {order.order_number}: {e}")
        return False


def send_test_email(recipient_email):
    """
    Envía un correo de prueba simple.
    
    Args:
        recipient_email: Email del destinatario
    
    Returns:
        bool: True si se envió correctamente, False si hubo error
    """
    try:
        subject = '🧪 Email de Prueba - E-commerce SI2'
        
        html_message = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #2196F3; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .success { background: #4CAF50; color: white; padding: 15px; margin: 15px 0; text-align: center; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 Email de Prueba</h1>
                </div>
                
                <div class="content">
                    <div class="success">
                        <h2>✅ ¡El servicio de email funciona correctamente!</h2>
                    </div>
                    
                    <p><strong>Configuración:</strong></p>
                    <ul>
                        <li>Servidor SMTP: pro.eu.turbo-smtp.com</li>
                        <li>Puerto: 465 (SSL)</li>
                        <li>Proveedor: Turbo SMTP</li>
                    </ul>
                    
                    <p>Este mensaje confirma que la configuración de email está funcionando correctamente.</p>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                        <em>E-commerce SI2 - Sistema de Información 2</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = """
🧪 EMAIL DE PRUEBA - E-commerce SI2
===================================

✅ ¡El servicio de email funciona correctamente!

Configuración:
- Servidor SMTP: pro.eu.turbo-smtp.com
- Puerto: 465 (SSL)
- Proveedor: Turbo SMTP

Este mensaje confirma que la configuración de email está funcionando correctamente.

--
E-commerce SI2 - Sistema de Información 2
        """
        
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.content_subtype = "html"
        email.body = html_message
        
        email.send(fail_silently=False)
        
        logger.info(f"✅ Email de prueba enviado a {recipient_email}")
        print(f"✅ Email de prueba enviado exitosamente a {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de prueba: {e}")
        print(f"❌ Error enviando email: {e}")
        return False
