#!/usr/bin/env python3
"""
Test script to check documents endpoints.
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

def test_documents_endpoints():
    """Test documents endpoints"""
    print("Testing Documents Endpoints...")
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
    
    # Test basic documents endpoints
    endpoints = [
        ("GET", "/documents", "List Documents"),
        ("POST", "/documents", "Create Document"),
        ("GET", "/documents/1", "Get Document by ID"),
        ("PUT", "/documents/1", "Update Document"),
        ("DELETE", "/documents/1", "Delete Document"),
        
        # Document categories
        ("GET", "/documents/categories", "List Document Categories"),
        ("POST", "/documents/categories", "Create Document Category"),
        ("GET", "/documents/categories/1", "Get Category by ID"),
        ("PUT", "/documents/categories/1", "Update Category"),
        ("DELETE", "/documents/categories/1", "Delete Category"),
        
        # Document versions
        ("GET", "/documents/1/versions", "List Document Versions"),
        ("POST", "/documents/1/versions", "Create Document Version"),
        ("GET", "/documents/versions/1", "Get Version by ID"),
        ("PUT", "/documents/versions/1", "Update Version"),
        ("DELETE", "/documents/versions/1", "Delete Version"),
        
        # Document approvals
        ("GET", "/documents/1/approvals", "List Document Approvals"),
        ("POST", "/documents/1/approvals", "Create Document Approval"),
        ("GET", "/documents/approvals/1", "Get Approval by ID"),
        ("PUT", "/documents/approvals/1", "Update Approval"),
        ("DELETE", "/documents/approvals/1", "Delete Approval"),
        
        # Document search
        ("GET", "/documents/search", "Search Documents"),
        ("GET", "/documents/dashboard", "Documents Dashboard"),
        ("GET", "/documents/stats", "Documents Statistics"),
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
                if "categories" in endpoint:
                    data = {"name": "Test Category", "description": "Test category description"}
                elif "versions" in endpoint:
                    data = {"version_number": "1.0", "description": "Test version"}
                elif "approvals" in endpoint:
                    data = {"approver_id": 1, "status": "pending"}
                else:
                    data = {"title": "Test Document", "category_id": 1, "content": "Test content"}
            
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
    validation_count = sum(1 for status, _ in results if status == "VALIDATION_ERROR")
    total_count = len(results)
    
    for status, description in results:
        print(f"{status} {description}: {status}")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"Missing Endpoints: {missing_count}")
    print(f"Validation Errors: {validation_count}")
    
    return success_count, missing_count, validation_count, total_count

def main():
    """Main function"""
    print("🔍 Testing Documents Endpoints")
    print("=" * 50)
    
    success_count, missing_count, validation_count, total_count = test_documents_endpoints()
    
    if success_count == total_count:
        print("\n✅ All documents endpoints are working!")
        print("🎉 Documents module is fully functional!")
    elif missing_count > 0:
        print(f"\n⚠️  Found {missing_count} missing endpoints that need to be implemented.")
        print("This will be addressed in Phase 2.2.")
    elif validation_count > 0:
        print(f"\n⚠️  Found {validation_count} endpoints with validation issues.")
        print("These need schema fixes.")
    else:
        print("\n⚠️  Some endpoints have other issues that need to be fixed.")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
