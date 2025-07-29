#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import TeamMember, User
from apps.tenants.models import Tenant
from apps.stores.models import Store

def check_and_create_data():
    print("=== Checking Database ===")
    print(f"Total Users: {User.objects.count()}")
    print(f"Total TeamMembers: {TeamMember.objects.count()}")
    print(f"Total Tenants: {Tenant.objects.count()}")
    print(f"Total Stores: {Store.objects.count()}")
    
    # List existing users
    print("\n=== Existing Users ===")
    for user in User.objects.all()[:10]:
        print(f"ID: {user.id}, Username: {user.username}, Name: {user.get_full_name()}, Role: {user.role}")
    
    # List existing team members
    print("\n=== Existing Team Members ===")
    for tm in TeamMember.objects.all()[:10]:
        print(f"ID: {tm.id}, Employee ID: {tm.employee_id}, User: {tm.user.get_full_name()}, Status: {tm.status}")
    
    # Create test data if none exists
    if TeamMember.objects.count() == 0:
        print("\n=== Creating Test Team Members ===")
        
        # Get or create a tenant
        tenant, created = Tenant.objects.get_or_create(
            name="Test Jewelry Store",
            defaults={
                'description': 'Test tenant for development',
                'is_active': True
            }
        )
        print(f"Tenant: {tenant.name} (created: {created})")
        
        # Get or create a store
        store, created = Store.objects.get_or_create(
            name="Main Store",
            tenant=tenant,
            defaults={
                'address': '123 Main St, City, State',
                'phone': '+1234567890',
                'is_active': True
            }
        )
        print(f"Store: {store.name} (created: {created})")
        
        # Create test users and team members
        test_members = [
            {
                'username': 'john.doe',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'manager',
                'employee_id': 'MEMP001',
                'department': 'Sales',
                'position': 'Sales Manager',
                'status': 'active'
            },
            {
                'username': 'jane.smith',
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'inhouse_sales',
                'employee_id': 'MEMP002',
                'department': 'Sales',
                'position': 'Senior Sales Associate',
                'status': 'active'
            },
            {
                'username': 'mike.johnson',
                'email': 'mike.johnson@example.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'role': 'tele_calling',
                'employee_id': 'MEMP003',
                'department': 'Tele-sales',
                'position': 'Tele-calling Specialist',
                'status': 'active'
            },
            {
                'username': 'sarah.wilson',
                'email': 'sarah.wilson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'role': 'inhouse_sales',
                'employee_id': 'MEMP004',
                'department': 'Sales',
                'position': 'Sales Associate',
                'status': 'active'
            },
            {
                'username': 'david.brown',
                'email': 'david.brown@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'role': 'marketing',
                'employee_id': 'MEMP005',
                'department': 'Marketing',
                'position': 'Marketing Specialist',
                'status': 'active'
            }
        ]
        
        for member_data in test_members:
            # Create user
            user, created = User.objects.get_or_create(
                username=member_data['username'],
                defaults={
                    'email': member_data['email'],
                    'first_name': member_data['first_name'],
                    'last_name': member_data['last_name'],
                    'role': member_data['role'],
                    'tenant': tenant,
                    'store': store,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                print(f"Created user: {user.get_full_name()}")
            
            # Create team member
            team_member, created = TeamMember.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': member_data['employee_id'],
                    'department': member_data['department'],
                    'position': member_data['position'],
                    'status': member_data['status'],
                    'sales_target': 50000.00,
                    'current_sales': 45000.00,
                    'performance_rating': 'good'
                }
            )
            
            if created:
                print(f"Created team member: {team_member.user.get_full_name()} ({team_member.employee_id})")
        
        print(f"\nTotal TeamMembers after creation: {TeamMember.objects.count()}")

if __name__ == '__main__':
    check_and_create_data() 