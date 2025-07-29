#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Category
from apps.tenants.models import Tenant
from apps.users.models import User

def add_sample_categories():
    """Add sample categories for testing"""
    
    # Get the first tenant (or create one if needed)
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found. Please create a tenant first.")
            return
        
        # Sample categories for jewelry business
        sample_categories = [
            {
                'name': 'Rings',
                'description': 'Engagement rings, wedding rings, and fashion rings',
                'is_active': True
            },
            {
                'name': 'Necklaces',
                'description': 'Pendants, chains, and statement necklaces',
                'is_active': True
            },
            {
                'name': 'Earrings',
                'description': 'Studs, hoops, and drop earrings',
                'is_active': True
            },
            {
                'name': 'Bracelets',
                'description': 'Bangles, charm bracelets, and tennis bracelets',
                'is_active': True
            },
            {
                'name': 'Watches',
                'description': 'Luxury and fashion watches',
                'is_active': True
            },
            {
                'name': 'Pendants',
                'description': 'Necklace pendants and charms',
                'is_active': True
            },
            {
                'name': 'Anklets',
                'description': 'Ankle bracelets and chains',
                'is_active': True
            },
            {
                'name': 'Brooches',
                'description': 'Decorative brooches and pins',
                'is_active': True
            }
        ]
        
        created_count = 0
        for category_data in sample_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                tenant=tenant,
                defaults=category_data
            )
            if created:
                created_count += 1
                print(f"Created category: {category.name}")
            else:
                print(f"Category already exists: {category.name}")
        
        print(f"\nTotal categories created: {created_count}")
        print(f"Total categories in database: {Category.objects.filter(tenant=tenant).count()}")
        
    except Exception as e:
        print(f"Error adding sample categories: {e}")

if __name__ == '__main__':
    add_sample_categories() 