#!/usr/bin/env python3
"""
Test script to check suppliers endpoints.
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                return data['access_token']
            elif 'data' in data and 'access_token' in data['data']:
                return data['data']['access_token']
        
        print(f"Failed to get auth token: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Error getting auth token: {str(e)}")
        return None

def test_suppliers_endpoints():
    """Test suppliers endpoints"""
    print("Testing Suppliers Endpoints...")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return False
    
    print(f"✅ Got authentication token")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test basic suppliers endpoints
    endpoints = [
        ("GET", "/suppliers", "List Suppliers"),
        ("POST", "/suppliers", "Create Supplier"),
        ("GET", "/suppliers/1", "Get Supplier by ID"),
        ("PUT", "/suppliers/1", "Update Supplier"),
        ("DELETE", "/suppliers/1", "Delete Supplier"),
        
        # Materials endpoints
        ("GET", "/suppliers/materials", "List Materials"),
        ("POST", "/suppliers/materials", "Create Material"),
        ("GET", "/suppliers/materials/1", "Get Material by ID"),
        ("PUT", "/suppliers/materials/1", "Update Material"),
        ("DELETE", "/suppliers/materials/1", "Delete Material"),
        
        # Evaluations endpoints
        ("GET", "/suppliers/evaluations", "List Evaluations"),
        ("POST", "/suppliers/evaluations", "Create Evaluation"),
        ("GET", "/suppliers/evaluations/1", "Get Evaluation by ID"),
        ("PUT", "/suppliers/evaluations/1", "Update Evaluation"),
        ("DELETE", "/suppliers/evaluations/1", "Delete Evaluation"),
        
        # Deliveries endpoints
        ("GET", "/suppliers/deliveries", "List Deliveries"),
        ("POST", "/suppliers/deliveries", "Create Delivery"),
        ("GET", "/suppliers/deliveries/1", "Get Delivery by ID"),
        ("PUT", "/suppliers/deliveries/1", "Update Delivery"),
        ("DELETE", "/suppliers/deliveries/1", "Delete Delivery"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nTesting: {description}")
            print(f"   URL: {method} {url}")
            
            # For POST/PUT requests, send minimal data
            data = None
            if method in ["POST", "PUT"]:
                if "materials" in endpoint:
                    data = {"name": "Test Material", "supplier_id": 1}
                elif "evaluations" in endpoint:
                    data = {"supplier_id": 1, "score": 85}
                elif "deliveries" in endpoint:
                    data = {"supplier_id": 1, "delivery_date": "2024-01-01"}
                else:
                    data = {"name": "Test Supplier", "contact_email": "test@example.com"}
            
            response = requests.request(method, url, headers=headers, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("SUCCESS", description))
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND (Status: {response.status_code}) - Endpoint missing")
                results.append(("MISSING", description))
            elif response.status_code == 422:
                print(f"   ⚠️  VALIDATION ERROR (Status: {response.status_code}) - Endpoint exists but validation failed")
                results.append(("VALIDATION_ERROR", description))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("FAILED", description))
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT (10s)")
            results.append(("TIMEOUT", description))
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(("ERROR", description))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for status, _ in results if status == "SUCCESS")
    missing_count = sum(1 for status, _ in results if status == "MISSING")
    total_count = len(results)
    
    for status, description in results:
        print(f"{status} {description}: {status}")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"Missing Endpoints: {missing_count}")
    
    return success_count, missing_count, total_count

def main():
    """Main function"""
    print("🔍 Testing Suppliers Endpoints")
    print("=" * 50)
    
    success_count, missing_count, total_count = test_suppliers_endpoints()
    
    if success_count == total_count:
        print("\n✅ All suppliers endpoints are working!")
    elif missing_count > 0:
        print(f"\n⚠️  Found {missing_count} missing endpoints that need to be implemented.")
    else:
        print("\n⚠️  Some endpoints have issues that need to be fixed.")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
