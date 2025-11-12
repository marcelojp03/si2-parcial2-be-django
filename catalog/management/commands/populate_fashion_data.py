"""
Management command para poblar datos iniciales de MODA
Uso: python manage.py populate_fashion_data
"""
from django.core.management.base import BaseCommand
from catalog.models import Category, Attribute, AttributeValue
from inventory.models import Warehouse


class Command(BaseCommand):
    help = 'Pobla la base de datos con categorias, atributos y almacenes para ecommerce de ropa'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🧹 Limpiando datos anteriores...'))
        self.stdout.write('='*60)
        
        # Limpiar datos anteriores
        AttributeValue.objects.all().delete()
        Attribute.objects.all().delete()
        Category.objects.all().delete()
        Warehouse.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Base de datos limpia\n'))
        
        # ===== CATEGORÍAS =====
        self.stdout.write(self.style.WARNING('📁 Creando Categorías de Ropa...'))
        self.stdout.write('='*60)
        
        fashion_categories = [
            "Sports Shoes", "Casual Shoes", "Formal Shoes", "Heels",
            "Tshirts", "Shirts", "Jackets", "Kurtis", "Dresses", "Tunics",
            "Jeans", "Shorts", "Sarees",
            "Handbags", "Wallets", "Watches", "Socks", "Caps", 
            "Ties", "Sunglasses", "Briefs", "Earrings"
        ]
        
        for name in fashion_categories:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'parent': None, 'status': 'ACTIVE'}
            )
            self.stdout.write(f"  ✓ {name}")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(fashion_categories)} categorías creadas\n'))
        
        # ===== ATRIBUTOS =====
        self.stdout.write(self.style.WARNING('🏷️  Creando Atributos...'))
        self.stdout.write('='*60)
        
        talla, _ = Attribute.objects.get_or_create(name="Talla")
        self.stdout.write(f"  ✓ {talla.name}")
        
        color, _ = Attribute.objects.get_or_create(name="Color")
        self.stdout.write(f"  ✓ {color.name}")
        
        material, _ = Attribute.objects.get_or_create(name="Material")
        self.stdout.write(f"  ✓ {material.name}")
        
        genero, _ = Attribute.objects.get_or_create(name="Genero")
        self.stdout.write(f"  ✓ {genero.name}")
        
        estilo, _ = Attribute.objects.get_or_create(name="Estilo")
        self.stdout.write(f"  ✓ {estilo.name}")
        
        self.stdout.write(self.style.SUCCESS('\n✅ 5 atributos creados\n'))
        
        # ===== VALORES DE ATRIBUTOS =====
        self.stdout.write(self.style.WARNING('📋 Creando Valores de Atributos...'))
        self.stdout.write('='*60)
        
        # Tallas
        tallas_valores = ["XS", "S", "M", "L", "XL", "XXL", "36", "37", "38", "39", "40", "41", "42", "43", "44"]
        for valor in tallas_valores:
            AttributeValue.objects.get_or_create(attribute=talla, value=valor)
        self.stdout.write(f"  ✓ Talla: {len(tallas_valores)} valores")
        
        # Colores
        colores = ["Negro", "Blanco", "Gris", "Azul", "Rojo", "Verde", "Amarillo", "Rosa", "Marron", "Beige", "Dorado", "Plateado"]
        for valor in colores:
            AttributeValue.objects.get_or_create(attribute=color, value=valor)
        self.stdout.write(f"  ✓ Color: {len(colores)} valores")
        
        # Materiales
        materiales = ["Algodon", "Poliester", "Mezclilla", "Cuero", "Cuero Sintetico", "Lana", "Seda", "Nylon"]
        for valor in materiales:
            AttributeValue.objects.get_or_create(attribute=material, value=valor)
        self.stdout.write(f"  ✓ Material: {len(materiales)} valores")
        
        # Género
        generos = ["Hombre", "Mujer", "Unisex"]
        for valor in generos:
            AttributeValue.objects.get_or_create(attribute=genero, value=valor)
        self.stdout.write(f"  ✓ Genero: {len(generos)} valores")
        
        # Estilos
        estilos = ["Casual", "Formal", "Deportivo", "Elegante", "Moderno"]
        for valor in estilos:
            AttributeValue.objects.get_or_create(attribute=estilo, value=valor)
        self.stdout.write(f"  ✓ Estilo: {len(estilos)} valores")
        
        total_valores = len(tallas_valores) + len(colores) + len(materiales) + len(generos) + len(estilos)
        self.stdout.write(self.style.SUCCESS(f'\n✅ {total_valores} valores creados\n'))
        
        # ===== ALMACENES =====
        self.stdout.write(self.style.WARNING('🏢 Creando Almacenes...'))
        self.stdout.write('='*60)
        
        almacenes = [
            ("Almacen Principal", "Santa Cruz", "ALM-SC", True),
            ("Almacen Norte", "La Paz", "ALM-LP", True),
            ("Almacen Sur", "Tarija", "ALM-TJ", True),
        ]
        
        for name, location, code, is_active in almacenes:
            warehouse, created = Warehouse.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'location': location,
                    'is_active': is_active
                }
            )
            self.stdout.write(f"  ✓ {name} ({location})")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(almacenes)} almacenes creados\n'))
        
        # ===== RESUMEN =====
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🎉 POBLACION DE DATOS COMPLETADA'))
        self.stdout.write('='*60)
        self.stdout.write(f'📁 Categorias: {Category.objects.count()}')
        self.stdout.write(f'🏷️  Atributos: {Attribute.objects.count()}')
        self.stdout.write(f'📋 Valores: {AttributeValue.objects.count()}')
        self.stdout.write(f'🏢 Almacenes: {Warehouse.objects.count()}')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\n✅ Base de datos lista para importar productos!\n'))
        self.stdout.write(self.style.WARNING('📌 Proximo paso:'))
        self.stdout.write('   python manage.py makemigrations')
        self.stdout.write('   python manage.py migrate')
        self.stdout.write('   python manage.py import_fashion_dataset --limit 10\n')
