#!/usr/bin/env python3
"""
Test script to verify the login endpoint is working correctly
"""
import requests
import json

def test_login_endpoint():
    """Test the login endpoint directly"""
    
    print("🔍 Testing Login Endpoint...")
    print("=" * 50)
    
    # Test different URLs
    test_urls = [
        "http://localhost:8000/api/v1/auth/login",
        "http://localhost:8000/auth/login",
        "http://localhost:8000/api/v1/auth/login/",
    ]
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    for url in test_urls:
        print(f"\n🧪 Testing URL: {url}")
        try:
            response = requests.post(url, data=login_data, headers=headers)
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                print(f"   User: {data.get('data', {}).get('user', {}).get('username')}")
                print(f"   Token: {data.get('data', {}).get('access_token', '')[:50]}...")
            elif response.status_code == 404:
                print("   ❌ 404 Not Found")
                print(f"   Response: {response.text}")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("If you see 404 errors, the endpoint path is incorrect")
    print("If you see 200 success, the endpoint is working")
    print("Check the backend logs for more details")

if __name__ == "__main__":
    test_login_endpoint()




