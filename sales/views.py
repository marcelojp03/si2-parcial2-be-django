from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid
from .models import Address, Cart, CartItem, Order, OrderItem, Payment
from customers.models import Customer
from .serializers import (
    AddressSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    AddToCartSerializer,
    PaymentSerializer
)
from catalog.models import ProductVariant
from inventory.models import Inventory


@extend_schema_view(
    list=extend_schema(summary="Listar direcciones", tags=['Sales']),
    retrieve=extend_schema(summary="Obtener dirección", tags=['Sales']),
    create=extend_schema(summary="Crear dirección", tags=['Sales']),
    update=extend_schema(summary="Actualizar dirección", tags=['Sales'])
)
class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar direcciones"""
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset


@extend_schema_view(
    list=extend_schema(summary="Listar carritos", tags=['Sales']),
    retrieve=extend_schema(summary="Obtener carrito", tags=['Sales'])
)
class CartViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestionar carritos"""
    queryset = Cart.objects.prefetch_related('items__variant__product').all()
    serializer_class = CartSerializer
    
    @extend_schema(
        summary="Agregar item al carrito",
        request=AddToCartSerializer,
        tags=['Sales']
    )
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Agrega un item al carrito"""
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        
        if serializer.is_valid():
            variant_id = serializer.validated_data['variant_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                
                # Verificar si ya existe en el carrito
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    variant=variant,
                    defaults={'qty': quantity, 'unit_price': variant.price}
                )
                
                if not created:
                    cart_item.qty += quantity
                    cart_item.save()
                
                cart_serializer = CartSerializer(cart)
                return Response(cart_serializer.data)
                
            except ProductVariant.DoesNotExist:
                return Response(
                    {'error': 'Variante no encontrada'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(summary="Eliminar item del carrito", tags=['Sales'])
    @action(detail=True, methods=['post'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """Elimina un item del carrito"""
        cart = self.get_object()
        
        # Validar que item_id no sea undefined o None
        if not item_id or item_id == 'undefined':
            return Response(
                {'error': 'Item ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data)
        except (CartItem.DoesNotExist, ValueError):
            return Response(
                {'error': 'Item no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(summary="Vaciar carrito", tags=['Sales'])
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Vacía el carrito"""
        cart = self.get_object()
        cart.items.all().delete()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
    @extend_schema(
        summary="Crear pedido desde carrito",
        request=OrderCreateSerializer,
        tags=['Sales']
    )
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        Crea un pedido desde el carrito.
        Acepta shipping_address_id (dirección existente) o shipping_address (crear nueva)
        """
        cart = self.get_object()
        serializer = OrderCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not cart.items.exists():
            return Response(
                {'error': 'El carrito está vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Determinar o crear la dirección de envío
                shipping_address_id = serializer.validated_data.get('shipping_address_id')
                shipping_address_data = serializer.validated_data.get('shipping_address')
                
                if shipping_address_data:
                    # Crear nueva dirección
                    address = Address.objects.create(
                        customer_id=serializer.validated_data['customer_id'],
                        line1=shipping_address_data['line1'],
                        city=shipping_address_data['city'],
                        state=shipping_address_data.get('state', ''),
                        zip=shipping_address_data.get('zip', ''),
                        notes=shipping_address_data.get('notes', ''),
                        is_default=shipping_address_data.get('is_default', False)
                    )
                    shipping_address_id = address.id
                
                # Generar número de orden único (max 20 chars)
                # Formato: YYYYMMDD-XXXXXXXX (8+1+8 = 17 chars)
                order_number = f"{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
                
                # Crear pedido
                order = Order.objects.create(
                    customer_id=serializer.validated_data['customer_id'],
                    shipping_address_id=shipping_address_id,
                    order_number=order_number,
                    status='CREATED',
                    payment_status='PENDING'
                )
                
                # Crear items del pedido y reservar stock
                subtotal = 0
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        variant=cart_item.variant,
                        qty=cart_item.qty,
                        unit_price=cart_item.unit_price
                    )
                    subtotal += cart_item.qty * cart_item.unit_price
                    
                    # Reservar stock del primer almacén disponible
                    inventory = Inventory.objects.filter(
                        variant=cart_item.variant,
                        stock_on_hand__gte=cart_item.qty
                    ).first()
                    
                    if inventory:
                        inventory.reserve_stock(cart_item.qty)
                
                # Calcular totales (usando los nombres de campos correctos del modelo)
                tax = subtotal * Decimal('0.13')  # 13% IVA (Bolivia)
                order.subtotal = subtotal
                order.shipping_total = Decimal(str(serializer.validated_data.get('shipping_cost', 0)))
                order.discount_total = Decimal(str(serializer.validated_data.get('discount', 0)))
                order.total = subtotal + tax + order.shipping_total - order.discount_total
                order.save()
                
                # Crear pago
                payment_provider = serializer.validated_data.get('payment_provider', 'MOCK')
                
                payment = Payment.objects.create(
                    order=order,
                    provider=payment_provider,
                    amount=order.total,
                    status='PENDING'
                )
                
                # VPAY: Generar QR de pago
                vpay_qr_data = None
                if payment_provider == 'VPAY':
                    from apps.core.services.vpay_service import generate_vpay_qr
                    
                    vpay_result = generate_vpay_qr(order)
                    
                    if vpay_result['success']:
                        # Guardar QR ID en payment.provider_ref
                        payment.provider_ref = vpay_result['qr_id']
                        payment.save()
                        
                        # Preparar datos para enviar al frontend
                        vpay_qr_data = {
                            'qr_id': vpay_result['qr_id'],
                            'qr_image': vpay_result['qr_image'],  # Base64
                            'expiration_date': vpay_result['expiration_date']
                        }
                        
                        logger.info(f"✅ QR VPAY generado para pedido {order.order_number}")
                    else:
                        # Si falla generar QR, cancelar pedido
                        order.status = 'CANCELLED'
                        order.save()
                        return Response(
                            {'error': f"Error generando QR VPAY: {vpay_result.get('error')}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                
                # AUTO-CONFIRMAR pago para métodos simulados
                # VPAY NO auto-confirma, espera polling del frontend
                should_auto_confirm = payment_provider in ['MOCK', 'QR']
                
                if should_auto_confirm:
                    # Confirmar pago
                    payment.status = 'SUCCESS'
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Actualizar estado del pedido
                    order.status = 'CONFIRMED'
                    order.payment_status = 'PAID'
                    order.save()
                    
                    # Confirmar venta: decrementar stock_on_hand y stock_reserved
                    for order_item in order.items.all():
                        inventory = Inventory.objects.filter(
                            variant=order_item.variant
                        ).first()
                        
                        if inventory:
                            inventory.confirm_sale(order_item.qty)
                    
                    # Enviar email de confirmación
                    try:
                        from apps.core.services.email_service import send_order_confirmation_email
                        send_order_confirmation_email(order)
                    except Exception as email_error:
                        # No fallar el checkout si falla el email
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Error enviando email de confirmación: {email_error}")
                
                # Vaciar carrito
                cart.items.all().delete()
                
                order_serializer = OrderSerializer(order)
                response_data = order_serializer.data
                
                # Si es VPAY, agregar datos del QR a la respuesta
                if vpay_qr_data:
                    response_data['vpay_qr'] = vpay_qr_data
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    list=extend_schema(summary="Listar pedidos", tags=['Sales']),
    retrieve=extend_schema(summary="Obtener pedido", tags=['Sales'])
)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestionar pedidos"""
    queryset = Order.objects.prefetch_related('items__variant__product', 'payment').all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'customer__user__first_name', 'customer__user__last_name', 'customer__user__email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        order_status = self.request.query_params.get('status')
        if order_status:
            queryset = queryset.filter(status=order_status)
        
        return queryset
    
    @extend_schema(summary="Confirmar pago del pedido", tags=['Sales'])
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirma el pago de un pedido con idempotencia y bloqueo pesimista"""
        idempotency_key = request.data.get('idempotency_key', '')
        
        try:
            with transaction.atomic():
                # Bloquear el pedido para evitar confirmaciones concurrentes
                order = Order.objects.select_for_update().get(pk=pk)
                
                # Validar estado del pedido
                if order.status != 'CREATED':
                    return Response(
                        {'error': f'Estado inválido para confirmar pago. Estado actual: {order.status}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Obtener o crear el pago con idempotencia
                payment, created = Payment.objects.get_or_create(
                    order=order,
                    defaults={
                        'provider': request.data.get('provider', 'MOCK'),
                        'status': 'INIT',
                        'amount': order.total
                    }
                )
                
                # Verificar idempotencia - si ya fue procesado con esta clave, retornar el resultado
                if payment.idempotency_key == idempotency_key and payment.status == 'SUCCESS':
                    order_serializer = OrderSerializer(order)
                    return Response({
                        'message': 'Pago ya confirmado previamente',
                        'order': order_serializer.data
                    })
                
                # Guardar clave de idempotencia
                payment.idempotency_key = idempotency_key
                
                # Obtener IDs de variantes para bloquear inventarios
                variant_ids = list(order.items.values_list('variant_id', flat=True))
                
                # Bloquear inventarios de todas las variantes involucradas
                inventories = Inventory.objects.select_for_update().filter(
                    variant_id__in=variant_ids
                )
                
                # Crear un mapa de inventarios por variante
                inv_map = {}
                for inv in inventories:
                    key = inv.variant_id
                    if key not in inv_map or inv.stock_available > inv_map[key].stock_available:
                        inv_map[key] = inv
                
                # Validar y confirmar cada item
                for item in order.items.all():
                    inventory = inv_map.get(item.variant_id)
                    
                    if not inventory:
                        raise ValueError(f'Inventario no encontrado para {item.variant.code}')
                    
                    # Validar que hay suficiente stock reservado y disponible
                    if inventory.stock_reserved < item.qty or inventory.stock_on_hand < item.qty:
                        raise ValueError(
                            f'Stock insuficiente para {item.variant.code}. '
                            f'Disponible: {inventory.stock_on_hand}, Reservado: {inventory.stock_reserved}'
                        )
                    
                    # Confirmar la venta: decrementar stock_on_hand y stock_reserved
                    inventory.stock_on_hand -= item.qty
                    inventory.stock_reserved -= item.qty
                    inventory.save(update_fields=['stock_on_hand', 'stock_reserved', 'updated_at'])
                
                # Actualizar pago
                payment.status = 'SUCCESS'
                payment.paid_at = timezone.now()
                payment.provider_ref = request.data.get('provider_ref', '')
                payment.save(update_fields=['status', 'paid_at', 'provider_ref', 'idempotency_key'])
                
                # Actualizar pedido
                order.payment_status = 'PAID'
                order.status = 'PAID'
                order.save(update_fields=['payment_status', 'status', 'updated_at'])
                
                order_serializer = OrderSerializer(order)
                return Response({
                    'message': 'Pago confirmado exitosamente',
                    'order': order_serializer.data
                })
                
        except Order.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al confirmar pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Consultar estado de pago VPAY",
        tags=['Sales'],
        description="Consulta el estado del QR de VPAY y auto-confirma si está pagado (status=PAG)"
    )
    @action(detail=True, methods=['get'], url_path='check-vpay-payment')
    def check_vpay_payment(self, request, pk=None):
        """
        Endpoint de polling para verificar el estado del pago VPAY.
        Frontend debe llamar cada 3-5 segundos hasta que status sea 'PAID'.
        """
        try:
            order = Order.objects.select_related('payment').get(pk=pk)
            
            # Validar que el pedido tiene un pago con VPAY
            if not hasattr(order, 'payment'):
                return Response(
                    {'error': 'Pedido sin pago asociado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payment = order.payment
            
            if payment.provider != 'VPAY':
                return Response(
                    {'error': 'Este endpoint solo funciona para pagos VPAY'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Si ya está confirmado, retornar estado
            if payment.status == 'SUCCESS':
                return Response({
                    'payment_status': 'PAID',
                    'order_status': order.status,
                    'paid_at': payment.paid_at,
                    'message': 'Pago ya confirmado'
                })
            
            # Verificar que tiene QR ID
            if not payment.provider_ref:
                return Response(
                    {'error': 'Pago VPAY sin QR ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Consultar estado en VPAY
            from apps.core.services.vpay_service import check_vpay_payment_status
            
            result = check_vpay_payment_status(payment.provider_ref)
            
            if not result['success']:
                return Response(
                    {'error': f"Error consultando VPAY: {result.get('error')}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Si está pagado (status=PAG), auto-confirmar
            if result['is_paid']:
                with transaction.atomic():
                    # Confirmar pago
                    payment.status = 'SUCCESS'
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Actualizar pedido
                    order.status = 'CONFIRMED'
                    order.payment_status = 'PAID'
                    order.save()
                    
                    # Confirmar venta (decrementar stock)
                    for order_item in order.items.all():
                        inventory = Inventory.objects.filter(
                            variant=order_item.variant
                        ).first()
                        
                        if inventory:
                            inventory.confirm_sale(order_item.qty)
                    
                    # Enviar email de confirmación
                    try:
                        from apps.core.services.email_service import send_order_confirmation_email
                        send_order_confirmation_email(order)
                    except Exception as email_error:
                        logger.warning(f"Error enviando email: {email_error}")
                
                return Response({
                    'payment_status': 'PAID',
                    'order_status': 'CONFIRMED',
                    'paid_at': payment.paid_at,
                    'message': '¡Pago confirmado exitosamente!'
                })
            
            # Aún pendiente (status=PEN)
            return Response({
                'payment_status': 'PENDING',
                'order_status': order.status,
                'vpay_status': result['status'],
                'message': 'Esperando confirmación de pago'
            })
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error verificando pago VPAY: {e}")
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(summary="Cancelar pedido", tags=['Sales'])
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela un pedido con validación de estados y liberación de stock"""
        try:
            with transaction.atomic():
                # Bloquear el pedido
                order = Order.objects.select_for_update().get(pk=pk)
                
                # Validar que el pedido puede ser cancelado
                if order.status in ['SHIPPED', 'DELIVERED']:
                    return Response(
                        {'error': 'No se puede cancelar un pedido enviado o entregado'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if order.status == 'CANCELLED':
                    return Response(
                        {'error': 'El pedido ya fue cancelado'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Obtener IDs de variantes
                variant_ids = list(order.items.values_list('variant_id', flat=True))
                
                # Bloquear inventarios
                inventories = Inventory.objects.select_for_update().filter(
                    variant_id__in=variant_ids
                )
                
                inv_map = {inv.variant_id: inv for inv in inventories}
                
                # Liberar stock reservado
                for item in order.items.all():
                    inventory = inv_map.get(item.variant_id)
                    
                    if inventory and inventory.stock_reserved >= item.qty:
                        inventory.stock_reserved -= item.qty
                        inventory.save(update_fields=['stock_reserved', 'updated_at'])
                
                # Actualizar estado del pedido
                order.status = 'CANCELLED'
                order.save(update_fields=['status', 'updated_at'])
                
                # Cancelar pago si existe
                try:
                    payment = order.payment
                    if payment.status not in ['SUCCESS', 'FAILED']:
                        payment.status = 'CANCELLED'
                        payment.save(update_fields=['status'])
                except Payment.DoesNotExist:
                    pass
                
                order_serializer = OrderSerializer(order)
                return Response({
                    'message': 'Pedido cancelado exitosamente',
                    'order': order_serializer.data
                })
                
        except Order.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al cancelar pedido: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
