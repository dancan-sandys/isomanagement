#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to help identify frontend authentication issues
"""
import requests
import json

def debug_frontend_auth():
    """Debug frontend authentication issues"""
    print("=== Frontend Authentication Debug ===\n")
    
    print("🔍 To debug the frontend authentication issue:")
    print("\n1. Open your browser's Developer Tools (F12)")
    print("2. Go to the Application/Storage tab")
    print("3. Check Local Storage for your domain")
    print("4. Look for these keys:")
    print("   - access_token")
    print("   - refresh_token")
    print("\n5. If tokens exist, copy the access_token value")
    print("6. Run this script with the token to test it")
    
    print("\n=== Manual Token Test ===")
    print("If you have a token, you can test it manually:")
    print("1. Copy your access_token from browser localStorage")
    print("2. Run: python debug_frontend_auth.py <your_token>")
    print("3. This will test if the token is valid")

def test_token(token):
    """Test a specific token"""
    base_url = "http://localhost:8000/api/v1"
    
    print(f"\n=== Testing Token: {token[:50]}... ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET /auth/me
    try:
        response = requests.get(f"{base_url}/auth/me", headers=headers)
        print(f"GET /auth/me status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token is valid!")
            print(f"User: {user_data.get('data', {}).get('username', 'Unknown')}")
            
            # Test POST /risk/ with correct data
            risk_data = {
                "title": "Test Risk",
                "description": "Test risk description",
                "item_type": "risk",
                "category": "process",  # Correct enum value
                "severity": "medium",
                "likelihood": "possible",  # Correct enum value
                "classification": "food_safety"  # Correct enum value
            }
            
            response = requests.post(f"{base_url}/risk/", json=risk_data, headers=headers)
            print(f"POST /risk/ status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ POST /risk/ successful!")
            else:
                print(f"❌ POST /risk/ failed: {response.text}")
        else:
            print(f"❌ Token is invalid: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing token: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
        test_token(token)
    else:
        debug_frontend_auth()
