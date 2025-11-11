from django.core.management.base import BaseCommand
from django.db import connection
from decouple import config


class Command(BaseCommand):
    help = 'Crea el schema de PostgreSQL si no existe'

    def handle(self, *args, **options):
        schema_name = config('DB_SCHEMA', default='public')
        
        self.stdout.write(f'Creando schema "{schema_name}" si no existe...')
        
        try:
            with connection.cursor() as cursor:
                # Crear el schema
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
                
                # Otorgar permisos
                db_user = config('DB_USER', default='postgres')
                cursor.execute(f'GRANT ALL PRIVILEGES ON SCHEMA "{schema_name}" TO {db_user}')
                
            self.stdout.write(self.style.SUCCESS(f'✓ Schema "{schema_name}" creado exitosamente'))
            self.stdout.write(f'  Usuario: {db_user}')
            self.stdout.write('\nAhora puedes ejecutar: python manage.py migrate')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error al crear schema: {str(e)}'))
            self.stdout.write('\nPuedes crear el schema manualmente con:')
            self.stdout.write(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";')
            self.stdout.write(f'GRANT ALL PRIVILEGES ON SCHEMA "{schema_name}" TO {db_user};')
