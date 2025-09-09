#!/usr/bin/env python3
"""
Test script to verify RBAC endpoints are working
"""

import requests
import json

def test_rbac_endpoints():
    base_url = "http://localhost:8000/api/v1"
    
    # First, login to get a token
    print("🔐 Logging in...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", data=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Test roles endpoint
        print("\n📋 Testing roles endpoint...")
        roles_response = requests.get(f"{base_url}/rbac/roles", headers=headers)
        print(f"Status: {roles_response.status_code}")
        if roles_response.status_code == 200:
            roles = roles_response.json()
            print(f"✅ Found {len(roles)} roles:")
            for role in roles:
                print(f"  - {role['name']}: {role['description']}")
        else:
            print(f"❌ Roles endpoint failed: {roles_response.text}")
        
        # Test permissions endpoint
        print("\n🔑 Testing permissions endpoint...")
        permissions_response = requests.get(f"{base_url}/rbac/permissions", headers=headers)
        print(f"Status: {permissions_response.status_code}")
        if permissions_response.status_code == 200:
            permissions = permissions_response.json()
            print(f"✅ Found {permissions['total']} permissions")
            print(f"Data structure: {list(permissions.keys())}")
        else:
            print(f"❌ Permissions endpoint failed: {permissions_response.text}")
        
        # Test role summary endpoint
        print("\n📊 Testing role summary endpoint...")
        summary_response = requests.get(f"{base_url}/rbac/roles/summary", headers=headers)
        print(f"Status: {summary_response.status_code}")
        if summary_response.status_code == 200:
            summary = summary_response.json()
            print(f"✅ Role summary loaded successfully")
            print(f"Data structure: {list(summary.keys())}")
        else:
            print(f"❌ Role summary endpoint failed: {summary_response.text}")
        
        # Test permission matrix endpoint
        print("\n🔢 Testing permission matrix endpoint...")
        matrix_response = requests.get(f"{base_url}/rbac/permissions/matrix", headers=headers)
        print(f"Status: {matrix_response.status_code}")
        if matrix_response.status_code == 200:
            matrix = matrix_response.json()
            print(f"✅ Permission matrix loaded successfully")
            print(f"Data structure: {list(matrix.keys())}")
        else:
            print(f"❌ Permission matrix endpoint failed: {matrix_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rbac_endpoints()
