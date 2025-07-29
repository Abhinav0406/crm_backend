#!/usr/bin/env python
"""
Script to create test data for announcements and team members.
Run this after setting up users.
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.announcements.models import Announcement, TeamMessage
from apps.tenants.models import Tenant

User = get_user_model()

def create_test_data():
    """Create test announcements and messages."""
    
    # Get the default tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenant found. Please run setup_users.py first.")
        return
    
    # Get some users
    users = User.objects.filter(tenant=tenant)[:5]
    if not users:
        print("No users found. Please run setup_users.py first.")
        return
    
    # Create test announcements
    announcements_data = [
        {
            'title': 'Welcome to the CRM System!',
            'content': 'Welcome everyone! This is our new CRM system for managing customers and sales.',
            'announcement_type': 'system_wide',
            'priority': 'medium',
            'is_pinned': True,
            'requires_acknowledgment': True,
        },
        {
            'title': 'Monthly Sales Target Update',
            'content': 'Great news! We have updated our monthly sales targets. Please check the new goals.',
            'announcement_type': 'team_specific',
            'priority': 'high',
            'is_pinned': False,
            'requires_acknowledgment': False,
        },
        {
            'title': 'System Maintenance Notice',
            'content': 'The system will be under maintenance on Sunday from 2 AM to 4 AM.',
            'announcement_type': 'system_wide',
            'priority': 'low',
            'is_pinned': False,
            'requires_acknowledgment': False,
        }
    ]
    
    for i, data in enumerate(announcements_data):
        announcement, created = Announcement.objects.get_or_create(
            title=data['title'],
            defaults={
                'content': data['content'],
                'announcement_type': data['announcement_type'],
                'priority': data['priority'],
                'is_pinned': data['is_pinned'],
                'requires_acknowledgment': data['requires_acknowledgment'],
                'author': users[i % len(users)],
                'tenant': tenant,
                'publish_at': timezone.now() - timedelta(days=i),
                'is_active': True,
            }
        )
        if created:
            print(f"Created announcement: {data['title']}")
        else:
            print(f"Announcement already exists: {data['title']}")
    
    # Create test team messages
    messages_data = [
        {
            'subject': 'Team Meeting Tomorrow',
            'content': 'Hi team! We have a meeting tomorrow at 10 AM to discuss this week\'s progress.',
            'message_type': 'general',
            'is_urgent': False,
            'requires_response': True,
        },
        {
            'subject': 'Customer Feedback Request',
            'content': 'Please review the recent customer feedback and provide your thoughts.',
            'message_type': 'customer',
            'is_urgent': True,
            'requires_response': True,
        }
    ]
    
    for i, data in enumerate(messages_data):
        message, created = TeamMessage.objects.get_or_create(
            subject=data['subject'],
            defaults={
                'content': data['content'],
                'message_type': data['message_type'],
                'is_urgent': data['is_urgent'],
                'requires_response': data['requires_response'],
                'sender': users[i % len(users)],
                'tenant': tenant,
            }
        )
        if created:
            # Add recipients (all other users)
            recipients = [u for u in users if u != message.sender]
            message.recipients.set(recipients)
            print(f"Created message: {data['subject']}")
        else:
            print(f"Message already exists: {data['subject']}")
    
    print("\nTest data creation completed!")
    print(f"Created {Announcement.objects.count()} announcements")
    print(f"Created {TeamMessage.objects.count()} team messages")

if __name__ == '__main__':
    create_test_data() 