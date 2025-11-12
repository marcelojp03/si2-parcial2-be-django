"""
Management command to clean database - remove all products, variants, and images.
Keeps categories, attributes, and warehouses intact.
"""
from django.core.management.base import BaseCommand
from catalog.models import Product, ProductVariant, ProductImage


class Command(BaseCommand):
    help = 'Clean database: remove all products, variants, and images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all products',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  This will DELETE ALL products, variants, and images from database!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Run with --confirm flag to proceed: python manage.py clean_products --confirm'
                )
            )
            return

        self.stdout.write(self.style.WARNING('🗑️  Starting database cleanup...'))

        try:
            # Count before deletion
            product_count = Product.objects.count()
            variant_count = ProductVariant.objects.count()
            image_count = ProductImage.objects.count()

            self.stdout.write(f'📊 Current counts:')
            self.stdout.write(f'   - Products: {product_count}')
            self.stdout.write(f'   - Variants: {variant_count}')
            self.stdout.write(f'   - Images: {image_count}')

            # Delete all (cascade will handle variants and images)
            self.stdout.write('\n🗑️  Deleting all product images...')
            ProductImage.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {image_count} images'))

            self.stdout.write('🗑️  Deleting all product variants...')
            ProductVariant.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {variant_count} variants'))

            self.stdout.write('🗑️  Deleting all products...')
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {product_count} products'))

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Database cleaned successfully!'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '   Categories, attributes, and warehouses were preserved.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error cleaning database: {str(e)}')
            )
            raise
