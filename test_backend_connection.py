#!/usr/bin/env python3
"""
Test script to check backend connectivity
"""

import requests
import json

def test_backend_connection():
    """Test if the backend is running and accessible"""
    
    print("Testing Backend Connection")
    print("=" * 40)
    
    # Test 1: Check if backend is running
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        print("   Please start the backend server with: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False
    
    # Test 2: Check API docs
    print("\n2. Testing API Documentation...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print(f"⚠️  API docs responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing API docs: {e}")
    
    # Test 3: Check auth endpoint
    print("\n3. Testing Auth Endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/auth/me", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Auth endpoint is working (401 expected without token)")
        else:
            print(f"⚠️  Auth endpoint responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing auth endpoint: {e}")
    
    # Test 4: Test login endpoint format
    print("\n4. Testing Login Endpoint Format...")
    try:
        # Test with proper form data
        form_data = {
            'username': 'test',
            'password': 'test'
        }
        response = requests.post("http://localhost:8000/api/v1/auth/login", data=form_data, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Login endpoint accepts form data (401 expected for invalid credentials)")
        else:
            print(f"⚠️  Login endpoint responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing login endpoint: {e}")
    
    print("\n" + "=" * 40)
    print("Backend Connection Test Complete")
    return True

if __name__ == "__main__":
    test_backend_connection() 