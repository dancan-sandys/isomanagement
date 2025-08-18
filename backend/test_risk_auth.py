#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to authenticate and test risk endpoints
"""
import requests
import json

def test_risk_endpoints():
    """Test risk endpoints with authentication"""
    base_url = "http://localhost:8000/api/v1"
    
    # Login
    print("Logging in...")
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
        
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            # Extract access token from nested data structure
            access_token = token_data.get("data", {}).get("access_token")
            
            if access_token:
                print(f"✅ Login successful")
                print(f"Token: {access_token[:50]}...")
                
                # Test risk endpoints with authentication
                headers = {"Authorization": f"Bearer {access_token}"}
                
                print("\nTesting risk endpoints...")
                
                # Test GET /risk/
                print("Testing GET /risk/...")
                response = requests.get(
                    f"{base_url}/risk/?item_type=risk",
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success: {data.get('message', 'No message')}")
                    print(f"Data: {json.dumps(data.get('data', {}), indent=2)[:200]}...")
                else:
                    print(f"❌ Error: {response.text}")
                
                # Test GET /risk/stats/overview
                print("\nTesting GET /risk/stats/overview...")
                response = requests.get(
                    f"{base_url}/risk/stats/overview",
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success: {data.get('message', 'No message')}")
                else:
                    print(f"❌ Error: {response.text}")
            else:
                print("❌ No access token in response")
                print(f"Response structure: {json.dumps(token_data, indent=2)}")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_risk_endpoints()
