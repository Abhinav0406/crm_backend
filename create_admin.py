#!/usr/bin/env python
"""
Script to create a working admin user for the CRM system.
Run this script to create a superuser account that can login.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User
from apps.tenants.models import Tenant

def create_admin_user():
    """Create a working admin user."""
    
    # Check if admin user already exists
    if User.objects.filter(username='admin').exists():
        print("Admin user already exists!")
        user = User.objects.get(username='admin')
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is superuser: {user.is_superuser}")
        print(f"Is staff: {user.is_staff}")
        print(f"Is active: {user.is_active}")
        return
    
    # Create default tenant if it doesn't exist
    default_tenant, created = Tenant.objects.get_or_create(
        slug='platform',
        defaults={
            'name': 'Platform Admin',
            'business_type': 'platform',
            'subscription_plan': 'enterprise',
            'max_users': 1000,
            'max_storage_gb': 1000,
        }
    )
    
    if created:
        print(f"Created default tenant: {default_tenant.name}")
    
    # Create admin user
    try:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@jewelrycrm.com',
            password='admin123456',
            first_name='Platform',
            last_name='Admin',
            role='platform_admin',
            is_superuser=True,
            is_staff=True,
            is_active=True,
            tenant=default_tenant
        )
        
        print("✅ Admin user created successfully!")
        print(f"Username: {admin_user.username}")
        print(f"Password: admin123456")
        print(f"Email: {admin_user.email}")
        print(f"Role: {admin_user.role}")
        print(f"Is superuser: {admin_user.is_superuser}")
        print(f"Is staff: {admin_user.is_staff}")
        print(f"Is active: {admin_user.is_active}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    
    return True

def create_test_users():
    """Create some test users for different roles."""
    
    # Get or create a test tenant
    test_tenant, created = Tenant.objects.get_or_create(
        slug='test-business',
        defaults={
            'name': 'Test Jewelry Store',
            'business_type': 'jewelry_store',
            'subscription_plan': 'professional',
            'max_users': 10,
            'max_storage_gb': 50,
        }
    )
    
    test_users = [
        {
            'username': 'business_admin',
            'password': 'business123',
            'email': 'admin@teststore.com',
            'first_name': 'Business',
            'last_name': 'Admin',
            'role': 'business_admin',
            'tenant': test_tenant
        },
        {
            'username': 'manager',
            'password': 'manager123',
            'email': 'manager@teststore.com',
            'first_name': 'Sales',
            'last_name': 'Manager',
            'role': 'manager',
            'tenant': test_tenant
        },
        {
            'username': 'sales',
            'password': 'sales123',
            'email': 'sales@teststore.com',
            'first_name': 'Sales',
            'last_name': 'Rep',
            'role': 'inhouse_sales',
            'tenant': test_tenant
        }
    ]
    
    for user_data in test_users:
        if not User.objects.filter(username=user_data['username']).exists():
            try:
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    tenant=user_data['tenant'],
                    is_active=True
                )
                print(f"✅ Created {user_data['role']} user: {user_data['username']} / {user_data['password']}")
            except Exception as e:
                print(f"❌ Error creating {user_data['username']}: {e}")

if __name__ == '__main__':
    print("🔧 Setting up admin user for Jewelry CRM...")
    print("=" * 50)
    
    # Create admin user
    if create_admin_user():
        print("\n" + "=" * 50)
        print("🎉 Login credentials:")
        print("Username: admin")
        print("Password: admin123456")
        print("URL: http://127.0.0.1:8000/admin/")
        print("=" * 50)
    
    # Create test users
    print("\n🔧 Creating test users...")
    create_test_users()
    
    print("\n✅ Setup complete! You can now login.") 