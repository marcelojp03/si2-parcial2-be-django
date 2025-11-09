"""
Script para poblar la base de datos con datos iniciales.
Ejecutar con: python populate_db.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from catalog.models import Category, Attribute, AttributeValue
from inventory.models import Warehouse

print("=" * 60)
print("POBLANDO BASE DE DATOS CON DATOS INICIALES")
print("=" * 60)

# Categorías
print("\n📁 Creando Categorías...")
electronica, _ = Category.objects.get_or_create(
    name="Electrónica",
    defaults={'parent': None, 'status': 'ACTIVE'}
)
print(f"  ✓ {electronica.name}")

laptops, _ = Category.objects.get_or_create(
    name="Laptops",
    defaults={'parent': electronica, 'status': 'ACTIVE'}
)
print(f"  ✓ {laptops.name}")

smartphones, _ = Category.objects.get_or_create(
    name="Smartphones",
    defaults={'parent': electronica, 'status': 'ACTIVE'}
)
print(f"  ✓ {smartphones.name}")

ropa, _ = Category.objects.get_or_create(
    name="Ropa",
    defaults={'parent': None, 'status': 'ACTIVE'}
)
print(f"  ✓ {ropa.name}")

camisetas, _ = Category.objects.get_or_create(
    name="Camisetas",
    defaults={'parent': ropa, 'status': 'ACTIVE'}
)
print(f"  ✓ {camisetas.name}")

pantalones, _ = Category.objects.get_or_create(
    name="Pantalones",
    defaults={'parent': ropa, 'status': 'ACTIVE'}
)
print(f"  ✓ {pantalones.name}")

# Atributos
print("\n🏷️  Creando Atributos...")
talla, _ = Attribute.objects.get_or_create(name="Talla")
print(f"  ✓ {talla.name}")

color, _ = Attribute.objects.get_or_create(name="Color")
print(f"  ✓ {color.name}")

ram, _ = Attribute.objects.get_or_create(name="Memoria RAM")
print(f"  ✓ {ram.name}")

storage, _ = Attribute.objects.get_or_create(name="Almacenamiento")
print(f"  ✓ {storage.name}")

# Valores de Atributos
print("\n📋 Creando Valores de Atributos...")

# Tallas
for valor in ["S", "M", "L", "XL"]:
    AttributeValue.objects.get_or_create(attribute=talla, value=valor)
    print(f"  ✓ Talla: {valor}")

# Colores
for valor in ["Rojo", "Azul", "Negro", "Blanco", "Verde", "Gris"]:
    AttributeValue.objects.get_or_create(attribute=color, value=valor)
    print(f"  ✓ Color: {valor}")

# RAM
for valor in ["8GB", "16GB", "32GB", "64GB"]:
    AttributeValue.objects.get_or_create(attribute=ram, value=valor)
    print(f"  ✓ RAM: {valor}")

# Almacenamiento
for valor in ["128GB", "256GB", "512GB", "1TB", "2TB"]:
    AttributeValue.objects.get_or_create(attribute=storage, value=valor)
    print(f"  ✓ Almacenamiento: {valor}")

# Almacenes
print("\n🏢 Creando Almacenes...")

wh1, _ = Warehouse.objects.get_or_create(
    code="WH-SC-01",
    defaults={
        'name': "Almacén Central",
        'location': "Av. Cristo Redentor #123, Santa Cruz",
        'is_active': True
    }
)
print(f"  ✓ {wh1.code} - {wh1.name}")

wh2, _ = Warehouse.objects.get_or_create(
    code="WH-SC-02",
    defaults={
        'name': "Almacén Norte",
        'location': "4to Anillo Norte, Santa Cruz",
        'is_active': True
    }
)
print(f"  ✓ {wh2.code} - {wh2.name}")

wh3, _ = Warehouse.objects.get_or_create(
    code="WH-LP-01",
    defaults={
        'name': "Almacén La Paz",
        'location': "Zona Sur, La Paz",
        'is_active': True
    }
)
print(f"  ✓ {wh3.code} - {wh3.name}")

print("\n" + "=" * 60)
print("✅ DATOS INICIALES CARGADOS EXITOSAMENTE")
print("=" * 60)
print(f"\nResumen:")
print(f"  - {Category.objects.count()} Categorías")
print(f"  - {Attribute.objects.count()} Atributos")
print(f"  - {AttributeValue.objects.count()} Valores de Atributos")
print(f"  - {Warehouse.objects.count()} Almacenes")
print()
