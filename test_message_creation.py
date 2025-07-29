#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.announcements.models import TeamMessage
from apps.stores.models import Store

User = get_user_model()

print("=== TESTING MESSAGE CREATION ===")

# Get the first user
user = User.objects.first()
if not user:
    print("No users found!")
    exit()

print(f"Testing with user: {user.username}")
print(f"User tenant: {user.tenant}")
print(f"User store: {user.store}")

# Create a test message
test_message = TeamMessage.objects.create(
    subject="Test Message",
    content="This is a test message to see if messages are working.",
    message_type="general",
    sender=user,
    tenant=user.tenant,
    store=user.store if user.store else None,
    is_urgent=False,
    requires_response=False
)

print(f"Created test message with ID: {test_message.id}")

# Now let's see what messages exist
all_messages = TeamMessage.objects.all()
print(f"Total messages in database: {all_messages.count()}")

for msg in all_messages:
    print(f"- Message {msg.id}: {msg.subject} (Sender: {msg.sender.username}, Store: {msg.store})") 