#!/usr/bin/env python
"""
Setup script to create initial users and tenants for the CRM system.
Run this script after running migrations.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.users.models import User

User = get_user_model()

def create_tenant(name, slug, **kwargs):
    """Create a tenant if it doesn't exist."""
    tenant, created = Tenant.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'subscription_plan': 'professional',
            'subscription_status': 'active',
            'is_active': True,
            **kwargs
        }
    )
    if created:
        print(f"Created tenant: {name}")
    else:
        print(f"Tenant already exists: {name}")
    return tenant

def create_user(username, password, role, tenant=None, **kwargs):
    """Create a user if it doesn't exist."""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'role': role,
            'tenant': tenant,
            'is_active': True,
            **kwargs
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"Created user: {username} ({role})")
    else:
        print(f"User already exists: {username}")
    return user

def main():
    print("Setting up initial users and tenants...")
    
    # Create default tenant
    default_tenant = create_tenant(
        name="Jewelry Store Demo",
        slug="jewelry-demo",
        business_type="Jewelry Retail",
        industry="Retail",
        email="admin@jewelrydemo.com",
        phone="+1234567890"
    )
    
    # Create users with different roles
    users_data = [
        {
            'username': 'platform_admin',
            'password': 'admin123456',
            'role': User.Role.PLATFORM_ADMIN,
            'first_name': 'Platform',
            'last_name': 'Admin',
            'email': 'platform@example.com',
            'tenant': None  # Platform admin doesn't belong to a specific tenant
        },
        {
            'username': 'business_admin',
            'password': 'business123',
            'role': User.Role.BUSINESS_ADMIN,
            'first_name': 'Business',
            'last_name': 'Admin',
            'email': 'business@jewelrydemo.com',
            'tenant': default_tenant
        },
        {
            'username': 'manager_sarah',
            'password': 'manager123',
            'role': User.Role.MANAGER,
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah@jewelrydemo.com',
            'tenant': default_tenant
        },
        {
            'username': 'sales_mike',
            'password': 'sales123',
            'role': User.Role.INHOUSE_SALES,
            'first_name': 'Mike',
            'last_name': 'Davis',
            'email': 'mike@jewelrydemo.com',
            'tenant': default_tenant
        },
        {
            'username': 'tele_emma',
            'password': 'tele123',
            'role': User.Role.TELE_CALLING,
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'email': 'emma@jewelrydemo.com',
            'tenant': default_tenant
        },
        {
            'username': 'marketing_david',
            'password': 'marketing123',
            'role': User.Role.MARKETING,
            'first_name': 'David',
            'last_name': 'Brown',
            'email': 'david@jewelrydemo.com',
            'tenant': default_tenant
        }
    ]
    
    for user_data in users_data:
        create_user(**user_data)
    
    print("\nSetup completed successfully!")
    print("\nLogin credentials:")
    print("=" * 50)
    for user_data in users_data:
        print(f"Username: {user_data['username']}")
        print(f"Password: {user_data['password']}")
        print(f"Role: {user_data['role']}")
        print("-" * 30)

if __name__ == '__main__':
    main() 