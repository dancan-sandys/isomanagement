#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify suppliers endpoints fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_suppliers_endpoints():
    """Test the suppliers endpoints to verify the fix"""
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        print("Testing suppliers endpoints fix...")
        
        # First, try to login to get a token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(f"{base_url}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        # Extract token
        token_data = login_response.json()
        access_token = token_data.get("data", {}).get("access_token")
        if not access_token:
            print("❌ No access token found in login response")
            return
        
        print("✅ Login successful")
        
        # Set up headers with token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test the specific failing endpoints
        failing_endpoints = [
            ("GET", "/suppliers/materials"),
            ("GET", "/suppliers/evaluations"),
            ("GET", "/suppliers/deliveries"),
        ]
        
        print("\nTesting previously failing endpoints:")
        for method, endpoint in failing_endpoints:
            print(f"\nTesting {method} {endpoint}...")
            
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 422:
                    print(f"❌ Still getting 422 error for {endpoint}")
                    print(f"Response: {response.text}")
                elif response.status_code == 200:
                    print(f"✅ {endpoint} is now working!")
                    data = response.json()
                    if 'data' in data and 'items' in data['data']:
                        print(f"   Found {len(data['data']['items'])} items")
                else:
                    print(f"⚠️ {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exception testing {endpoint}: {e}")
        
        print("\n✅ Test completed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_suppliers_endpoints()
