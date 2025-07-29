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

def add_gold_category_and_products():
    """Add Gold category and sample gold products"""
    
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found. Please create a tenant first.")
            return
        
        # Create Gold category
        gold_category, created = Category.objects.get_or_create(
            name='Gold',
            tenant=tenant,
            defaults={
                'description': 'Gold jewelry items including rings, necklaces, earrings, and more',
                'is_active': True
            }
        )
        
        if created:
            print(f"Created Gold category")
        else:
            print(f"Gold category already exists")
        
        # Sample gold products
        gold_products = [
            {
                'name': '22K Gold Ring',
                'sku': 'GOLD-RING-22K-001',
                'cost_price': Decimal('45000.00'),
                'selling_price': Decimal('55000.00'),
                'quantity': 10,
                'material': '22K Gold',
                'weight': Decimal('8.5'),
                'status': 'active'
            },
            {
                'name': '24K Gold Necklace',
                'sku': 'GOLD-NECK-24K-001',
                'cost_price': Decimal('85000.00'),
                'selling_price': Decimal('95000.00'),
                'quantity': 5,
                'material': '24K Gold',
                'weight': Decimal('15.2'),
                'status': 'active'
            },
            {
                'name': '18K Gold Earrings',
                'sku': 'GOLD-EAR-18K-001',
                'cost_price': Decimal('25000.00'),
                'selling_price': Decimal('32000.00'),
                'quantity': 15,
                'material': '18K Gold',
                'weight': Decimal('4.8'),
                'status': 'active'
            },
            {
                'name': '22K Gold Bracelet',
                'sku': 'GOLD-BRACE-22K-001',
                'cost_price': Decimal('35000.00'),
                'selling_price': Decimal('42000.00'),
                'quantity': 8,
                'material': '22K Gold',
                'weight': Decimal('12.5'),
                'status': 'active'
            },
            {
                'name': '24K Gold Pendant',
                'sku': 'GOLD-PEND-24K-001',
                'cost_price': Decimal('18000.00'),
                'selling_price': Decimal('22000.00'),
                'quantity': 20,
                'material': '24K Gold',
                'weight': Decimal('3.2'),
                'status': 'active'
            }
        ]
        
        created_count = 0
        for product_data in gold_products:
            # Check if product already exists
            existing_product = Product.objects.filter(sku=product_data['sku'], tenant=tenant).first()
            if existing_product:
                print(f"Product already exists: {product_data['name']} ({product_data['sku']})")
                continue
            
            # Create the product
            product = Product.objects.create(
                category=gold_category,
                tenant=tenant,
                **product_data
            )
            created_count += 1
            print(f"Created product: {product.name} in Gold category")
        
        print(f"\nTotal gold products created: {created_count}")
        print(f"Total products in Gold category: {Product.objects.filter(category=gold_category, tenant=tenant).count()}")
        
        # Print all categories and their product counts
        print("\nAll categories and product counts:")
        categories = Category.objects.filter(tenant=tenant)
        for category in categories:
            product_count = Product.objects.filter(category=category, tenant=tenant).count()
            print(f"  {category.name}: {product_count} products")
        
    except Exception as e:
        print(f"Error adding gold category and products: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_gold_category_and_products() 