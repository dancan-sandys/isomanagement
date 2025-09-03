#!/usr/bin/env python3
"""
Simple test to verify PESTEL endpoint works after fixing the is_active issue
"""

import requests

def test_pestel_endpoint():
    """Test the PESTEL analytics endpoint"""
    try:
        response = requests.get(
            'http://localhost:8000/api/v1/swot-pestel/analytics/pestel-summary',
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PESTEL endpoint working!")
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"❌ PESTEL endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    print("🧪 Testing PESTEL Analytics Endpoint")
    print("=" * 50)
    test_pestel_endpoint()
