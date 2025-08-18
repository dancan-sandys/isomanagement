#!/usr/bin/env python3
"""
Debug script to help identify frontend authentication issues
"""
import requests
import json

def test_frontend_auth():
    """Test the authentication flow that the frontend would use"""
    
    # Base URL
    base_url = "http://localhost:8000/api/v1"
    
    print("🔍 Testing Frontend Authentication Flow...")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1. Testing Login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Login successful!")
            print(f"   User: {login_result['data']['user']['username']}")
            print(f"   Role: {login_result['data']['user']['role_name']}")
            
            # Extract token
            token = login_result['data']['access_token']
            print(f"   Token: {token[:50]}...")
            
            # Step 2: Test Risk API with token
            print("\n2. Testing Risk API with token...")
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            risk_response = requests.get(f"{base_url}/risk/", headers=headers)
            
            if risk_response.status_code == 200:
                print("✅ Risk API call successful!")
                risk_data = risk_response.json()
                print(f"   Response: {json.dumps(risk_data, indent=2)}")
            else:
                print(f"❌ Risk API call failed: {risk_response.status_code}")
                print(f"   Response: {risk_response.text}")
                
            # Step 3: Test Risk Stats
            print("\n3. Testing Risk Stats...")
            stats_response = requests.get(f"{base_url}/risk/stats/overview", headers=headers)
            
            if stats_response.status_code == 200:
                print("✅ Risk Stats call successful!")
                stats_data = stats_response.json()
                print(f"   Response: {json.dumps(stats_data, indent=2)}")
            else:
                print(f"❌ Risk Stats call failed: {stats_response.status_code}")
                print(f"   Response: {stats_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_frontend_auth()
