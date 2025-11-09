from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Carga datos iniciales (categorías, atributos, almacenes)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Cargando datos iniciales...'))
        
        try:
            call_command('loaddata', 'fixtures/initial_data.json')
            self.stdout.write(self.style.SUCCESS('✓ Datos iniciales cargados exitosamente'))
            
            self.stdout.write('\nDatos cargados:')
            self.stdout.write('  - 6 Categorías (Electrónica, Laptops, Smartphones, Ropa, Camisetas, Pantalones)')
            self.stdout.write('  - 4 Atributos (Talla, Color, Memoria RAM, Almacenamiento)')
            self.stdout.write('  - 14 Valores de Atributos')
            self.stdout.write('  - 3 Almacenes (Central, Norte, La Paz)')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error al cargar datos: {str(e)}'))
