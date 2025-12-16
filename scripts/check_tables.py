import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'si2-ecommmerce'
    ORDER BY table_name
""")

tables = cursor.fetchall()
print("=" * 60)
print(f"TABLAS EN ESQUEMA 'si2-ecommmerce': {len(tables)} tablas")
print("=" * 60)
for table in tables:
    print(f"  - {table[0]}")
print()
