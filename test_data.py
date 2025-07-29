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
from apps.products.serializers import ProductListSerializer, CategorySerializer

def test_data_structure():
    """Test the data structure to debug the issue"""
    
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found.")
            return
        
        print("=== TESTING DATA STRUCTURE ===")
        
        # Test categories
        print("\n1. Categories:")
        categories = Category.objects.filter(tenant=tenant)
        for cat in categories:
            print(f"  - {cat.name} (ID: {cat.id})")
        
        # Test Gold category specifically
        gold_category = categories.filter(name='Gold').first()
        if gold_category:
            print(f"\n2. Gold Category Details:")
            print(f"  - Name: {gold_category.name}")
            print(f"  - ID: {gold_category.id}")
            print(f"  - Active: {gold_category.is_active}")
            
            # Test products in Gold category
            gold_products = Product.objects.filter(category=gold_category, tenant=tenant)
            print(f"  - Products count: {gold_products.count()}")
            for prod in gold_products:
                print(f"    * {prod.name} (ID: {prod.id}, Category ID: {prod.category.id})")
        else:
            print("Gold category not found!")
        
        # Test serializer output
        print(f"\n3. Serializer Test:")
        if gold_products.exists():
            product = gold_products.first()
            serializer = ProductListSerializer(product)
            print(f"  - Product: {product.name}")
            print(f"  - Serialized data: {serializer.data}")
            print(f"  - Category field: {serializer.data.get('category')}")
            print(f"  - Category type: {type(serializer.data.get('category'))}")
        
        # Test all products
        print(f"\n4. All Products:")
        all_products = Product.objects.filter(tenant=tenant)
        for prod in all_products:
            print(f"  - {prod.name} (Category: {prod.category.name}, Category ID: {prod.category.id})")
        
    except Exception as e:
        print(f"Error testing data structure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_data_structure() 