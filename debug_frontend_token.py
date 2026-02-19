#!/usr/bin/env python3
"""
Debug script to check frontend token usage
"""
import requests
import json

def debug_frontend_token():
    """Debug the frontend token issue"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=== Frontend Token Debug ===\n")
    
    # Step 1: Login and get token
    print("1. Getting fresh token...")
    login_data = {
        "username": "string",
        "password": "Test123*"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("data", {}).get("access_token")
            user_data = token_data.get("data", {}).get("user", {})
            
            print(f"✅ Login successful!")
            print(f"User ID: {user_data.get('id')}")
            print(f"Username: {user_data.get('username')}")
            print(f"Token: {access_token}")
            
            # Step 2: Test the exact request the frontend is making
            print("\n2. Testing exact frontend request...")
            
            # The frontend is making this request: GET /api/v1/risk/?item_type=risk
            # Let's test it with the proxy URL
            proxy_url = "http://localhost:3000/api/v1/risk/?item_type=risk"
            
            proxy_response = requests.get(
                proxy_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Proxy request status: {proxy_response.status_code}")
            if proxy_response.status_code == 200:
                print("✅ Proxy request successful!")
            else:
                print(f"❌ Proxy request failed: {proxy_response.text}")
            
            # Step 3: Test direct backend request for comparison
            print("\n3. Testing direct backend request...")
            
            backend_response = requests.get(
                f"{base_url}/risk/?item_type=risk",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Direct backend request status: {backend_response.status_code}")
            if backend_response.status_code == 200:
                print("✅ Direct backend request successful!")
            else:
                print(f"❌ Direct backend request failed: {backend_response.text}")
            
            # Step 4: Check if there's a difference in headers
            print("\n4. Comparing request headers...")
            print("Proxy request headers:")
            for key, value in proxy_response.request.headers.items():
                print(f"  {key}: {value}")
            
            print("\nDirect backend request headers:")
            for key, value in backend_response.request.headers.items():
                print(f"  {key}: {value}")
            
            # Step 5: Test with different user agents
            print("\n5. Testing with browser user agent...")
            
            browser_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
            }
            
            browser_response = requests.get(
                f"{base_url}/risk/?item_type=risk",
                headers=browser_headers
            )
            
            print(f"Browser user agent request status: {browser_response.status_code}")
            if browser_response.status_code == 200:
                print("✅ Browser user agent request successful!")
            else:
                print(f"❌ Browser user agent request failed: {browser_response.text}")
            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_frontend_token()


