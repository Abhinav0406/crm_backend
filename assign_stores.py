#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import TeamMember, User
from apps.stores.models import Store
from apps.tenants.models import Tenant

def assign_stores_to_team_members():
    print("=== Assigning Stores to Team Members ===")
    
    # Get the main tenant (mandeep jewelries)
    tenant = Tenant.objects.filter(name__icontains='mandeep').first()
    if not tenant:
        print("❌ No mandeep tenant found")
        return
    
    print(f"Using tenant: {tenant.name}")
    
    # Get stores for this tenant
    stores = Store.objects.filter(tenant=tenant)
    print(f"Found {stores.count()} stores for this tenant:")
    for store in stores:
        print(f"- {store.name}")
    
    if not stores.exists():
        print("❌ No stores found for this tenant")
        return
    
    # Get the first store (or you can choose a specific one)
    default_store = stores.first()
    print(f"Using default store: {default_store.name}")
    
    # Get team members without stores
    team_members_without_stores = TeamMember.objects.filter(
        user__store__isnull=True,
        user__tenant=tenant
    )
    
    print(f"\nFound {team_members_without_stores.count()} team members without stores")
    
    # Assign stores
    updated_count = 0
    for tm in team_members_without_stores:
        user = tm.user
        if user.store is None:
            user.store = default_store
            user.save()
            updated_count += 1
            print(f"✅ Assigned {default_store.name} to {user.get_full_name()} ({tm.employee_id})")
    
    print(f"\n✅ Successfully assigned stores to {updated_count} team members")
    
    # Verify the changes
    print(f"\n=== Verification ===")
    team_members = TeamMember.objects.filter(user__tenant=tenant)
    for tm in team_members:
        store_name = tm.user.store.name if tm.user.store else 'None'
        print(f"{tm.employee_id}: {tm.user.get_full_name()} - Store: {store_name}")

if __name__ == '__main__':
    assign_stores_to_team_members() 