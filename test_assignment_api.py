#!/usr/bin/env python
import requests
import json

# Test the assignment detail endpoint
def test_assignment_detail():
    print("Testing Assignment Detail API...")
    
    # First, let's get the list of assignments
    url = "http://localhost:8000/api/telecalling/assignments/"
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE"  # You'll need to replace this with a valid token
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('results', data))} assignments")
            
            # If there are assignments, test the detail endpoint
            if data.get('results', data):
                assignment_id = data.get('results', data)[0]['id']
                detail_url = f"http://localhost:8000/api/telecalling/assignments/{assignment_id}/"
                detail_response = requests.get(detail_url, headers=headers)
                print(f"Detail Status Code: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"Assignment {assignment_id} details:")
                    print(f"  Customer: {detail_data.get('customer_visit_details', {}).get('customer_name', 'N/A')}")
                    print(f"  Call Logs: {len(detail_data.get('call_logs', []))}")
                else:
                    print(f"Detail Error: {detail_response.text}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

# Test creating a call log
def test_create_call_log():
    print("\nTesting Call Log Creation API...")
    
    url = "http://localhost:8000/api/telecalling/call-logs/"
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",  # You'll need to replace this with a valid token
        "Content-Type": "application/json"
    }
    
    call_log_data = {
        "assignment": 1,  # Assuming assignment ID 1 exists
        "call_status": "connected",
        "call_duration": 120,
        "feedback": "Customer was very interested in diamond rings. Wants to visit the store next week.",
        "customer_sentiment": "positive",
        "revisit_required": False,
        "revisit_notes": "",
        "disposition_code": "interested"
    }
    
    try:
        response = requests.post(url, headers=headers, json=call_log_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            print("Call log created successfully!")
            data = response.json()
            print(f"Call Log ID: {data.get('id')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("API Test Script")
    print("=" * 50)
    print("Note: You need to replace 'YOUR_TOKEN_HERE' with a valid JWT token")
    print("To get a token, login through the frontend and copy the token from localStorage")
    print("=" * 50)
    
    test_assignment_detail()
    test_create_call_log() 