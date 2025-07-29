#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import TeamMember, User
from apps.stores.models import Store
from apps.tenants.models import Tenant

def check_store_assignments():
    print("=== Checking Store Assignments ===")
    
    # Check stores
    print(f"\nTotal Stores: {Store.objects.count()}")
    for store in Store.objects.all():
        print(f"- Store: {store.name} (Tenant: {store.tenant.name if store.tenant else 'None'})")
    
    # Check team members and their store assignments
    print(f"\n=== Team Members Store Assignments ===")
    team_members = TeamMember.objects.all()
    
    for tm in team_members:
        user = tm.user
        store_name = user.store.name if user.store else 'None'
        tenant_name = user.tenant.name if user.tenant else 'None'
        
        print(f"ID: {tm.id}, Employee: {tm.employee_id}")
        print(f"  User: {user.get_full_name()} ({user.username})")
        print(f"  Store: {store_name}")
        print(f"  Tenant: {tenant_name}")
        print(f"  Role: {user.role}")
        print("---")
    
    # Check users without stores
    users_without_stores = User.objects.filter(store__isnull=True)
    print(f"\n=== Users Without Stores: {users_without_stores.count()} ===")
    for user in users_without_stores[:10]:
        print(f"- {user.get_full_name()} ({user.username}) - Role: {user.role}")

if __name__ == '__main__':
    check_store_assignments() 