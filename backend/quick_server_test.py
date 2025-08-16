#!/usr/bin/env python3
"""
Quick server test to check if the backend is responding properly.
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_server_health():
    """Test if the server is responding"""
    print("Testing Server Health...")
    print("=" * 40)
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/auth/login", timeout=5)
        print(f"✅ Server is responding (Status: {response.status_code})")
        return True
    except requests.exceptions.Timeout:
        print("❌ Server timeout - server might be overloaded")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Server connection error - server might be down")
        return False
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        return False

def test_traceability_endpoints():
    """Test traceability endpoints with shorter timeout"""
    print("\nTesting Traceability Endpoints (5s timeout)...")
    print("=" * 40)
    
    endpoints = [
        ("GET", "/traceability/batches", "List Batches"),
        ("GET", "/traceability/recalls", "List Recalls"),
        ("GET", "/traceability/dashboard", "Dashboard"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nTesting: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("SUCCESS", description))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("FAILED", description))
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT (5s)")
            results.append(("TIMEOUT", description))
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(("ERROR", description))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for status, _ in results if status == "SUCCESS")
    total_count = len(results)
    
    for status, description in results:
        print(f"{status} {description}: {status}")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

def main():
    """Main function"""
    print("🔍 Quick Server Health Check")
    print("=" * 50)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server health check failed. Please restart the backend server.")
        return False
    
    # Test traceability endpoints
    success = test_traceability_endpoints()
    
    if success:
        print("\n✅ All tests passed! Server is working properly.")
    else:
        print("\n⚠️  Some tests failed. Check server performance.")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
