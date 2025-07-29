#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User

def create_platform_admin():
    """Create a platform admin user for testing"""
    try:
        # Check if platform admin already exists
        if User.objects.filter(role=User.Role.PLATFORM_ADMIN).exists():
            print("Platform admin user already exists!")
            admin = User.objects.filter(role=User.Role.PLATFORM_ADMIN).first()
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            return
        
        # Create platform admin user
        admin = User.objects.create_user(
            username='platform_admin',
            email='admin@jewelrycrm.com',
            password='admin123',
            first_name='Platform',
            last_name='Admin',
            role=User.Role.PLATFORM_ADMIN,
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        
        print("Platform admin user created successfully!")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Password: admin123")
        print(f"Role: {admin.get_role_display()}")
        
    except Exception as e:
        print(f"Error creating platform admin: {e}")

if __name__ == '__main__':
    create_platform_admin() 