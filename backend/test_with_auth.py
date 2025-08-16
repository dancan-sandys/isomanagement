#!/usr/bin/env python3
"""
Test script with authentication to properly test the endpoints.
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
        
        print(f"Failed to get auth token: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Error getting auth token: {str(e)}")
        return None

def test_traceability_endpoints_with_auth():
    """Test traceability endpoints with authentication"""
    print("Testing Traceability Endpoints with Authentication...")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return False
    
    print(f"✅ Got authentication token")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        ("GET", "/traceability/batches", "List Batches"),
        ("GET", "/traceability/recalls", "List Recalls"),
        ("GET", "/traceability/dashboard", "Dashboard"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nTesting: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("SUCCESS", description))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("FAILED", description))
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT (10s)")
            results.append(("TIMEOUT", description))
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(("ERROR", description))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for status, _ in results if status == "SUCCESS")
    total_count = len(results)
    
    for status, description in results:
        print(f"{status} {description}: {status}")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

def main():
    """Main function"""
    print("🔍 Testing with Authentication")
    print("=" * 50)
    
    success = test_traceability_endpoints_with_auth()
    
    if success:
        print("\n✅ All tests passed! All endpoints are working properly.")
        print("🎉 Phase 2.1 COMPLETED - Traceability endpoints are fully functional!")
    else:
        print("\n⚠️  Some tests failed. Check the specific errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
