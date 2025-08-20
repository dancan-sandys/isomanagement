#!/usr/bin/env python3
"""
Test script to simulate frontend authentication flow and debug 403 issues
"""
import requests
import json

def test_frontend_auth_flow():
    """Test the complete frontend authentication flow"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=== Frontend Authentication Flow Test ===\n")
    
    # Step 1: Login with the credentials the user is using
    print("1. Testing login with 'string' user and 'Test123*' password...")
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
        
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            
            # Extract tokens
            access_token = token_data.get("data", {}).get("access_token")
            refresh_token = token_data.get("data", {}).get("refresh_token")
            user_data = token_data.get("data", {}).get("user", {})
            
            print(f"User ID: {user_data.get('id')}")
            print(f"Username: {user_data.get('username')}")
            print(f"Role: {user_data.get('role_name')}")
            print(f"Access Token: {access_token[:50]}...")
            
            # Step 2: Test /auth/me endpoint (like frontend does)
            print("\n2. Testing /auth/me endpoint...")
            me_response = requests.get(
                f"{base_url}/auth/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"/auth/me status: {me_response.status_code}")
            if me_response.status_code == 200:
                print("✅ /auth/me successful!")
                me_data = me_response.json()
                print(f"User data: {me_data.get('data', {}).get('username')}")
            else:
                print(f"❌ /auth/me failed: {me_response.text}")
            
            # Step 3: Test risk endpoints with the same token
            print("\n3. Testing risk endpoints...")
            
            # Test GET /risk/
            risk_response = requests.get(
                f"{base_url}/risk/",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"GET /risk/ status: {risk_response.status_code}")
            if risk_response.status_code == 200:
                print("✅ GET /risk/ successful!")
                risk_data = risk_response.json()
                print(f"Risk items count: {risk_data.get('data', {}).get('total', 0)}")
            else:
                print(f"❌ GET /risk/ failed: {risk_response.text}")
            
            # Test GET /risk/stats/overview
            stats_response = requests.get(
                f"{base_url}/risk/stats/overview",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"GET /risk/stats/overview status: {stats_response.status_code}")
            if stats_response.status_code == 200:
                print("✅ GET /risk/stats/overview successful!")
            else:
                print(f"❌ GET /risk/stats/overview failed: {stats_response.text}")
            
            # Step 4: Test with query parameters (like frontend does)
            print("\n4. Testing risk endpoint with query parameters...")
            risk_with_params_response = requests.get(
                f"{base_url}/risk/?item_type=risk",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"GET /risk/?item_type=risk status: {risk_with_params_response.status_code}")
            if risk_with_params_response.status_code == 200:
                print("✅ GET /risk/?item_type=risk successful!")
            else:
                print(f"❌ GET /risk/?item_type=risk failed: {risk_with_params_response.text}")
            
            # Step 5: Check user permissions
            print("\n5. Checking user permissions...")
            # We can't directly check permissions via API, but we can verify the user has the right role
            print(f"User role: {user_data.get('role_name')}")
            print(f"User ID: {user_data.get('id')}")
            
            # Step 6: Test token format
            print("\n6. Analyzing token format...")
            try:
                import jwt
                # Decode token without verification to see payload
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                print(f"Token payload: {json.dumps(decoded, indent=2)}")
            except ImportError:
                print("JWT library not available, skipping token analysis")
            except Exception as e:
                print(f"Error decoding token: {e}")
            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_frontend_auth_flow()


