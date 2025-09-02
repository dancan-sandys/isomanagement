#!/usr/bin/env python3
"""
Test script to check the roles endpoint response structure for frontend debugging
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_roles_endpoint():
    """Test the roles endpoint to see the response structure"""
    print("=== TESTING ROLES ENDPOINT FOR FRONTEND ===")
    
    # First, login to get a token
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
            print(f"Response: {login_response.text}")
            return
        
        print("✅ Login successful")
        token_data = login_response.json()
        
        # Extract token from nested structure
        if 'data' in token_data and 'access_token' in token_data['data']:
            access_token = token_data['data']['access_token']
        else:
            print("❌ No access token found in response")
            print("Available keys:", list(token_data.keys()))
            return
        
        print(f"Token: {access_token[:20]}...")
        
        # Now test the roles endpoint
        print("\n2. Testing roles endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        roles_response = requests.get(
            f"{BASE_URL}/api/v1/rbac/roles",
            headers=headers
        )
        
        print(f"Roles endpoint status: {roles_response.status_code}")
        
        if roles_response.status_code == 200:
            roles_data = roles_response.json()
            print(f"✅ Roles endpoint successful")
            print(f"Response type: {type(roles_data)}")
            print(f"Response keys: {list(roles_data.keys()) if isinstance(roles_data, dict) else 'Not a dict'}")
            
            if isinstance(roles_data, dict):
                print(f"Data key: {roles_data.get('data', 'No data key')}")
                if 'data' in roles_data:
                    roles_list = roles_data['data']
                    print(f"Roles count: {len(roles_list)}")
                    if roles_list:
                        print(f"First role structure: {json.dumps(roles_list[0], indent=2, default=str)}")
            else:
                print(f"Direct response: {json.dumps(roles_data, indent=2, default=str)}")
        else:
            print(f"❌ Roles endpoint failed: {roles_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_roles_endpoint()
