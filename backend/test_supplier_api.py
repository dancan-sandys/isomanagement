#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for supplier API endpoints
"""
import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api/v1"

def test_supplier_api():
    """Test supplier API endpoints"""
    print("Testing Supplier API endpoints...")
    
    # Test 1: Get suppliers list
    print("\n1. Testing Suppliers List...")
    try:
        response = requests.get(f"{API_BASE}/suppliers/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Suppliers list: {len(data.get('data', {}).get('items', []))} suppliers found")
        else:
            print(f"❌ Failed to get suppliers list: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing suppliers list: {e}")
    
    # Test 2: Get supplier dashboard stats
    print("\n2. Testing Supplier Dashboard Stats...")
    try:
        response = requests.get(f"{API_BASE}/suppliers/dashboard/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard stats: {data.get('data', {}).get('total_suppliers', 0)} total suppliers")
        else:
            print(f"❌ Failed to get dashboard stats: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing dashboard stats: {e}")
    
    # Test 3: Get materials list
    print("\n3. Testing Materials List...")
    try:
        response = requests.get(f"{API_BASE}/suppliers/materials/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Materials list: {len(data.get('data', {}).get('items', []))} materials found")
        else:
            print(f"❌ Failed to get materials list: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing materials list: {e}")

if __name__ == "__main__":
    test_supplier_api()
