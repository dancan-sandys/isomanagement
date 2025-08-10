#!/usr/bin/env python3
"""
Debug script to test frontend authentication and template creation
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"
TEMPLATES_URL = f"{BASE_URL}/documents/templates"

def test_frontend_auth():
    """Test frontend authentication flow"""
    
    print("Testing Frontend Authentication Flow")
    print("=" * 50)
    
    # Login as admin (simulating frontend login)
    login_data = {
        "username": "admin",
        "password": "admin123456"
    }
    
    try:
        # Step 1: Login (simulating frontend login)
        print("🔐 Step 1: Login")
        login_response = requests.post(LOGIN_URL, data=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
            
        login_data = login_response.json()
        print(f"Login response keys: {list(login_data.keys())}")
        
        if 'data' not in login_data:
            print(f"❌ No 'data' in login response: {login_data}")
            return
            
        access_token = login_data['data']['access_token']
        print(f"✅ Got access token: {access_token[:20]}...")
        
        # Step 2: Test GET templates with token
        print("\n📄 Step 2: Test GET templates with token")
        headers = {"Authorization": f"Bearer {access_token}"}
        get_response = requests.get(TEMPLATES_URL, headers=headers)
        print(f"GET status: {get_response.status_code}")
        print(f"GET response: {get_response.text[:200]}")
        
        # Step 3: Test POST template creation with token
        print("\n📝 Step 3: Test POST template creation with token")
        template_data = {
            "name": "Test Template",
            "description": "A test template for testing",
            "document_type": "procedure",
            "category": "quality",
            "template_content": "This is a test template content."
        }
        
        print(f"POST data: {json.dumps(template_data, indent=2)}")
        print(f"POST headers: {headers}")
        
        post_response = requests.post(TEMPLATES_URL, json=template_data, headers=headers)
        print(f"POST status: {post_response.status_code}")
        print(f"POST response: {post_response.text}")
        
        # Step 4: Test without token (should fail)
        print("\n🚫 Step 4: Test POST without token (should fail)")
        post_no_token = requests.post(TEMPLATES_URL, json=template_data)
        print(f"POST without token status: {post_no_token.status_code}")
        print(f"POST without token response: {post_no_token.text}")
        
        # Step 5: Test with invalid token
        print("\n🚫 Step 5: Test POST with invalid token")
        invalid_headers = {"Authorization": "Bearer invalid_token_123"}
        post_invalid = requests.post(TEMPLATES_URL, json=template_data, headers=invalid_headers)
        print(f"POST with invalid token status: {post_invalid.status_code}")
        print(f"POST with invalid token response: {post_invalid.text}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_frontend_auth()
