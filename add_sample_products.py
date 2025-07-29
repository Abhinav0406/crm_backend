#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Category, Product
from apps.tenants.models import Tenant
from decimal import Decimal

def add_sample_products():
    """Add sample products for testing"""
    
    # Get the first tenant
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found. Please create a tenant first.")
            return
        
        # Get categories
        categories = Category.objects.filter(tenant=tenant)
        if not categories.exists():
            print("No categories found. Please run add_sample_categories.py first.")
            return
        
        # Sample products for each category
        sample_products = [
            # Gold category products
            {
                'name': 'Gold Ring 22K',
                'sku': 'GR22K001',
                'category_name': 'Rings',
                'cost_price': Decimal('45000.00'),
                'selling_price': Decimal('55000.00'),
                'quantity': 10,
                'material': '22K Gold',
                'weight': Decimal('8.5'),
                'status': 'active'
            },
            {
                'name': 'Gold Necklace 24K',
                'sku': 'GN24K001',
                'category_name': 'Necklaces',
                'cost_price': Decimal('85000.00'),
                'selling_price': Decimal('95000.00'),
                'quantity': 5,
                'material': '24K Gold',
                'weight': Decimal('15.2'),
                'status': 'active'
            },
            {
                'name': 'Gold Earrings 18K',
                'sku': 'GE18K001',
                'category_name': 'Earrings',
                'cost_price': Decimal('25000.00'),
                'selling_price': Decimal('32000.00'),
                'quantity': 15,
                'material': '18K Gold',
                'weight': Decimal('4.8'),
                'status': 'active'
            },
            {
                'name': 'Gold Bracelet 22K',
                'sku': 'GB22K001',
                'category_name': 'Bracelets',
                'cost_price': Decimal('35000.00'),
                'selling_price': Decimal('42000.00'),
                'quantity': 8,
                'material': '22K Gold',
                'weight': Decimal('12.5'),
                'status': 'active'
            },
            {
                'name': 'Gold Pendant 24K',
                'sku': 'GP24K001',
                'category_name': 'Pendants',
                'cost_price': Decimal('18000.00'),
                'selling_price': Decimal('22000.00'),
                'quantity': 20,
                'material': '24K Gold',
                'weight': Decimal('3.2'),
                'status': 'active'
            },
            # Diamond category products
            {
                'name': 'Diamond Ring 1 Carat',
                'sku': 'DR1C001',
                'category_name': 'Rings',
                'cost_price': Decimal('120000.00'),
                'selling_price': Decimal('150000.00'),
                'quantity': 3,
                'material': '18K White Gold',
                'weight': Decimal('2.1'),
                'status': 'active'
            },
            {
                'name': 'Diamond Necklace 2 Carat',
                'sku': 'DN2C001',
                'category_name': 'Necklaces',
                'cost_price': Decimal('250000.00'),
                'selling_price': Decimal('320000.00'),
                'quantity': 2,
                'material': '18K White Gold',
                'weight': Decimal('4.5'),
                'status': 'active'
            },
            # Silver category products
            {
                'name': 'Silver Anklet',
                'sku': 'SA001',
                'category_name': 'Anklets',
                'cost_price': Decimal('800.00'),
                'selling_price': Decimal('1200.00'),
                'quantity': 25,
                'material': '925 Silver',
                'weight': Decimal('8.0'),
                'status': 'active'
            },
            {
                'name': 'Silver Brooch',
                'sku': 'SB001',
                'category_name': 'Brooches',
                'cost_price': Decimal('500.00'),
                'selling_price': Decimal('800.00'),
                'quantity': 12,
                'material': '925 Silver',
                'weight': Decimal('5.5'),
                'status': 'active'
            }
        ]
        
        created_count = 0
        for product_data in sample_products:
            category_name = product_data.pop('category_name')
            category = categories.filter(name=category_name).first()
            
            if not category:
                print(f"Category '{category_name}' not found, skipping product {product_data['name']}")
                continue
            
            # Check if product already exists
            existing_product = Product.objects.filter(sku=product_data['sku'], tenant=tenant).first()
            if existing_product:
                print(f"Product already exists: {product_data['name']} ({product_data['sku']})")
                continue
            
            # Create the product
            product = Product.objects.create(
                category=category,
                tenant=tenant,
                **product_data
            )
            created_count += 1
            print(f"Created product: {product.name} in category {category.name}")
        
        print(f"\nTotal products created: {created_count}")
        print(f"Total products in database: {Product.objects.filter(tenant=tenant).count()}")
        
        # Print category-product counts
        print("\nCategory-Product counts:")
        for category in categories:
            product_count = Product.objects.filter(category=category, tenant=tenant).count()
            print(f"  {category.name}: {product_count} products")
        
    except Exception as e:
        print(f"Error adding sample products: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_sample_products() 