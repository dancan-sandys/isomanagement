#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for risk API endpoints
"""
import requests
import json

def test_risk_api():
    """Test risk API endpoints"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=== Risk API Test ===\n")
    
    # Step 1: Login
    print("1. Testing login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
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
            access_token = token_data.get("data", {}).get("access_token")
            
            if access_token:
                print("✅ Login successful")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Step 2: Test GET /risk/
                print("\n2. Testing GET /risk/...")
                response = requests.get(f"{base_url}/risk/", headers=headers)
                print(f"GET /risk/ status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ GET /risk/ successful")
                    data = response.json()
                    print(f"Found {len(data.get('data', []))} risk items")
                else:
                    print(f"❌ GET /risk/ failed: {response.text}")
                
                # Step 3: Test POST /risk/ with correct data
                print("\n3. Testing POST /risk/...")
                risk_data = {
                    "risk_number": "RISK-TEST-001",
                    "title": "Test Risk Item",
                    "description": "Test risk description",
                    "item_type": "risk",
                    "category": "equipment",
                    "severity": "medium",
                    "likelihood": "possible",
                    "classification": "business",
                    "status": "open"
                }
                
                response = requests.post(
                    f"{base_url}/risk/",
                    json=risk_data,
                    headers=headers
                )
                print(f"POST /risk/ status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ POST /risk/ successful")
                else:
                    print(f"❌ POST /risk/ failed: {response.text}")
                
            else:
                print("❌ No access token in response")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_risk_api()
