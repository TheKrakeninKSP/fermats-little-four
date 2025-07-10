from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from ar_tryon.models import Product, ARModel
import json

class Command(BaseCommand):
    help = 'Setup sample AR models for testing'

    def handle(self, *args, **options):
        # Create sample products with AR models
        products_data = [
            {
                'name': 'Premium Cotton T-Shirt',
                'description': 'Comfortable everyday wear',
                'price': 29.99,
                'category': 'shirt',
                'ar_data': {
                    'sizing_data': {
                        'XS': {'chest': 85, 'length': 65},
                        'S': {'chest': 90, 'length': 67},
                        'M': {'chest': 95, 'length': 69},
                        'L': {'chest': 100, 'length': 71},
                        'XL': {'chest': 105, 'length': 73}
                    },
                    'anchor_points': {
                        'shoulders': {'x': 0, 'y': -0.2, 'z': 0},
                        'chest': {'x': 0, 'y': 0, 'z': 0},
                        'waist': {'x': 0, 'y': 0.2, 'z': 0}
                    }
                }
            },
            {
                'name': 'Slim Fit Jeans',
                'description': 'Modern slim fit denim',
                'price': 79.99,
                'category': 'pants',
                'ar_data': {
                    'sizing_data': {
                        '28': {'waist': 71, 'inseam': 81},
                        '30': {'waist': 76, 'inseam': 81},
                        '32': {'waist': 81, 'inseam': 84},
                        '34': {'waist': 86, 'inseam': 84},
                        '36': {'waist': 91, 'inseam': 86}
                    },
                    'anchor_points': {
                        'waist': {'x': 0, 'y': 0, 'z': 0},
                        'hips': {'x': 0, 'y': 0.1, 'z': 0},
                        'knee': {'x': 0, 'y': 0.4, 'z': 0}
                    }
                }
            }
        ]

        for product_data in products_data:
            ar_data = product_data.pop('ar_data')
            category = product_data['category']
            
            # Create product
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            
            if created:
                self.stdout.write(f"Created product: {product.name}")
            
            # Create AR model
            ar_model, created = ARModel.objects.get_or_create(
                product=product,
                defaults={
                    'category': category,
                    'sizing_data': ar_data['sizing_data'],
                    'anchor_points': ar_data['anchor_points'],
                    'scale_factor': 1.0,
                    'rotation_offset': {'x': 0, 'y': 0, 'z': 0}
                }
            )
            
            if created:
                self.stdout.write(f"Created AR model for: {product.name}")

        self.stdout.write(
            self.style.SUCCESS('Successfully setup AR models!')
        )