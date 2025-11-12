"""
Script para poblar la base de datos con datos iniciales para ecommerce de ROPA.
Basado en el dataset Fashion Product Images Dataset.

Ejecutar: python manage.py shell < _project/scripts/populate_fashion_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from catalog.models import Category, Attribute, AttributeValue
from inventory.models import Warehouse
from django.contrib.auth.models import User

print("🧹 Limpiando datos anteriores...")
print("="*60)

# Limpiar datos anteriores (excepto usuarios admin)
AttributeValue.objects.all().delete()
Attribute.objects.all().delete()
Category.objects.all().delete()
Warehouse.objects.all().delete()

print("✅ Base de datos limpia\n")

# ===== CATEGORÍAS DE ROPA (del dataset) =====
print("📁 Creando Categorías de Ropa...")
print("="*60)

fashion_categories = [
    # Calzado
    ("Sports Shoes", "Zapatos deportivos para actividades físicas"),
    ("Casual Shoes", "Zapatos casuales para uso diario"),
    ("Formal Shoes", "Zapatos formales para eventos y oficina"),
    ("Heels", "Zapatos de tacón para mujer"),
    
    # Ropa Superior
    ("Tshirts", "Camisetas casuales de manga corta"),
    ("Shirts", "Camisas formales y casuales"),
    ("Jackets", "Chaquetas y abrigos"),
    ("Kurtis", "Túnicas tradicionales"),
    ("Dresses", "Vestidos para mujer"),
    ("Tunics", "Túnicas modernas"),
    
    # Ropa Inferior
    ("Jeans", "Pantalones de mezclilla"),
    ("Shorts", "Pantalones cortos"),
    ("Sarees", "Saris tradicionales"),
    
    # Accesorios
    ("Handbags", "Bolsos y carteras"),
    ("Wallets", "Billeteras"),
    ("Watches", "Relojes de pulsera"),
    ("Socks", "Calcetines"),
    ("Caps", "Gorras y sombreros"),
    ("Ties", "Corbatas"),
    ("Sunglasses", "Gafas de sol"),
    ("Briefs", "Ropa interior"),
    ("Earrings", "Aretes y pendientes"),
]

categories_created = {}
for name, description in fashion_categories:
    category, created = Category.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'parent': None,
            'status': 'ACTIVE'
        }
    )
    categories_created[name] = category
    print(f"  ✓ {name}")

print(f"\n✅ {len(fashion_categories)} categorías creadas\n")

# ===== ATRIBUTOS ESPECÍFICOS DE MODA =====
print("🏷️  Creando Atributos de Moda...")
print("="*60)

# Atributo: Talla
talla, _ = Attribute.objects.get_or_create(name="Talla")
print(f"  ✓ {talla.name}")

# Atributo: Color
color, _ = Attribute.objects.get_or_create(name="Color")
print(f"  ✓ {color.name}")

# Atributo: Material
material, _ = Attribute.objects.get_or_create(name="Material")
print(f"  ✓ {material.name}")

# Atributo: Género
genero, _ = Attribute.objects.get_or_create(name="Género")
print(f"  ✓ {genero.name}")

# Atributo: Estilo
estilo, _ = Attribute.objects.get_or_create(name="Estilo")
print(f"  ✓ {estilo.name}")

print("\n✅ 5 atributos creados\n")

# ===== VALORES DE ATRIBUTOS =====
print("📋 Creando Valores de Atributos...")
print("="*60)

# Tallas (ropa y calzado)
tallas_ropa = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
tallas_zapatos = ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"]
tallas_valores = tallas_ropa + tallas_zapatos

for valor in tallas_valores:
    AttributeValue.objects.get_or_create(attribute=talla, value=valor)
print(f"  ✓ Talla: {len(tallas_valores)} valores")

# Colores (moda)
colores = [
    "Negro", "Blanco", "Gris", "Azul", "Rojo", "Verde", "Amarillo", 
    "Naranja", "Rosa", "Morado", "Marrón", "Beige", "Plateado", "Dorado",
    "Multicolor", "Azul Marino", "Celeste", "Fucsia", "Turquesa"
]
for valor in colores:
    AttributeValue.objects.get_or_create(attribute=color, value=valor)
print(f"  ✓ Color: {len(colores)} valores")

# Materiales (textiles y accesorios)
materiales = [
    "Algodón", "Poliéster", "Mezclilla", "Cuero", "Cuero Sintético",
    "Lana", "Seda", "Lino", "Nylon", "Spandex", "Terciopelo",
    "Gamuza", "Goma", "Plástico", "Metal", "Tela"
]
for valor in materiales:
    AttributeValue.objects.get_or_create(attribute=material, value=valor)
print(f"  ✓ Material: {len(materiales)} valores")

# Género
generos = ["Hombre", "Mujer", "Unisex", "Niño", "Niña"]
for valor in generos:
    AttributeValue.objects.get_or_create(attribute=genero, value=valor)
print(f"  ✓ Género: {len(generos)} valores")

# Estilos
estilos = [
    "Casual", "Formal", "Deportivo", "Elegante", "Vintage",
    "Moderno", "Clásico", "Bohemio", "Streetwear", "Minimalista"
]
for valor in estilos:
    AttributeValue.objects.get_or_create(attribute=estilo, value=valor)
print(f"  ✓ Estilo: {len(estilos)} valores")

total_valores = len(tallas_valores) + len(colores) + len(materiales) + len(generos) + len(estilos)
print(f"\n✅ {total_valores} valores de atributos creados\n")

# ===== ALMACENES =====
print("🏢 Creando Almacenes...")
print("="*60)

almacenes = [
    ("Almacén Principal", "Santa Cruz", "Zona Central", True),
    ("Almacén Norte", "La Paz", "Zona Norte", True),
    ("Almacén Sur", "Tarija", "Zona Sur", True),
]

for name, city, description, is_active in almacenes:
    warehouse, created = Warehouse.objects.get_or_create(
        name=name,
        defaults={
            'location': city,
            'description': description,
            'is_active': is_active
        }
    )
    print(f"  ✓ {name} ({city})")

print(f"\n✅ {len(almacenes)} almacenes creados\n")

# ===== RESUMEN =====
print("="*60)
print("🎉 POBLACIÓN DE DATOS COMPLETADA")
print("="*60)
print(f"📁 Categorías: {Category.objects.count()}")
print(f"🏷️  Atributos: {Attribute.objects.count()}")
print(f"📋 Valores de atributos: {AttributeValue.objects.count()}")
print(f"🏢 Almacenes: {Warehouse.objects.count()}")
print("="*60)

print("\n✅ ¡Base de datos lista para importar productos de moda!")
print("\n📌 Próximo paso:")
print("   python manage.py import_fashion_dataset --limit 10\n")
