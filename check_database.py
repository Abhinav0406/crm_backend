#!/usr/bin/env python
"""
Script to check database connection and tables.
Run this locally to diagnose database issues.
"""

import os
import django
import requests

def check_database_via_api():
    """Check database status via API."""
    
    base_url = "https://crm-backend-094z.onrender.com"
    
    # Check if the API is responding
    try:
        response = requests.get(f"{base_url}/api/schema/")
        print(f"✅ API is responding: {response.status_code}")
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return
    
    # Check admin endpoint
    try:
        response = requests.get(f"{base_url}/admin/")
        print(f"✅ Admin endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Admin page is accessible")
        elif response.status_code == 302:
            print("✅ Admin redirecting to login (normal)")
        else:
            print(f"⚠️ Admin status: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin check failed: {e}")

def check_database_tables():
    """Check if database tables exist."""
    
    base_url = "https://crm-backend-094z.onrender.com"
    
    # Try to access a protected endpoint that requires database
    try:
        response = requests.get(f"{base_url}/api/auth/users/")
        print(f"✅ Users API: {response.status_code}")
        if response.status_code == 401:
            print("✅ Database is working (401 is expected for unauthenticated)")
        elif response.status_code == 500:
            print("❌ Database error (500)")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    print("🔍 Checking database status...")
    print("=" * 50)
    
    check_database_via_api()
    print()
    check_database_tables()
    
    print("\n" + "=" * 50)
    print("💡 If database is working, try redeploying with FORCE_MIGRATE=true")
    print("💡 If database is not working, check your DATABASE_URL") 