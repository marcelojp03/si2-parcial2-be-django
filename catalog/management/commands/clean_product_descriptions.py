"""
Management command para limpiar HTML de las descripciones de productos
"""
import re
from html import unescape
from django.core.management.base import BaseCommand
from catalog.models import Product


class Command(BaseCommand):
    help = 'Limpia las etiquetas HTML de las descripciones de productos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar la limpieza de descripciones',
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Mostrar preview sin aplicar cambios',
        )

    def clean_html(self, text):
        """
        Limpia HTML de un texto manteniendo el formato legible
        """
        if not text:
            return text
        
        # Decodificar entidades HTML
        text = unescape(text)
        
        # Reemplazar <br>, <br/>, <br /> con saltos de línea
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        
        # Reemplazar </div> con saltos de línea
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        
        # Reemplazar </li> con salto de línea + bullet point
        text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
        
        # Reemplazar <li> con bullet point
        text = re.sub(r'<li>', '• ', text, flags=re.IGNORECASE)
        
        # Remover todas las demás etiquetas HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Limpiar múltiples saltos de línea consecutivos
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Limpiar espacios al inicio y final de cada línea
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text.strip()

    def handle(self, *args, **options):
        confirm = options['confirm']
        preview = options['preview']
        
        if not confirm and not preview:
            self.stdout.write(self.style.WARNING(
                '⚠️  Este comando limpiará el HTML de todas las descripciones de productos.'
            ))
            self.stdout.write(self.style.WARNING(
                '   Usa --preview para ver los cambios sin aplicarlos'
            ))
            self.stdout.write(self.style.WARNING(
                '   Usa --confirm para aplicar los cambios'
            ))
            return
        
        products = Product.objects.all()
        total = products.count()
        
        self.stdout.write(self.style.HTTP_INFO(
            f'\n📊 Total de productos: {total}\n'
        ))
        
        updated_count = 0
        unchanged_count = 0
        
        for product in products:
            original = product.description
            cleaned = self.clean_html(original)
            
            if original != cleaned:
                if preview:
                    self.stdout.write(self.style.WARNING(
                        f'\n{"="*80}'
                    ))
                    self.stdout.write(self.style.HTTP_INFO(
                        f'Producto: {product.name} (ID: {product.id})'
                    ))
                    self.stdout.write(self.style.WARNING('\nANTES:'))
                    self.stdout.write(original[:200] + '...' if len(original) > 200 else original)
                    self.stdout.write(self.style.SUCCESS('\nDESPUÉS:'))
                    self.stdout.write(cleaned[:200] + '...' if len(cleaned) > 200 else cleaned)
                    self.stdout.write('')
                    updated_count += 1
                elif confirm:
                    product.description = cleaned
                    product.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Actualizado: {product.name} (ID: {product.id})'
                    ))
                    updated_count += 1
            else:
                unchanged_count += 1
        
        # Resumen
        self.stdout.write(self.style.HTTP_INFO(
            f'\n{"="*80}'
        ))
        self.stdout.write(self.style.HTTP_INFO('RESUMEN'))
        self.stdout.write(self.style.HTTP_INFO(
            f'{"="*80}\n'
        ))
        
        if preview:
            self.stdout.write(self.style.WARNING(
                f'📋 Productos que se actualizarían: {updated_count}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'✓ Productos sin cambios: {unchanged_count}'
            ))
            self.stdout.write(self.style.HTTP_INFO(
                f'\n▶️  Para aplicar los cambios, ejecuta:'
            ))
            self.stdout.write(self.style.HTTP_INFO(
                '   python manage.py clean_product_descriptions --confirm\n'
            ))
        elif confirm:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Productos actualizados: {updated_count}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'✓ Productos sin cambios: {unchanged_count}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'\n🎉 Limpieza completada exitosamente!\n'
            ))
