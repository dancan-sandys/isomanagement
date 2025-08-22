#!/usr/bin/env python3
"""
Test script to verify that 403 errors have been resolved
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

def login_as_admin():
    """Login as admin and return the access token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        if response.status_code == 200:
            response_data = response.json()
            # Check different possible response formats
            if "access_token" in response_data:
                token = response_data["access_token"]
            elif "data" in response_data and "access_token" in response_data["data"]:
                token = response_data["data"]["access_token"]
            else:
                print(f"❌ Unexpected response format: {response_data}")
                return None
            print("✅ Successfully logged in as admin")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_endpoint(endpoint, token, method="GET", data=None):
    """Test a specific endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data or {})
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data or {})
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 403:
            print(f"❌ 403 Forbidden: {endpoint}")
            return False
        elif response.status_code >= 400:
            print(f"⚠️  {response.status_code} Error: {endpoint} - {response.text[:100]}")
            return True  # Not a 403, so permission is working
        else:
            print(f"✅ {response.status_code} Success: {endpoint}")
            return True
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing 403 error fixes...")
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Login as admin
    token = login_as_admin()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test endpoints that were having 403 issues
    test_endpoints = [
        # Risk Management
        ("/api/v1/risk/register", "GET"),
        ("/api/v1/risk/opportunities", "GET"),
        ("/api/v1/risk/assessments", "GET"),
        ("/api/v1/risk/matrices", "GET"),
        
        # Audits
        ("/api/v1/audits/", "GET"),
        ("/api/v1/audits/programs", "GET"),
        ("/api/v1/audits/plans", "GET"),
        
        # Complaints
        ("/api/v1/complaints/", "GET"),
        ("/api/v1/complaints/categories", "GET"),
        
        # Equipment
        ("/api/v1/equipment/", "GET"),
        ("/api/v1/equipment/calibrations", "GET"),
        ("/api/v1/equipment/maintenance", "GET"),
        
        # Management Review
        ("/api/v1/management-reviews/", "GET"),
        ("/api/v1/management-reviews/inputs", "GET"),
        ("/api/v1/management-reviews/outputs", "GET"),
        
        # Other modules
        ("/api/v1/suppliers/", "GET"),
        ("/api/v1/traceability/batches", "GET"),
        ("/api/v1/documents/", "GET"),
        ("/api/v1/haccp/hazards", "GET"),
        ("/api/v1/prp/programs", "GET"),
    ]
    
    success_count = 0
    total_count = len(test_endpoints)
    
    for endpoint, method in test_endpoints:
        if test_endpoint(endpoint, token, method):
            success_count += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All 403 errors have been resolved!")
    else:
        print("⚠️  Some endpoints still have issues")

if __name__ == "__main__":
    main()
