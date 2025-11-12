"""
Django management command to import fashion dataset
Usage: python manage.py import_fashion_dataset

Sube imágenes a S3 bucket: si2-proyectos/si2-ecommerce-images/
"""
import csv
import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from catalog.models import Category, Product, ProductVariant, ProductImage
from apps.core.services.aws_s3 import upload_product_image


class Command(BaseCommand):
    help = 'Importa el dataset de moda con productos e imágenes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='dataset/data.csv',
            help='Ruta al archivo CSV (por defecto: dataset/data.csv)'
        )
        parser.add_argument(
            '--images',
            type=str,
            default='dataset/data/',
            help='Ruta a la carpeta de imágenes (por defecto: dataset/data/)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Límite de productos a importar (por defecto: todos)'
        )
        parser.add_argument(
            '--skip',
            type=int,
            default=0,
            help='Número de filas a saltar (por defecto: 0)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        images_path = options['images']
        limit = options['limit']
        skip = options['skip']
        
        self.stdout.write(self.style.WARNING(f'📂 Leyendo CSV: {csv_path}'))
        self.stdout.write(self.style.WARNING(f'🖼️  Carpeta de imágenes: {images_path}'))
        
        # Verificar que los archivos existen
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'❌ No se encontró el archivo CSV: {csv_path}'))
            return
        
        if not os.path.exists(images_path):
            self.stdout.write(self.style.ERROR(f'❌ No se encontró la carpeta de imágenes: {images_path}'))
            return
        
        # Contadores
        stats = {
            'total': 0,
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'categories': 0
        }
        
        # Mapeo de categorías
        category_cache = {}
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                self.stdout.write(self.style.SUCCESS('\n🚀 Iniciando importación...\n'))
                
                for index, row in enumerate(reader):
                    # Saltar filas iniciales si se especificó
                    if index < skip:
                        continue
                    
                    # Aplicar límite si se especificó
                    if limit and stats['total'] >= limit:
                        break
                    
                    stats['total'] += 1
                    
                    # Mostrar progreso cada 100 productos
                    if stats['total'] % 100 == 0:
                        self.stdout.write(
                            f'📊 Procesados: {stats["total"]} | '
                            f'Creados: {stats["created"]} | '
                            f'Errores: {stats["errors"]}'
                        )
                    
                    try:
                        # Crear o obtener categoría
                        category_name = row['category'].strip()
                        if category_name not in category_cache:
                            category, created = Category.objects.get_or_create(
                                name=category_name,
                                defaults={'parent': None, 'status': 'ACTIVE'}
                            )
                            category_cache[category_name] = category
                            if created:
                                stats['categories'] += 1
                        
                        category = category_cache[category_name]
                        
                        # Preparar datos del producto
                        product_name = row['display name'].strip()[:160]
                        if not product_name:
                            product_name = f"Producto {index}"
                        
                        description = row['description'].strip() if row['description'] else product_name
                        
                        # Generar SKU único
                        base_sku = slugify(product_name)[:40]
                        sku = f"SKU-{base_sku}-{index}"
                        counter = 1
                        while Product.objects.filter(sku=sku).exists():
                            sku = f"SKU-{base_sku}-{index}-{counter}"
                            counter += 1
                        
                        # Generar precio aleatorio basado en la categoría
                        price = self._generate_price(category_name)
                        
                        # Crear producto usando transacción atómica
                        with transaction.atomic():
                            product = Product.objects.create(
                                sku=sku,
                                name=product_name,
                                description=description,
                                base_price=price,
                                brand=category_name,  # Usar categoría como marca temporalmente
                                status='ACTIVE'
                            )
                            
                            # Asignar categoría (M2M)
                            product.categories.add(category)
                            
                            # Crear variante del producto
                            variant = ProductVariant.objects.create(
                                product=product,
                                code=f'VAR-{product.id}-{index}',
                                price=price
                            )
                            
                            # Procesar imagen y subir a S3
                            image_filename = row['image'].strip()
                            image_path = os.path.join(images_path, image_filename)
                            
                            if os.path.exists(image_path):
                                try:
                                    # Leer imagen como bytes
                                    with open(image_path, 'rb') as img_file:
                                        image_bytes = img_file.read()
                                    
                                    # Subir a S3
                                    # Nombre base para S3: main, variant-1, etc.
                                    s3_filename = 'main'
                                    extension = image_filename.split('.')[-1].lower()
                                    
                                    s3_bucket, s3_key, error = upload_product_image(
                                        imagen_bytes=image_bytes,
                                        product_sku=sku,
                                        filename=s3_filename,
                                        extension=extension,
                                        max_reintentos=2  # 2 reintentos para agilizar
                                    )
                                    
                                    if error:
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f'⚠️  Error subiendo a S3 {image_filename}: {error}'
                                            )
                                        )
                                        stats['errors'] += 1
                                    else:
                                        # Crear registro de imagen con S3
                                        ProductImage.objects.create(
                                            product=product,
                                            s3_bucket=s3_bucket,
                                            s3_key=s3_key,
                                            alt=product_name,
                                            is_main=True,
                                            sort=0
                                        )
                                        
                                except Exception as img_error:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'⚠️  No se pudo procesar imagen {image_filename}: {str(img_error)}'
                                        )
                                    )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'⚠️  Imagen no encontrada: {image_filename}')
                                )
                        
                        stats['created'] += 1
                        
                    except Exception as e:
                        stats['errors'] += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ Error en fila {index}: {str(e)}')
                        )
                        continue
                
                # Resumen final
                self.stdout.write(self.style.SUCCESS('\n' + '='*60))
                self.stdout.write(self.style.SUCCESS('🎉 IMPORTACIÓN COMPLETADA'))
                self.stdout.write(self.style.SUCCESS('='*60))
                self.stdout.write(f'📊 Total procesados: {stats["total"]}')
                self.stdout.write(self.style.SUCCESS(f'✓ Productos creados: {stats["created"]}'))
                self.stdout.write(f'📁 Categorías creadas: {stats["categories"]}')
                self.stdout.write(self.style.WARNING(f'⚠ Productos saltados: {stats["skipped"]}'))
                if stats['errors'] > 0:
                    self.stdout.write(self.style.ERROR(f'✗ Errores: {stats["errors"]}'))
                self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error fatal: {str(e)}'))
            raise

    def _generate_price(self, category_name: str) -> Decimal:
        """Genera un precio basado en la categoría del producto"""
        price_ranges = {
            'Sports Shoes': (50, 150),
            'Casual Shoes': (40, 120),
            'Formal Shoes': (60, 200),
            'Heels': (45, 180),
            'Tshirts': (15, 40),
            'Shirts': (25, 70),
            'Jeans': (40, 100),
            'Shorts': (20, 50),
            'Dresses': (35, 150),
            'Kurtis': (30, 80),
            'Jackets': (60, 200),
            'Handbags': (30, 150),
            'Wallets': (15, 60),
            'Watches': (50, 300),
            'Socks': (5, 15),
            'Caps': (10, 30),
            'Ties': (15, 50),
            'Sunglasses': (20, 100),
            'Sarees': (40, 200),
            'Briefs': (8, 25),
            'Earrings': (10, 80),
        }
        
        # Obtener rango de precio o usar default
        price_range = price_ranges.get(category_name, (20, 80))
        
        # Generar precio aleatorio dentro del rango
        price = random.uniform(price_range[0], price_range[1])
        
        # Redondear a 2 decimales
        return Decimal(str(round(price, 2)))
