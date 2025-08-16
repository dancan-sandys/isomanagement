#!/usr/bin/env python3
"""
Test script to verify audit endpoints work after schema migration.
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_audit_endpoints():
    """Test all audit endpoints"""
    print("Testing Audit Endpoints...")
    print("=" * 40)
    
    # Test endpoints
    endpoints = [
        ("GET", "/audits/", "List Audits"),
        ("GET", "/audits/stats", "Audit Statistics"),
        ("GET", "/audits/kpis/overview", "Audit KPIs"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nTesting: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, timeout=10)
            
            if response.status_code == 200:
                print(f"   SUCCESS (Status: {response.status_code})")
                results.append(("SUCCESS", description, "SUCCESS"))
            else:
                print(f"   FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("FAILED", description, f"Status {response.status_code}"))
                
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append(("ERROR", description, str(e)))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for result in results if result[0] == "SUCCESS")
    total_count = len(results)
    
    for status, description, details in results:
        print(f"{status} {description}: {details}")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_audit_endpoints()
    sys.exit(0 if success else 1)
