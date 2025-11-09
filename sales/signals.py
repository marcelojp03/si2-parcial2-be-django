"""
Signals para el módulo de ventas.
Automatiza la creación de registros en SaleFact cuando un pedido es pagado.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from sales.models import Order
from analytics.models import SaleFact


@receiver(post_save, sender=Order)
def fill_salefact_on_paid(sender, instance: Order, created, **kwargs):
    """
    Crea registros en SaleFact cuando un pedido cambia a estado PAID.
    Esto alimenta automáticamente los reportes y forecasting.
    """
    # Solo procesar si el pedido cambió a PAID (no en creación inicial)
    if not created and instance.status == 'PAID':
        with transaction.atomic():
            rows = []
            for item in instance.items.select_related('variant__product__category'):
                rows.append(SaleFact(
                    date=instance.created_at.date(),
                    order=instance,
                    product=item.variant.product,
                    variant=item.variant,
                    category=item.variant.product.category,
                    qty=item.qty,
                    unit_price=item.unit_price,
                    revenue=item.qty * item.unit_price,
                    discount=item.discount,
                ))
            
            # Usar bulk_create con ignore_conflicts para evitar duplicados
            # si se confirma el pago múltiples veces
            SaleFact.objects.bulk_create(rows, ignore_conflicts=True)
