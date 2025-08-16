#!/usr/bin/env python3
"""
Test script to verify audit endpoints work after schema migration with authentication.
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                return data['access_token']
            elif 'data' in data and 'access_token' in data['data']:
                return data['data']['access_token']
        
        print(f"Failed to get auth token: {response.status_code}")
        print(f"Response: {response.text}")
        return None
        
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def test_audit_endpoints():
    """Test all audit endpoints"""
    print("Testing Audit Endpoints with Authentication...")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints
    endpoints = [
        ("GET", "/audits/", "List Audits"),
        ("GET", "/audits/stats", "Audit Statistics"),
        ("GET", "/audits/kpis/overview", "Audit KPIs"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nTesting: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   SUCCESS (Status: {response.status_code})")
                results.append(("SUCCESS", description, "SUCCESS"))
            else:
                print(f"   FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("FAILED", description, f"Status {response.status_code}"))
                
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append(("ERROR", description, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    success_count = sum(1 for result in results if result[0] == "SUCCESS")
    total_count = len(results)
    
    for status, description, details in results:
        print(f"{status} {description}: {details}")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_audit_endpoints()
    sys.exit(0 if success else 1)
