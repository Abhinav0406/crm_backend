#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.tenants.models import Tenant
from apps.users.models import User
from apps.clients.models import Client
from apps.sales.models import Sale
from apps.products.models import Product, Category
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

def create_sample_data():
    """Create sample data for testing the platform admin dashboard"""
    try:
        # Create sample tenants
        tenants_data = [
            {
                'name': 'Diamond Palace',
                'slug': 'diamond-palace',
                'business_type': 'Jewelry Store',
                'subscription_status': 'active',
                'subscription_plan': 'professional'
            },
            {
                'name': 'Golden Treasures',
                'slug': 'golden-treasures',
                'business_type': 'Jewelry Store',
                'subscription_status': 'active',
                'subscription_plan': 'basic'
            },
            {
                'name': 'Silver Sparkles',
                'slug': 'silver-sparkles',
                'business_type': 'Jewelry Store',
                'subscription_status': 'inactive',
                'subscription_plan': 'basic'
            },
            {
                'name': 'Royal Gems',
                'slug': 'royal-gems',
                'business_type': 'Jewelry Store',
                'subscription_status': 'active',
                'subscription_plan': 'enterprise'
            }
        ]
        
        created_tenants = []
        for tenant_data in tenants_data:
            tenant, created = Tenant.objects.get_or_create(
                slug=tenant_data['slug'],
                defaults=tenant_data
            )
            if created:
                print(f"Created tenant: {tenant.name}")
            else:
                print(f"Tenant already exists: {tenant.name}")
            created_tenants.append(tenant)
        
        # Create sample users for each tenant
        for i, tenant in enumerate(created_tenants):
            if tenant.subscription_status == 'active':
                # Create business admin for active tenants
                admin_user, created = User.objects.get_or_create(
                    username=f"admin_{tenant.slug}",
                    defaults={
                        'email': f"admin@{tenant.slug}.com",
                        'password': 'admin123',
                        'first_name': f'Admin',
                        'last_name': tenant.name,
                        'role': User.Role.BUSINESS_ADMIN,
                        'tenant': tenant,
                        'is_active': True
                    }
                )
                if created:
                    admin_user.set_password('admin123')
                    admin_user.save()
                    print(f"Created admin user for {tenant.name}")
                
                # Create some sample clients
                for j in range(5):
                    client, created = Client.objects.get_or_create(
                        email=f"client{j+1}@{tenant.slug}.com",
                        tenant=tenant,
                        defaults={
                            'first_name': f'Client{j+1}',
                            'last_name': 'Customer',
                            'phone': f'+1234567890{j}',
                            'address': f'{j+1} Main St, City{j+1}'
                        }
                    )
                    if created:
                        print(f"Created client {client.full_name} for {tenant.name}")
                
                # Create some sample products
                for k in range(3):
                    # Create category first
                    category, created = Category.objects.get_or_create(
                        name='Rings' if k == 0 else 'Necklaces' if k == 1 else 'Earrings',
                        tenant=tenant,
                        defaults={'description': f'{("Rings" if k == 0 else "Necklaces" if k == 1 else "Earrings")} category'}
                    )
                    
                    product, created = Product.objects.get_or_create(
                        name=f'Product {k+1} - {tenant.name}',
                        tenant=tenant,
                        defaults={
                            'sku': f'{tenant.slug.upper()}-PROD-{k+1:03d}',
                            'description': f'Sample product {k+1} for {tenant.name}',
                            'cost_price': Decimal(f'{50 + k * 25}.00'),
                            'selling_price': Decimal(f'{100 + k * 50}.00'),
                            'quantity': 10,
                            'category': category
                        }
                    )
                    if created:
                        print(f"Created product {product.name} for {tenant.name}")
                
                # Create some sample sales
                clients = Client.objects.filter(tenant=tenant)
                products = Product.objects.filter(tenant=tenant)
                
                if clients.exists() and products.exists():
                    for l in range(2):
                        sale, created = Sale.objects.get_or_create(
                            order_number=f"ORD-{tenant.slug.upper()}-{l+1:03d}",
                            tenant=tenant,
                            defaults={
                                'client': clients.first(),
                                'sales_representative': admin_user,
                                'subtotal': Decimal(f'{200 + l * 100}.00'),
                                'tax_amount': Decimal(f'{20 + l * 10}.00'),
                                'total_amount': Decimal(f'{220 + l * 110}.00'),
                                'status': 'confirmed',
                                'payment_status': 'paid'
                            }
                        )
                        if created:
                            print(f"Created sale {sale.order_number} for {tenant.name}")
        
        print("\nSample data creation completed!")
        print(f"Total tenants: {Tenant.objects.count()}")
        print(f"Total users: {User.objects.count()}")
        print(f"Total clients: {Client.objects.count()}")
        print(f"Total products: {Product.objects.count()}")
        print(f"Total sales: {Sale.objects.count()}")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

if __name__ == '__main__':
    create_sample_data() 