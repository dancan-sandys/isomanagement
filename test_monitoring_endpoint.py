#!/usr/bin/env python3
"""
Test script for monitoring endpoint
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

# Test credentials (you may need to adjust these)
test_credentials = {
    "username": "admin@example.com",
    "password": "admin123"
}

def test_monitoring_endpoint():
    """Test the monitoring endpoint"""
    
    # Step 1: Login to get access token
    print("🔐 Logging in...")
    try:
        login_response = requests.post(LOGIN_URL, json=test_credentials)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            print("❌ No access token in response")
            return False
        
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get products to find a CCP
    print("\n📋 Getting products...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        products_response = requests.get(f"{BASE_URL}/haccp/products", headers=headers)
        if products_response.status_code != 200:
            print(f"❌ Failed to get products: {products_response.status_code}")
            print(f"Response: {products_response.text}")
            return False
        
        products_data = products_response.json()
        products = products_data.get("data", {}).get("items", [])
        
        if not products:
            print("❌ No products found")
            return False
        
        print(f"✅ Found {len(products)} products")
        
        # Find a product with CCPs
        product_with_ccps = None
        for product in products:
            if product.get("ccps") and len(product["ccps"]) > 0:
                product_with_ccps = product
                break
        
        if not product_with_ccps:
            print("❌ No products with CCPs found")
            return False
        
        print(f"✅ Found product with CCPs: {product_with_ccps.get('name', 'Unknown')}")
        
        # Get the first CCP
        ccp = product_with_ccps["ccps"][0]
        ccp_id = ccp["id"]
        print(f"✅ Using CCP ID: {ccp_id}")
        
    except Exception as e:
        print(f"❌ Error getting products: {e}")
        return False
    
    # Step 3: Test monitoring endpoint
    print(f"\n🧪 Testing monitoring endpoint for CCP {ccp_id}...")
    
    test_data = {
        "measured_value": 25.5,
        "unit": "°C",
        "observations": "Test monitoring log from automated test"
    }
    
    try:
        monitoring_url = f"{BASE_URL}/haccp/ccps/{ccp_id}/monitoring-logs/enhanced"
        monitoring_response = requests.post(
            monitoring_url, 
            json=test_data, 
            headers=headers
        )
        
        print(f"Status Code: {monitoring_response.status_code}")
        print(f"Response: {monitoring_response.text}")
        
        if monitoring_response.status_code == 200:
            print("✅ Monitoring endpoint test PASSED!")
            return True
        else:
            print("❌ Monitoring endpoint test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing monitoring endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting monitoring endpoint test...")
    success = test_monitoring_endpoint()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
