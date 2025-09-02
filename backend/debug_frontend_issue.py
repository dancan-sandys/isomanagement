#!/usr/bin/env python3
"""
Debug script to test the exact API call the frontend is making
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def debug_frontend_issue():
    """Debug the frontend issue step by step"""
    print("=== DEBUGGING FRONTEND ISSUE ===")
    
    # 1. Login to get token
    print("1. Logging in...")
    login_data = {
        "username": "testuser123",
        "password": "test123"
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token_data = login_response.json()
        access_token = token_data['data']['access_token']
        print("✅ Login successful")
        
        # 2. Test the exact API call the frontend makes
        print("\n2. Testing roles API call...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Test the exact endpoint the frontend calls
        roles_response = requests.get(
            f"{BASE_URL}/api/v1/rbac/roles",
            headers=headers
        )
        
        print(f"Status: {roles_response.status_code}")
        print(f"Headers: {dict(roles_response.headers)}")
        
        if roles_response.status_code == 200:
            roles_data = roles_response.json()
            print(f"✅ Roles API successful")
            print(f"Response type: {type(roles_data)}")
            print(f"Response length: {len(roles_data) if isinstance(roles_data, list) else 'Not a list'}")
            
            if isinstance(roles_data, list) and len(roles_data) > 0:
                print(f"First role: {roles_data[0].get('name', 'No name')}")
                print(f"Total roles: {len(roles_data)}")
            else:
                print(f"Unexpected response structure: {roles_data}")
        else:
            print(f"❌ Roles API failed: {roles_response.text}")
            
        # 3. Test with different Accept headers
        print("\n3. Testing with different Accept headers...")
        headers_json = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        roles_response_json = requests.get(
            f"{BASE_URL}/api/v1/rbac/roles",
            headers=headers_json
        )
        
        print(f"JSON Accept status: {roles_response_json.status_code}")
        if roles_response_json.status_code == 200:
            print(f"JSON response type: {type(roles_response_json.json())}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_frontend_issue()
