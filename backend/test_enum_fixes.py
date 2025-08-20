#!/usr/bin/env python3
"""
Test script to verify all enum fixes are working properly
"""

import requests
import json
import sys

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "eng_manager", "password": "test123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_endpoint(endpoint, token, description):
    """Test an endpoint and report results"""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ {description}: SUCCESS")
            return True
        else:
            print(f"❌ {description}: FAILED ({response.status_code})")
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    print(f"   Validation error: {error_data.get('error', 'Unknown')}")
                except:
                    pass
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {str(e)}")
        return False

def main():
    """Main test function"""
    print("🔍 Testing Enum Fixes")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    print("✅ Authentication successful")
    
    # Test endpoints that were previously failing due to enum issues
    tests = [
        ("/api/v1/suppliers/", "Suppliers List"),
        ("/api/v1/suppliers/1", "Supplier Detail"),
        ("/api/v1/traceability/recalls/", "Recalls List"),
        ("/api/v1/equipment/stats", "Equipment Stats"),
        ("/api/v1/equipment/upcoming-maintenance", "Equipment Maintenance"),
        ("/api/v1/equipment/overdue-calibrations", "Equipment Calibrations"),
        ("/api/v1/equipment/alerts", "Equipment Alerts"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for endpoint, description in tests:
        if test_endpoint(endpoint, token, description):
            success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("✅ All enum fixes verified successfully!")
        return True
    else:
        print("❌ Some enum issues may still exist")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
