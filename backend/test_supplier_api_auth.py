#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for supplier API endpoints with authentication
"""
import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return None

def test_supplier_api_with_auth():
    """Test supplier API endpoints with authentication"""
    print("Testing Supplier API endpoints with authentication...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get suppliers list
    print("\n1. Testing Suppliers List...")
    try:
        response = requests.get(f"{API_BASE}/suppliers/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Suppliers list: {len(data.get('data', {}).get('items', []))} suppliers found")
        elif response.status_code == 422:
            print(f"❌ Validation error: {response.text}")
        else:
            print(f"❌ Failed to get suppliers list: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing suppliers list: {e}")
    
    # Test 2: Get supplier dashboard stats
    print("\n2. Testing Supplier Dashboard Stats...")
    try:
        response = requests.get(f"{API_BASE}/suppliers/dashboard/stats", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard stats: {data.get('data', {}).get('total_suppliers', 0)} total suppliers")
        elif response.status_code == 422:
            print(f"❌ Validation error: {response.text}")
        else:
            print(f"❌ Failed to get dashboard stats: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing dashboard stats: {e}")
    
    # Test 3: Get materials list
    print("\n3. Testing Materials List...")
    try:
        response = requests.get(f"{API_BASE}/suppliers/materials/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Materials list: {len(data.get('data', {}).get('items', []))} materials found")
        elif response.status_code == 422:
            print(f"❌ Validation error: {response.text}")
        else:
            print(f"❌ Failed to get materials list: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing materials list: {e}")

if __name__ == "__main__":
    test_supplier_api_with_auth()
