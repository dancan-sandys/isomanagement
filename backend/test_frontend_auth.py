#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to simulate frontend authentication flow
"""
import requests
import json

def test_frontend_auth_flow():
    """Test the complete frontend authentication flow"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=== Frontend Authentication Flow Test ===\n")
    
    # Step 1: Login
    print("1. Testing login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("data", {}).get("access_token")
            
            if access_token:
                print("✅ Login successful")
                print(f"Access token: {access_token[:50]}...")
                
                # Step 2: Test GET /auth/me
                print("\n2. Testing GET /auth/me...")
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(f"{base_url}/auth/me", headers=headers)
                print(f"GET /auth/me status: {response.status_code}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    print("✅ User data retrieved successfully")
                    print(f"User: {user_data.get('data', {}).get('username', 'Unknown')}")
                else:
                    print(f"❌ GET /auth/me failed: {response.text}")
                
                # Step 3: Test GET /risk/ (should work with auth)
                print("\n3. Testing GET /risk/...")
                response = requests.get(f"{base_url}/risk/", headers=headers)
                print(f"GET /risk/ status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ GET /risk/ successful")
                else:
                    print(f"❌ GET /risk/ failed: {response.text}")
                
                # Step 4: Test POST /risk/ (should work with auth)
                print("\n4. Testing POST /risk/...")
                risk_data = {
                    "risk_number": "RISK-TEST-002",
                    "title": "Test Risk Item",
                    "description": "Test risk description",
                    "item_type": "risk",
                    "category": "equipment",
                    "severity": "medium",
                    "likelihood": "possible",
                    "classification": "business",
                    "status": "open"
                }
                
                response = requests.post(
                    f"{base_url}/risk/",
                    json=risk_data,
                    headers=headers
                )
                print(f"POST /risk/ status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ POST /risk/ successful")
                    risk_response = response.json()
                    print(f"Created risk: {risk_response.get('message', 'No message')}")
                else:
                    print(f"❌ POST /risk/ failed: {response.text}")
                
                # Step 5: Test without auth (should fail)
                print("\n5. Testing without authentication...")
                response = requests.get(f"{base_url}/risk/")
                print(f"GET /risk/ without auth status: {response.status_code}")
                
                if response.status_code == 403:
                    print("✅ Correctly rejected without authentication")
                else:
                    print(f"❌ Unexpected response without auth: {response.status_code}")
                
            else:
                print("❌ No access token in response")
                print(f"Response: {json.dumps(token_data, indent=2)}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_auth_flow()
