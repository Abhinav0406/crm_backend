#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import CustomerTag

def check_tags():
    print("=== CHECKING EXISTING TAGS ===")
    tags = CustomerTag.objects.all()
    print(f"Total tags in database: {tags.count()}")
    
    for tag in tags:
        print(f"- {tag.name} (slug: {tag.slug}, category: {tag.category})")
    
    # Check for specific tags that might be used in the frontend
    common_slugs = ['needs-follow-up', 'diamond-interested', 'gold-interested', 'wedding-buyer', 'referral']
    print(f"\n=== CHECKING COMMON SLUGS ===")
    for slug in common_slugs:
        try:
            tag = CustomerTag.objects.get(slug=slug)
            print(f"✓ {slug} exists: {tag.name}")
        except CustomerTag.DoesNotExist:
            print(f"✗ {slug} does not exist")

if __name__ == '__main__':
    check_tags() 