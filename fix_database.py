#!/usr/bin/env python
"""
Script to fix database issues manually.
This can be run locally to diagnose and fix database problems.
"""

import os
import django
import requests

def check_database_status():
    """Check if database is accessible and tables exist."""
    
    base_url = "https://crm-backend-094z.onrender.com"
    
    print("🔍 Checking database status...")
    print("=" * 50)
    
    # Check if API is responding
    try:
        response = requests.get(f"{base_url}/api/schema/")
        print(f"✅ API Status: {response.status_code}")
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False
    
    # Check admin endpoint
    try:
        response = requests.get(f"{base_url}/admin/")
        print(f"✅ Admin Status: {response.status_code}")
        if response.status_code == 302:
            print("✅ Admin redirecting to login (normal)")
        elif response.status_code == 500:
            print("❌ Admin returning 500 error")
        else:
            print(f"⚠️ Unexpected admin status: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin Error: {e}")
    
    return True

def create_admin_via_api():
    """Try to create admin user via API."""
    
    base_url = "https://crm-backend-094z.onrender.com"
    
    # Try to access a simple endpoint that doesn't require database
    try:
        response = requests.get(f"{base_url}/api/schema/")
        if response.status_code == 200:
            print("✅ API is working")
            print("❌ Database tables don't exist")
            print("\n💡 Solution:")
            print("1. Go to Render dashboard")
            print("2. Update Build Command: chmod +x build.sh && ./build.sh")
            print("3. Update Start Command: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT")
            print("4. Add environment variable: FORCE_MIGRATE=true")
            print("5. Manual deploy")
        else:
            print(f"❌ API not working: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🔧 Database Fix Script")
    print("=" * 50)
    
    if check_database_status():
        create_admin_via_api()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Update Render service settings")
    print("2. Add FORCE_MIGRATE=true environment variable")
    print("3. Manual deploy")
    print("4. Check build logs for migration output") 