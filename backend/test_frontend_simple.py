#!/usr/bin/env python3
"""
Simple test to check frontend-backend communication
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple():
    """Simple test to check backend response"""
    print("=== SIMPLE FRONTEND-BACKEND TEST ===")
    
    # Test without authentication first
    print("1. Testing roles endpoint without auth...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/rbac/roles")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Expected 401 - authentication required")
        else:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with CORS headers
    print("\n2. Testing with CORS headers...")
    try:
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization"
        }
        response = requests.options(f"{BASE_URL}/api/v1/rbac/roles", headers=headers)
        print(f"OPTIONS status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple()
