#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.announcements.models import TeamMessage, MessageRead
from apps.stores.models import Store

User = get_user_model()

print("=== DEBUGGING TEAM MESSAGES ===")

# Get all users
users = User.objects.all()
print(f"\nTotal users: {users.count()}")
for user in users:
    print(f"- {user.username} (ID: {user.id}, Tenant: {user.tenant}, Store: {user.store})")

# Get all stores
stores = Store.objects.all()
print(f"\nTotal stores: {stores.count()}")
for store in stores:
    print(f"- {store.name} (ID: {store.id}, Tenant: {store.tenant})")

# Get all team messages
messages = TeamMessage.objects.all()
print(f"\nTotal team messages: {messages.count()}")
for message in messages:
    print(f"- Message ID: {message.id}")
    print(f"  Subject: {message.subject}")
    print(f"  Sender: {message.sender.username} (ID: {message.sender.id})")
    print(f"  Store: {message.store}")
    print(f"  Tenant: {message.tenant}")
    print(f"  Recipients: {[r.username for r in message.recipients.all()]}")
    print(f"  Created: {message.created_at}")

# Get all message reads
reads = MessageRead.objects.all()
print(f"\nTotal message reads: {reads.count()}")
for read in reads:
    print(f"- Message: {read.message.id}, User: {read.user.username}, Read at: {read.read_at}")

# Test with a specific user (assuming 'aditya' exists)
try:
    test_user = User.objects.get(username='aditya')
    print(f"\n=== TESTING FOR USER: {test_user.username} ===")
    print(f"User ID: {test_user.id}")
    print(f"User Tenant: {test_user.tenant}")
    print(f"User Store: {test_user.store}")
    
    # Messages sent by user
    sent_messages = TeamMessage.objects.filter(sender=test_user)
    print(f"Messages sent by user: {sent_messages.count()}")
    
    # Messages where user is recipient
    received_messages = TeamMessage.objects.filter(recipients=test_user)
    print(f"Messages where user is recipient: {received_messages.count()}")
    
    # Messages in same tenant
    tenant_messages = TeamMessage.objects.filter(tenant=test_user.tenant)
    print(f"Messages in same tenant: {tenant_messages.count()}")
    
    # Messages in same store (if user has store)
    if test_user.store:
        store_messages = TeamMessage.objects.filter(store=test_user.store)
        print(f"Messages in same store: {store_messages.count()}")
    
    # Unread messages for user
    read_messages = MessageRead.objects.filter(user=test_user).values_list('message_id', flat=True)
    unread_messages = TeamMessage.objects.filter(recipients=test_user).exclude(id__in=read_messages)
    print(f"Unread messages for user: {unread_messages.count()}")
    
except User.DoesNotExist:
    print("\nUser 'aditya' not found. Testing with first user...")
    if users.exists():
        test_user = users.first()
        print(f"Testing with user: {test_user.username}")
        # ... same logic as above 