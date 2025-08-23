#!/usr/bin/env python3
"""
Comprehensive debug script to identify login endpoint issues
"""
import requests
import json
import sys
import os

def test_backend_directly():
    """Test the backend login endpoint directly"""
    print("🔍 Testing Backend Login Endpoint Directly...")
    print("=" * 60)
    
    # Test the correct endpoint
    url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print(f"🧪 Testing URL: {url}")
    print(f"📋 Data: {login_data}")
    print(f"📋 Headers: {headers}")
    
    try:
        response = requests.post(url, data=login_data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Backend login endpoint is working")
            data = response.json()
            print(f"👤 User: {data.get('data', {}).get('user', {}).get('username')}")
            print(f"🔑 Token: {data.get('data', {}).get('access_token', '')[:50]}...")
            return True
        elif response.status_code == 404:
            print("❌ 404 Not Found - Endpoint doesn't exist")
            print(f"📄 Response: {response.text}")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frontend_proxy():
    """Test the frontend proxy configuration"""
    print("\n🔍 Testing Frontend Proxy Configuration...")
    print("=" * 60)
    
    # Test through the frontend proxy (assuming frontend is running on 3000)
    url = "http://localhost:3000/api/v1/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print(f"🧪 Testing Frontend Proxy URL: {url}")
    print(f"📋 Data: {login_data}")
    print(f"📋 Headers: {headers}")
    
    try:
        response = requests.post(url, data=login_data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Frontend proxy is working")
            data = response.json()
            print(f"👤 User: {data.get('data', {}).get('user', {}).get('username')}")
            return True
        elif response.status_code == 404:
            print("❌ 404 Not Found - Proxy issue")
            print(f"📄 Response: {response.text}")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_backend_routes():
    """Check what routes are available on the backend"""
    print("\n🔍 Checking Backend Routes...")
    print("=" * 60)
    
    try:
        # Get OpenAPI schema
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            
            print("📋 Available API endpoints:")
            auth_endpoints = [path for path in paths.keys() if 'auth' in path]
            for path in auth_endpoints:
                methods = list(paths[path].keys())
                print(f"  {path}: {methods}")
            
            # Check specifically for login
            login_paths = [path for path in paths.keys() if 'login' in path]
            if login_paths:
                print(f"\n✅ Login endpoints found: {login_paths}")
            else:
                print("\n❌ No login endpoints found!")
                
        else:
            print(f"❌ Could not get OpenAPI schema: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking routes: {e}")

def check_backend_status():
    """Check if backend is running and healthy"""
    print("\n🔍 Checking Backend Status...")
    print("=" * 60)
    
    try:
        # Health check
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            data = response.json()
            print(f"📊 Status: {data.get('status')}")
            print(f"📊 Environment: {data.get('environment')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def main():
    """Main debug function"""
    print("🚀 Login Endpoint Debug Script")
    print("=" * 60)
    
    # Check backend status first
    if not check_backend_status():
        print("\n❌ Backend is not running or not accessible!")
        print("💡 Make sure to start the backend with: python -m uvicorn app.main:app --reload")
        return
    
    # Check available routes
    check_backend_routes()
    
    # Test backend directly
    backend_works = test_backend_directly()
    
    # Test frontend proxy
    frontend_works = test_frontend_proxy()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print(f"  Backend direct access: {'✅ Working' if backend_works else '❌ Failed'}")
    print(f"  Frontend proxy access: {'✅ Working' if frontend_works else '❌ Failed'}")
    
    if backend_works and not frontend_works:
        print("\n🔧 Issue identified: Backend works but frontend proxy doesn't")
        print("💡 Solutions:")
        print("  1. Check if frontend is running on port 3000")
        print("  2. Check setupProxy.js configuration")
        print("  3. Check browser console for errors")
        print("  4. Restart frontend development server")
    elif not backend_works:
        print("\n🔧 Issue identified: Backend login endpoint is not working")
        print("💡 Solutions:")
        print("  1. Check backend logs for errors")
        print("  2. Verify auth router is properly included")
        print("  3. Check if admin user exists in database")
        print("  4. Restart backend server")
    else:
        print("\n✅ Everything is working correctly!")

if __name__ == "__main__":
    main()


