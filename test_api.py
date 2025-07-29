#!/usr/bin/env python
import requests
import json

def test_team_members_api():
    # Login to get token
    login_data = {
        "username": "vamshi_manager",
        "password": "password123"
    }
    
    try:
        # Login
        login_response = requests.post(
            "http://localhost:8000/api/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access']
            print("✅ Login successful")
            print(f"Token: {token[:50]}...")
            
            # Get team members
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            team_response = requests.get(
                "http://localhost:8000/api/auth/team-members/",
                headers=headers
            )
            
            print(f"\nTeam Members API Status: {team_response.status_code}")
            
            if team_response.status_code == 200:
                data = team_response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
                
                if 'results' in data:
                    print(f"\nFound {len(data['results'])} team members:")
                    for member in data['results']:
                        print(f"- {member.get('user_name', 'No Name')} ({member.get('employee_id', 'No ID')})")
                else:
                    print(f"\nFound {len(data)} team members:")
                    for member in data:
                        print(f"- {member.get('user_name', 'No Name')} ({member.get('employee_id', 'No ID')})")
            else:
                print(f"❌ Team members API failed: {team_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_team_members_api() 