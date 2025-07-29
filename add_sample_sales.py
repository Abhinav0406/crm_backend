#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sales.models import Sale
from apps.clients.models import Client
from apps.products.models import Product
from apps.tenants.models import Tenant
from apps.users.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

def add_sample_sales():
    """Add sample sales for testing dashboard stats"""
    
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found. Please create a tenant first.")
            return
        
        # Get or create a sales user
        sales_user, created = User.objects.get_or_create(
            username='sales_user',
            tenant=tenant,
            defaults={
                'email': 'sales@example.com',
                'first_name': 'Sales',
                'last_name': 'User',
                'role': 'inhouse_sales',
                'is_active': True
            }
        )
        
        if created:
            sales_user.set_password('password123')
            sales_user.save()
            print("Created sales user")
        else:
            print("Sales user already exists")
        
        # Get some customers
        customers = Client.objects.filter(tenant=tenant)[:5]
        if not customers.exists():
            print("No customers found. Please create customers first.")
            return
        
        # Get some products
        products = Product.objects.filter(tenant=tenant)[:5]
        if not products.exists():
            print("No products found. Please create products first.")
            return
        
        # Sample sales data
        sample_sales = [
            {
                'client': customers[0] if customers.count() > 0 else None,
                'sales_representative': sales_user,
                'order_number': 'ORD-001',
                'subtotal': Decimal('55000.00'),
                'total_amount': Decimal('55000.00'),
                'status': 'confirmed',
                'payment_status': 'paid',
                'notes': 'Gold ring purchase'
            },
            {
                'client': customers[1] if customers.count() > 1 else customers[0],
                'sales_representative': sales_user,
                'order_number': 'ORD-002',
                'subtotal': Decimal('85000.00'),
                'total_amount': Decimal('85000.00'),
                'status': 'delivered',
                'payment_status': 'paid',
                'notes': 'Gold necklace purchase'
            },
            {
                'client': customers[2] if customers.count() > 2 else customers[0],
                'sales_representative': sales_user,
                'order_number': 'ORD-003',
                'subtotal': Decimal('32000.00'),
                'total_amount': Decimal('32000.00'),
                'status': 'processing',
                'payment_status': 'paid',
                'notes': 'Gold earrings purchase'
            },
            {
                'client': customers[3] if customers.count() > 3 else customers[0],
                'sales_representative': sales_user,
                'order_number': 'ORD-004',
                'subtotal': Decimal('42000.00'),
                'total_amount': Decimal('42000.00'),
                'status': 'shipped',
                'payment_status': 'paid',
                'notes': 'Gold bracelet purchase'
            },
            {
                'client': customers[4] if customers.count() > 4 else customers[0],
                'sales_representative': sales_user,
                'order_number': 'ORD-005',
                'subtotal': Decimal('22000.00'),
                'total_amount': Decimal('22000.00'),
                'status': 'confirmed',
                'payment_status': 'paid',
                'notes': 'Gold pendant purchase'
            }
        ]
        
        created_count = 0
        for i, sale_data in enumerate(sample_sales):
            # Create sale with different dates (last 30 days)
            days_ago = random.randint(1, 30)
            created_date = timezone.now() - timedelta(days=days_ago)
            
            sale = Sale.objects.create(
                tenant=tenant,
                created_at=created_date,
                updated_at=created_date,
                **sale_data
            )
            created_count += 1
            print(f"Created sale: {sale.total_amount} for {sale.client.full_name if sale.client else 'Unknown'}")
        
        print(f"\nTotal sales created: {created_count}")
        print(f"Total sales in database: {Sale.objects.filter(tenant=tenant).count()}")
        
        # Print sales summary
        total_revenue = Sale.objects.filter(
            tenant=tenant,
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).aggregate(total=Decimal('0'))['total'] or Decimal('0')
        
        print(f"Total revenue: ${total_revenue}")
        
        # Print sales by status
        for status in ['confirmed', 'processing', 'shipped', 'delivered']:
            count = Sale.objects.filter(tenant=tenant, status=status).count()
            revenue = Sale.objects.filter(
                tenant=tenant, 
                status=status
            ).aggregate(total=Decimal('0'))['total'] or Decimal('0')
            print(f"  {status.capitalize()}: {count} sales, ${revenue}")
        
    except Exception as e:
        print(f"Error adding sample sales: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_sample_sales() 