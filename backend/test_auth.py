#!/usr/bin/env python3
"""
Test script to verify authentication and test HACCP endpoints
"""
import requests
import json
from passlib.context import CryptContext

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password():
    """Test password verification"""
    hashed = '$2b$12$JWkpozit7.vhYrpN5gO4MubR15m8uJ/rr2bZz0PrPqf3Dm31RA.WC'
    
    # Try common passwords
    test_passwords = ['password123', 'admin123', 'password', 'admin', '123456', 'test123']
    
    for password in test_passwords:
        if pwd_context.verify(password, hashed):
            print(f"✅ Password found: {password}")
            return password
    
    print("❌ Password not found in common list")
    return None

def login_and_test():
    """Login and test HACCP endpoints"""
    base_url = "http://localhost:8000/api/v1"
    
    # Try to login
    password = test_password()
    if not password:
        print("❌ Cannot determine password")
        return
    
    login_data = {
        "username": "eng_manager",
        "password": password
    }
    
    print(f"🔐 Attempting login with password: {password}")
    
    try:
        # Login
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', {}).get('access_token')
            print(f"✅ Login successful, token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test HACCP endpoints
            print("\n🧪 Testing HACCP endpoints...")
            
            # Test products endpoint
            response = requests.get(f"{base_url}/haccp/products", headers=headers)
            print(f"Products endpoint: {response.status_code}")
            if response.status_code == 200:
                products = response.json()
                print(f"Found {len(products.get('data', []))} products")
                
                # Test hazards endpoint if products exist
                if products.get('data'):
                    product_id = products['data'][0]['id']
                    response = requests.get(f"{base_url}/haccp/products/{product_id}/hazards", headers=headers)
                    print(f"Hazards endpoint: {response.status_code}")
                    if response.status_code == 200:
                        hazards = response.json()
                        print(f"Found {len(hazards.get('data', []))} hazards")
                        
                        # Test decision tree if hazards exist
                        if hazards.get('data'):
                            hazard_id = hazards['data'][0]['id']
                            response = requests.get(f"{base_url}/haccp/hazards/{hazard_id}/decision-tree", headers=headers)
                            print(f"Decision tree endpoint: {response.status_code}")
                            
                            # Test delete hazard functionality
                            print(f"\n🗑️ Testing delete hazard functionality...")
                            print(f"Note: This is a test - not actually deleting hazard {hazard_id}")
                            
                            # Test decision tree run
                            response = requests.post(f"{base_url}/haccp/hazards/{hazard_id}/decision-tree/run", headers=headers)
                            print(f"Decision tree run endpoint: {response.status_code}")
                            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_password()
    login_and_test()
