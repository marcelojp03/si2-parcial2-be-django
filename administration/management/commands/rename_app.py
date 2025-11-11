"""
Comando para renombrar la app de security a administration en la base de datos.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Renombra las tablas y migraciones de security a administration'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('Actualizando django_migrations...')
            cursor.execute("""
                UPDATE django_migrations 
                SET app = 'administration' 
                WHERE app = 'security'
            """)
            
            self.stdout.write('Renombrando tablas de security_ a administration_...')
            
            # Obtener todas las tablas que empiezan con security_
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'si2-ecommerce' 
                AND table_name LIKE 'security_%'
            """)
            
            tables = cursor.fetchall()
            
            for table in tables:
                old_name = table[0]
                new_name = old_name.replace('security_', 'administration_', 1)
                self.stdout.write(f'  Renombrando {old_name} -> {new_name}')
                cursor.execute(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"')
            
            # Actualizar secuencias
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'si2-ecommerce' 
                AND sequence_name LIKE 'security_%'
            """)
            
            sequences = cursor.fetchall()
            
            for seq in sequences:
                old_name = seq[0]
                new_name = old_name.replace('security_', 'administration_', 1)
                self.stdout.write(f'  Renombrando secuencia {old_name} -> {new_name}')
                cursor.execute(f'ALTER SEQUENCE "{old_name}" RENAME TO "{new_name}"')
            
            self.stdout.write(self.style.SUCCESS('✓ Renombrado completado'))
