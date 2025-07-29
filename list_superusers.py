#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User

def list_superusers():
    print("=== Superusers in Database ===")
    
    # Get all superusers
    superusers = User.objects.filter(is_superuser=True)
    
    if superusers.exists():
        print(f"Found {superusers.count()} superuser(s):")
        for user in superusers:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Is Active: {user.is_active}")
            print(f"Is Staff: {user.is_staff}")
            print("---")
    else:
        print("No superusers found in the database.")
    
    # Also check staff users
    print("\n=== Staff Users ===")
    staff_users = User.objects.filter(is_staff=True)
    
    if staff_users.exists():
        print(f"Found {staff_users.count()} staff user(s):")
        for user in staff_users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Is Superuser: {user.is_superuser}")
            print(f"Is Active: {user.is_active}")
            print("---")
    else:
        print("No staff users found in the database.")

if __name__ == '__main__':
    list_superusers() 