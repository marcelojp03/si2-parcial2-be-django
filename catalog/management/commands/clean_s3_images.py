"""
Management command to delete all product images from S3 bucket.
"""
from django.core.management.base import BaseCommand
from apps.core.services.aws_s3 import _get_s3_client
import boto3
from botocore.config import Config
from django.conf import settings


class Command(BaseCommand):
    help = 'Delete all product images from S3 bucket'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all S3 images',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  This will DELETE ALL images from S3 bucket!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Run with --confirm flag to proceed: python manage.py clean_s3_images --confirm'
                )
            )
            return

        self.stdout.write(self.style.WARNING('🗑️  Starting S3 cleanup...'))

        try:
            # Get S3 client
            s3_client = _get_s3_client()
            bucket_name = 'si2-proyectos'
            prefix = 'si2-ecommerce-images/'

            # List all objects in the prefix
            self.stdout.write(f'📋 Listing objects in {bucket_name}/{prefix}...')
            
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            deleted_count = 0
            objects_to_delete = []

            for page in pages:
                if 'Contents' not in page:
                    continue

                for obj in page['Contents']:
                    objects_to_delete.append({'Key': obj['Key']})
                    deleted_count += 1

                    # Delete in batches of 1000 (S3 limit)
                    if len(objects_to_delete) >= 1000:
                        s3_client.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': objects_to_delete}
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Deleted {len(objects_to_delete)} objects')
                        )
                        objects_to_delete = []

            # Delete remaining objects
            if objects_to_delete:
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Deleted {len(objects_to_delete)} objects')
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully deleted {deleted_count} images from S3!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Error cleaning S3: {str(e)}')
            )
            raise
