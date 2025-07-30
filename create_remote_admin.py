#!/usr/bin/env python
"""
Script to create admin user for remote deployment.
Run this locally to create admin user on your deployed backend.
"""

import requests
import json

def create_admin_via_api():
    """Create admin user via API call to your deployed backend."""
    
    # Your deployed backend URL
    base_url = "https://crm-backend-094z.onrender.com"
    
    # Admin creation endpoint (you might need to create this)
    admin_url = f"{base_url}/api/auth/create-admin/"
    
    admin_data = {
        "username": "admin",
        "email": "admin@jewelrycrm.com",
        "password": "admin123456",
        "first_name": "Platform",
        "last_name": "Admin",
        "role": "platform_admin"
    }
    
    try:
        response = requests.post(admin_url, json=admin_data)
        if response.status_code == 201:
            print("✅ Admin user created successfully!")
            print("Login credentials:")
            print("Username: admin")
            print("Password: admin123456")
            print(f"Admin URL: {base_url}/admin/")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🔧 Creating admin user for remote deployment...")
    create_admin_via_api() 