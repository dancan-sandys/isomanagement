#!/usr/bin/env python3
"""
Detailed test script to verify RBAC endpoints and response formats
"""

import requests
import json

def test_rbac_detailed():
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
            print(f"✅ Roles response type: {type(roles)}")
            print(f"✅ Roles count: {len(roles) if isinstance(roles, list) else 'Not a list'}")
            if isinstance(roles, list) and len(roles) > 0:
                print(f"✅ First role structure: {list(roles[0].keys())}")
        else:
            print(f"❌ Roles endpoint failed: {roles_response.text}")
        
        # Test permissions endpoint
        print("\n🔑 Testing permissions endpoint...")
        permissions_response = requests.get(f"{base_url}/rbac/permissions", headers=headers)
        print(f"Status: {permissions_response.status_code}")
        if permissions_response.status_code == 200:
            permissions = permissions_response.json()
            print(f"✅ Permissions response type: {type(permissions)}")
            print(f"✅ Permissions keys: {list(permissions.keys()) if isinstance(permissions, dict) else 'Not a dict'}")
            if isinstance(permissions, dict) and 'data' in permissions:
                print(f"✅ Permissions data type: {type(permissions['data'])}")
                print(f"✅ Permissions count: {len(permissions['data']) if isinstance(permissions['data'], list) else 'Not a list'}")
        else:
            print(f"❌ Permissions endpoint failed: {permissions_response.text}")
        
        # Test role summary endpoint
        print("\n📊 Testing role summary endpoint...")
        summary_response = requests.get(f"{base_url}/rbac/roles/summary", headers=headers)
        print(f"Status: {summary_response.status_code}")
        if summary_response.status_code == 200:
            summary = summary_response.json()
            print(f"✅ Summary response type: {type(summary)}")
            print(f"✅ Summary keys: {list(summary.keys()) if isinstance(summary, dict) else 'Not a dict'}")
            if isinstance(summary, dict) and 'data' in summary:
                print(f"✅ Summary data type: {type(summary['data'])}")
                print(f"✅ Summary count: {len(summary['data']) if isinstance(summary['data'], list) else 'Not a list'}")
                if isinstance(summary['data'], list) and len(summary['data']) > 0:
                    print(f"✅ First summary item keys: {list(summary['data'][0].keys())}")
        else:
            print(f"❌ Role summary endpoint failed: {summary_response.text}")
        
        # Test permission matrix endpoint
        print("\n🔢 Testing permission matrix endpoint...")
        matrix_response = requests.get(f"{base_url}/rbac/permissions/matrix", headers=headers)
        print(f"Status: {matrix_response.status_code}")
        if matrix_response.status_code == 200:
            matrix = matrix_response.json()
            print(f"✅ Matrix response type: {type(matrix)}")
            print(f"✅ Matrix keys: {list(matrix.keys()) if isinstance(matrix, dict) else 'Not a dict'}")
            if isinstance(matrix, dict) and 'data' in matrix:
                print(f"✅ Matrix data type: {type(matrix['data'])}")
                print(f"✅ Matrix data keys: {list(matrix['data'].keys()) if isinstance(matrix['data'], dict) else 'Not a dict'}")
        else:
            print(f"❌ Permission matrix endpoint failed: {matrix_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rbac_detailed()
