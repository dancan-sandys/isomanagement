#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to test authentication and permissions for risk endpoints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_risk_endpoints():
    """Test risk endpoints with authentication"""
    base_url = "http://localhost:8000/api/v1"
    
    # Test different users
    test_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "qa_manager", "password": "qa123"},
        {"username": "prod_manager", "password": "prod123"},
    ]
    
    for user in test_users:
        print(f"\nTesting login with {user['username']}...")
        
        try:
            response = requests.post(
                f"{base_url}/auth/login",
                data=user,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("data", {}).get("access_token")
                print(f"✅ Login successful for {user['username']}")
                print(f"Access token: {access_token[:20]}...")
                
                # Test risk endpoints with token
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Test risk list endpoint
                print(f"Testing risk list endpoint with {user['username']}...")
                response = requests.get(
                    f"{base_url}/risk/?item_type=risk",
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Risk list endpoint works for {user['username']}")
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ Risk list endpoint failed for {user['username']}")
                    print(f"Response: {response.text}")
                
                # Test risk stats endpoint
                print(f"Testing risk stats endpoint with {user['username']}...")
                response = requests.get(
                    f"{base_url}/risk/stats/overview",
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Risk stats endpoint works for {user['username']}")
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ Risk stats endpoint failed for {user['username']}")
                    print(f"Response: {response.text}")
                    
                break  # Stop after first successful login
                    
            else:
                print(f"❌ Login failed for {user['username']}: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {user['username']}: {e}")

if __name__ == "__main__":
    print("=== Risk Endpoint Authentication Test ===\n")
    test_risk_endpoints()
    print("\n=== Test completed ===")
