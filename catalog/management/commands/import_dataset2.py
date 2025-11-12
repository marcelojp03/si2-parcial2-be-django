"""
Management command to import products from dataset2 (Google Store clothing).

Dataset structure:
- JSON files: mens_tshirts.json, ladies_tshirts.json, mens_outerwear.json, ladies_outerwear.json
- Local images: dataset2/images/shirts/*.jpg
- Each product has 2 images: large (A) and thumbnail (B)

Example JSON:
{
  "name": "YouTube+Organic+Cotton+T-Shirt+-+Grey",
  "title": "YouTube Organic Cotton T-Shirt - Grey",
  "category": "mens_tshirts",
  "price": 14.75,
  "description": "Stay casual and cool in this 100% organic...",
  "image": "/assets/images/shirts/10-13058B.jpg",
  "largeImage": "/assets/images/shirts/10-13058A.jpg"
}
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Product, ProductVariant, ProductImage, Category
from apps.core.services.aws_s3 import upload_product_image
import json
import os
from pathlib import Path
from decimal import Decimal
import time


class Command(BaseCommand):
    help = 'Import products from dataset2 (Google Store clothing)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of products to import per category',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting dataset2 import...'))
        
        limit = options.get('limit')
        if limit:
            self.stdout.write(f'📊 Limit set to {limit} products per category')

        # Base paths
        base_path = Path('dataset2')
        data_path = base_path / 'data'
        images_path = base_path / 'images' / 'shirts'

        if not data_path.exists():
            self.stdout.write(self.style.ERROR('❌ dataset2/data folder not found!'))
            return

        if not images_path.exists():
            self.stdout.write(self.style.ERROR('❌ dataset2/images/shirts folder not found!'))
            return

        # JSON files to process
        json_files = [
            ('mens_tshirts.json', 'Men\'s T-Shirts'),
            ('ladies_tshirts.json', 'Ladies\' T-Shirts'),
            ('mens_outerwear.json', 'Men\'s Outerwear'),
            ('ladies_outerwear.json', 'Ladies\' Outerwear'),
        ]

        total_imported = 0
        total_errors = 0

        for json_file, category_name in json_files:
            self.stdout.write(f'\n📂 Processing {json_file}...')
            
            file_path = data_path / json_file
            if not file_path.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠️  File not found: {json_file}'))
                continue

            # Get or create category
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'parent': None,
                    'status': 'ACTIVE'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created category: {category_name}'))

            # Load products from JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)

            self.stdout.write(f'  📊 Found {len(products_data)} products')

            # Limit if specified
            if limit:
                products_data = products_data[:limit]
                self.stdout.write(f'  📊 Processing only {len(products_data)} products')

            # Import each product
            for idx, product_data in enumerate(products_data, 1):
                try:
                    imported = self._import_product(product_data, category, images_path)
                    if imported:
                        total_imported += 1
                    else:
                        total_errors += 1

                    if idx % 10 == 0:
                        self.stdout.write(f'  ⏳ Progress: {idx}/{len(products_data)}')

                except Exception as e:
                    total_errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Error importing {product_data.get("name", "unknown")}: {str(e)}')
                    )

        # Final summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import completed!'))
        self.stdout.write(self.style.SUCCESS(f'   - Imported: {total_imported} products'))
        if total_errors > 0:
            self.stdout.write(self.style.WARNING(f'   - Errors: {total_errors}'))

    def _import_product(self, data, category, images_path):
        """Import a single product with images to S3."""
        try:
            # Extract data
            name = data['title']
            sku = slugify(data['name'])[:50]  # Use name as SKU
            price = Decimal(str(data['price']))
            description = data.get('description', '')
            
            # Clean HTML entities in description
            description = description.replace('&amp;', '&')
            description = description.replace('&lt;', '<')
            description = description.replace('&gt;', '>')
            description = description.replace('&nbsp;', ' ')

            # Create product
            product = Product.objects.create(
                name=name,
                sku=sku,
                description=description,
                base_price=price,
                brand='Google Store',
                status='ACTIVE'
            )
            product.categories.add(category)

            # Create variant
            variant = ProductVariant.objects.create(
                product=product,
                code=f'{sku}-default',
                price=price,
                status='ACTIVE'
            )

            # Upload images to S3
            image_paths = []
            
            # Large image (A)
            if 'largeImage' in data:
                large_img = data['largeImage'].replace('/assets/images/shirts/', '')
                image_paths.append((large_img, True))  # is_main=True
            
            # Thumbnail (B)
            if 'image' in data:
                thumb_img = data['image'].replace('/assets/images/shirts/', '')
                if thumb_img != image_paths[0][0] if image_paths else True:
                    image_paths.append((thumb_img, False))

            # Upload each image to S3
            for img_filename, is_main in image_paths:
                local_path = images_path / img_filename
                
                if not local_path.exists():
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  Image not found: {img_filename}')
                    )
                    continue

                # Upload to S3 with retries
                s3_bucket, s3_key, uploaded = self._upload_with_retry(
                    str(local_path), 
                    product, 
                    img_filename
                )

                if uploaded:
                    # Create ProductImage record
                    ProductImage.objects.create(
                        product=product,
                        s3_bucket=s3_bucket,
                        s3_key=s3_key,
                        alt=name,
                        is_main=is_main,
                        sort=1 if is_main else 2
                    )

            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error: {str(e)}')
            )
            # Rollback: delete product if created
            try:
                if 'product' in locals():
                    product.delete()
            except:
                pass
            return False

    def _upload_with_retry(self, local_path, product, filename, max_retries=2):
        """Upload image to S3 with retries."""
        try:
            # Read image file as bytes
            with open(local_path, 'rb') as f:
                image_bytes = f.read()
            
            # Get file extension
            extension = os.path.splitext(filename)[1].replace('.', '')
            if not extension:
                extension = 'jpg'
            
            # Upload to S3
            bucket, s3_key, error = upload_product_image(
                imagen_bytes=image_bytes,
                product_sku=slugify(product.name),
                filename=os.path.splitext(filename)[0],
                extension=extension,
                max_reintentos=max_retries + 1
            )
            
            if error:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Failed to upload {filename}: {error}')
                )
                return None, None, False
            
            return bucket, s3_key, True
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Error reading/uploading {filename}: {str(e)}')
            )
            return None, None, False
