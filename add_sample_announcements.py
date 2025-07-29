#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.announcements.models import Announcement
from apps.tenants.models import Tenant
from apps.users.models import User
from django.utils import timezone
from datetime import timedelta

def add_sample_announcements():
    """Add sample announcements for testing dashboard stats"""
    
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found. Please create a tenant first.")
            return
        
        # Get or create an admin user
        admin_user, created = User.objects.get_or_create(
            username='admin_user',
            tenant=tenant,
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'business_admin',
                'is_active': True
            }
        )
        
        if created:
            admin_user.set_password('password123')
            admin_user.save()
            print("Created admin user")
        else:
            print("Admin user already exists")
        
        # Sample announcements data
        sample_announcements = [
            {
                'title': 'New Product Launch',
                'content': 'We are excited to announce the launch of our new gold collection. All sales team members should familiarize themselves with the new products.',
                'announcement_type': 'system_wide',
                'priority': 'high',
                'target_roles': ['inhouse_sales', 'manager'],
                'is_pinned': True,
                'is_active': True
            },
            {
                'title': 'Monthly Sales Target Update',
                'content': 'Great job team! We have achieved 85% of our monthly sales target. Let\'s push for the remaining 15% in the last week.',
                'announcement_type': 'role_specific',
                'priority': 'medium',
                'target_roles': ['inhouse_sales'],
                'is_pinned': False,
                'is_active': True
            },
            {
                'title': 'Customer Service Training',
                'content': 'Mandatory customer service training session will be held this Friday at 2 PM. All team members must attend.',
                'announcement_type': 'team_specific',
                'priority': 'high',
                'target_roles': ['inhouse_sales', 'manager'],
                'is_pinned': True,
                'is_active': True
            },
            {
                'title': 'Holiday Schedule',
                'content': 'Store will be closed on Independence Day. Please inform customers about the holiday schedule.',
                'announcement_type': 'system_wide',
                'priority': 'medium',
                'target_roles': ['inhouse_sales'],
                'is_pinned': False,
                'is_active': True
            },
            {
                'title': 'Inventory Update',
                'content': 'New gold jewelry items have been added to inventory. Please check the updated catalog.',
                'announcement_type': 'role_specific',
                'priority': 'low',
                'target_roles': ['inhouse_sales'],
                'is_pinned': False,
                'is_active': True
            }
        ]
        
        created_count = 0
        for i, announcement_data in enumerate(sample_announcements):
            # Create announcement with different dates (last 30 days)
            days_ago = i * 3  # Spread them out over time
            created_date = timezone.now() - timedelta(days=days_ago)
            
            announcement = Announcement.objects.create(
                tenant=tenant,
                author=admin_user,
                created_at=created_date,
                updated_at=created_date,
                **announcement_data
            )
            created_count += 1
            print(f"Created announcement: {announcement.title}")
        
        print(f"\nTotal announcements created: {created_count}")
        print(f"Total announcements in database: {Announcement.objects.filter(tenant=tenant).count()}")
        
        # Print announcements summary
        active_announcements = Announcement.objects.filter(
            tenant=tenant,
            is_active=True
        ).count()
        
        pinned_announcements = Announcement.objects.filter(
            tenant=tenant,
            is_pinned=True
        ).count()
        
        print(f"Active announcements: {active_announcements}")
        print(f"Pinned announcements: {pinned_announcements}")
        
    except Exception as e:
        print(f"Error adding sample announcements: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_sample_announcements() 