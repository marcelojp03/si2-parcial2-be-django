"""
Management command para poblar datos iniciales para dataset2 (Google Store)
Uso: python manage.py populate_dataset2_base
"""
from django.core.management.base import BaseCommand
from catalog.models import Category, Attribute, AttributeValue
from inventory.models import Warehouse


class Command(BaseCommand):
    help = 'Pobla la base de datos con categorías base para dataset2 (Google Store)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmar limpieza de categorías existentes',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Este comando eliminará TODAS las categorías existentes!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Run con --confirm para proceder: python manage.py populate_dataset2_base --confirm'
                )
            )
            return

        self.stdout.write(self.style.WARNING('🧹 Limpiando categorías anteriores...'))
        self.stdout.write('='*60)
        
        # Limpiar solo categorías (mantener atributos y warehouses)
        Category.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Categorías eliminadas\n'))
        
        # ===== CATEGORÍAS DATASET2 =====
        self.stdout.write(self.style.WARNING('📁 Creando Categorías de Google Store...'))
        self.stdout.write('='*60)
        
        # Categorías del dataset2
        dataset2_categories = [
            "Men's T-Shirts",
            "Ladies' T-Shirts",
            "Men's Outerwear",
            "Ladies' Outerwear"
        ]
        
        for name in dataset2_categories:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'parent': None, 'status': 'ACTIVE'}
            )
            action = "✓ Creada" if created else "✓ Existente"
            self.stdout.write(f"  {action}: {name}")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(dataset2_categories)} categorías creadas\n'))
        
        # ===== ATRIBUTOS (si no existen) =====
        self.stdout.write(self.style.WARNING('🏷️  Verificando Atributos...'))
        self.stdout.write('='*60)
        
        attributes = [
            ("Talla", ["XS", "S", "M", "L", "XL", "XXL"]),
            ("Color", ["Black", "White", "Grey", "Blue", "Red", "Green", "Yellow", "Purple", "Pink"]),
            ("Material", ["Cotton", "Polyester", "Fleece", "Nylon", "Blended"]),
            ("Gender", ["Men", "Women", "Unisex"]),
            ("Style", ["Casual", "Sport", "Formal"])
        ]
        
        for attr_name, values in attributes:
            attr, created = Attribute.objects.get_or_create(name=attr_name)
            action = "✓ Creado" if created else "✓ Existente"
            self.stdout.write(f"  {action}: {attr_name}")
            
            # Crear valores
            for value in values:
                AttributeValue.objects.get_or_create(attribute=attr, value=value)
            self.stdout.write(f"    → {len(values)} valores")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(attributes)} atributos verificados\n'))
        
        # ===== WAREHOUSES (si no existen) =====
        self.stdout.write(self.style.WARNING('🏭 Verificando Almacenes...'))
        self.stdout.write('='*60)
        
        warehouses = [
            {"name": "Almacén Principal Santa Cruz", "location": "Santa Cruz, Bolivia", "code": "WH-SCZ"},
            {"name": "Almacén La Paz", "location": "La Paz, Bolivia", "code": "WH-LPZ"},
            {"name": "Almacén Tarija", "location": "Tarija, Bolivia", "code": "WH-TJA"},
        ]
        
        for wh_data in warehouses:
            wh, created = Warehouse.objects.get_or_create(
                code=wh_data['code'],
                defaults={
                    'name': wh_data['name'],
                    'location': wh_data['location']
                }
            )
            action = "✓ Creado" if created else "✓ Existente"
            self.stdout.write(f"  {action}: {wh_data['name']}")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ {len(warehouses)} almacenes verificados\n'))
        
        # ===== RESUMEN =====
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Base de datos lista para dataset2!'))
        self.stdout.write('='*60)
        self.stdout.write(f"📁 Categorías: {Category.objects.count()}")
        self.stdout.write(f"🏷️  Atributos: {Attribute.objects.count()}")
        self.stdout.write(f"📋 Valores: {AttributeValue.objects.count()}")
        self.stdout.write(f"🏭 Almacenes: {Warehouse.objects.count()}")
        self.stdout.write('='*60)
        self.stdout.write(self.style.WARNING('\n▶️  Siguiente paso:'))
        self.stdout.write('   python manage.py import_dataset2')
        self.stdout.write('')
