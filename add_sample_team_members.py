#!/usr/bin/env python
"""
Script to add sample team members for testing.
Run this script to populate the database with sample team members.
"""

import os
import sys
import django
from datetime import date

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User, TeamMember
from apps.tenants.models import Tenant

def create_sample_team_members():
    """Create sample team members for testing."""
    
    # Get or create a tenant
    tenant, created = Tenant.objects.get_or_create(
        name='Prestige Jewelers',
        defaults={
            'slug': 'prestige-jewelers',
            'business_type': 'Jewelry Retail',
            'industry': 'Retail',
            'description': 'Premium jewelry retailer',
            'email': 'info@prestigejewelers.com',
            'phone': '+1 (555) 123-4567',
            'subscription_plan': 'professional',
            'subscription_status': 'active',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created tenant: {tenant.name}")
    else:
        print(f"Using existing tenant: {tenant.name}")
    
    # Sample team members data
    team_members_data = [
        {
            'username': 'john.doe',
            'email': 'john.doe@prestigejewelers.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'manager',
            'phone': '+1 (555) 123-4567',
            'employee_id': 'EMP001',
            'department': 'Sales',
            'position': 'Store Manager',
            'status': 'active',
            'performance_rating': 'excellent',
            'current_sales': 45000.00,
            'hire_date': date(2023, 1, 15),
            'notes': 'Experienced manager with 5+ years in jewelry sales'
        },
        {
            'username': 'sarah.smith',
            'email': 'sarah.smith@prestigejewelers.com',
            'first_name': 'Sarah',
            'last_name': 'Smith',
            'role': 'inhouse_sales',
            'phone': '+1 (555) 234-5678',
            'employee_id': 'EMP002',
            'department': 'Sales',
            'position': 'Senior Sales Associate',
            'status': 'active',
            'performance_rating': 'good',
            'current_sales': 32000.00,
            'hire_date': date(2023, 3, 20),
            'notes': 'Specializes in diamond jewelry'
        },
        {
            'username': 'mike.johnson',
            'email': 'mike.johnson@prestigejewelers.com',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'role': 'tele_calling',
            'phone': '+1 (555) 345-6789',
            'employee_id': 'EMP003',
            'department': 'Sales',
            'position': 'Tele-caller',
            'status': 'active',
            'performance_rating': 'average',
            'current_sales': 18000.00,
            'hire_date': date(2023, 6, 10),
            'notes': 'Handles customer follow-ups and appointments'
        },
        {
            'username': 'emma.wilson',
            'email': 'emma.wilson@prestigejewelers.com',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'role': 'marketing',
            'phone': '+1 (555) 456-7890',
            'employee_id': 'EMP004',
            'department': 'Marketing',
            'position': 'Marketing Specialist',
            'status': 'active',
            'performance_rating': 'good',
            'current_sales': 25000.00,
            'hire_date': date(2023, 2, 28),
            'notes': 'Manages social media and promotional campaigns'
        },
        {
            'username': 'david.brown',
            'email': 'david.brown@prestigejewelers.com',
            'first_name': 'David',
            'last_name': 'Brown',
            'role': 'inhouse_sales',
            'phone': '+1 (555) 567-8901',
            'employee_id': 'EMP005',
            'department': 'Sales',
            'position': 'Sales Associate',
            'status': 'inactive',
            'performance_rating': 'below_average',
            'current_sales': 8000.00,
            'hire_date': date(2023, 8, 15),
            'notes': 'On probation due to performance issues'
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for member_data in team_members_data:
        # Check if user already exists
        user, user_created = User.objects.get_or_create(
            username=member_data['username'],
            defaults={
                'email': member_data['email'],
                'first_name': member_data['first_name'],
                'last_name': member_data['last_name'],
                'role': member_data['role'],
                'phone': member_data['phone'],
                'tenant': tenant,
                'is_active': True
            }
        )
        
        if not user_created:
            # Update existing user
            user.email = member_data['email']
            user.first_name = member_data['first_name']
            user.last_name = member_data['last_name']
            user.role = member_data['role']
            user.phone = member_data['phone']
            user.tenant = tenant
            user.save()
            print(f"Updated user: {user.username}")
        else:
            # Set password for new user
            user.set_password('password123')
            user.save()
            print(f"Created user: {user.username}")
        
        # Check if team member already exists
        team_member, tm_created = TeamMember.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': member_data['employee_id'],
                'department': member_data['department'],
                'position': member_data['position'],
                'status': member_data['status'],
                'performance_rating': member_data['performance_rating'],
                'sales_target': 50000.00,
                'current_sales': member_data['current_sales'],
                'hire_date': member_data['hire_date'],
                'notes': member_data['notes']
            }
        )
        
        if not tm_created:
            # Update existing team member
            team_member.employee_id = member_data['employee_id']
            team_member.department = member_data['department']
            team_member.position = member_data['position']
            team_member.status = member_data['status']
            team_member.performance_rating = member_data['performance_rating']
            team_member.current_sales = member_data['current_sales']
            team_member.hire_date = member_data['hire_date']
            team_member.notes = member_data['notes']
            team_member.save()
            updated_count += 1
            print(f"Updated team member: {user.get_full_name()}")
        else:
            created_count += 1
            print(f"Created team member: {user.get_full_name()}")
    
    print(f"\nSummary:")
    print(f"Created: {created_count} team members")
    print(f"Updated: {updated_count} team members")
    print(f"Total team members in database: {TeamMember.objects.count()}")
    print(f"Total users in database: {User.objects.count()}")
    
    # Print login credentials
    print(f"\nLogin credentials for testing:")
    print(f"Username: john.doe")
    print(f"Password: password123")
    print(f"Role: Manager")

if __name__ == '__main__':
    create_sample_team_members() 