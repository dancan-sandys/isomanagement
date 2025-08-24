#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json={})
        
        success = response.status_code == expected_status
        print(f"{'✅' if success else '❌'} {method} {endpoint} - {response.status_code}")
        return success
    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR: {e}")
        return False

def main():
    print("🚀 Testing Key Endpoints...")
    
    endpoints = [
        # Core endpoints
        ("/health", "GET", 200),
        ("/", "GET", 200),
        ("/debug", "GET", 200),
        
        # API endpoints
        ("/api/v1/suppliers", "GET", 200),
        ("/api/v1/users", "GET", 200),
        ("/api/v1/documents", "GET", 200),
        ("/api/v1/haccp/products", "GET", 200),
        ("/api/v1/prp/programs", "GET", 200),
        ("/api/v1/risk/register", "GET", 200),
        ("/api/v1/audits", "GET", 200),
        ("/api/v1/equipment", "GET", 200),
        ("/api/v1/production/processes", "GET", 200),
        ("/api/v1/complaints", "GET", 200),
        ("/api/v1/dashboard", "GET", 200),
        ("/api/v1/settings", "GET", 200),
        ("/api/v1/notifications", "GET", 200),
        ("/api/v1/traceability/batches", "GET", 200),
        ("/api/v1/training/programs", "GET", 200),
        ("/api/v1/management-reviews", "GET", 200),
        ("/api/v1/objectives", "GET", 200),
        ("/api/v1/analytics/reports", "GET", 200),
        ("/api/v1/actions-log", "GET", 200),
        ("/api/v1/rbac/roles", "GET", 200),
        ("/api/v1/search", "GET", 200),
        ("/api/v1/profile", "GET", 200),
        ("/api/v1/nonconformance", "GET", 200),
        ("/api/v1/allergen-label", "GET", 200),
        
        # Auth endpoints (should return 422 for missing data)
        ("/api/v1/auth/login", "POST", 422),
        ("/api/v1/auth/signup", "POST", 422),
    ]
    
    successful = 0
    total = len(endpoints)
    
    for endpoint, method, expected_status in endpoints:
        if test_endpoint(endpoint, method, expected_status):
            successful += 1
    
    print(f"\n📊 Results: {successful}/{total} endpoints working ({successful/total*100:.1f}%)")

if __name__ == "__main__":
    main()


