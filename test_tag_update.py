#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client, CustomerTag
from apps.clients.serializers import ClientSerializer
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

def test_tag_update():
    print("=== TESTING TAG UPDATE FUNCTIONALITY ===")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    
    # Get or create a test client
    client, created = Client.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'tenant': user.tenant
        }
    )
    
    # Get some existing tags
    tags = CustomerTag.objects.all()[:3]
    if not tags.exists():
        print("No tags found in database. Creating test tags...")
        tag1 = CustomerTag.objects.create(name='Test Tag 1', slug='test-tag-1', category='custom')
        tag2 = CustomerTag.objects.create(name='Test Tag 2', slug='test-tag-2', category='custom')
        tags = [tag1, tag2]
    
    tag_slugs = [tag.slug for tag in tags]
    print(f"Available tag slugs: {tag_slugs}")
    
    # Create a mock request
    factory = APIRequestFactory()
    request = factory.put(f'/api/clients/clients/{client.id}/', {
        'tag_slugs': tag_slugs
    })
    request.user = user
    
    # Test the serializer
    serializer = ClientSerializer(instance=client, data={'tag_slugs': tag_slugs}, context={'request': request})
    
    print(f"Serializer is valid: {serializer.is_valid()}")
    if not serializer.is_valid():
        print(f"Validation errors: {serializer.errors}")
        return
    
    # Save the update
    updated_client = serializer.save()
    print(f"Updated client tags: {[tag.name for tag in updated_client.tags.all()]}")
    
    # Test with empty tags
    print("\n=== TESTING EMPTY TAGS ===")
    serializer2 = ClientSerializer(instance=client, data={'tag_slugs': []}, context={'request': request})
    print(f"Empty tags serializer is valid: {serializer2.is_valid()}")
    if serializer2.is_valid():
        updated_client2 = serializer2.save()
        print(f"Client tags after empty update: {[tag.name for tag in updated_client2.tags.all()]}")
    
    print("=== TEST COMPLETED ===")

if __name__ == '__main__':
    test_tag_update() 