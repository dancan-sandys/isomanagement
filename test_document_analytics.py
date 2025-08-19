#!/usr/bin/env python3
"""
Test script for document analytics endpoints
Tests the new real data document analytics functionality
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def login():
    """Login and get access token"""
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_endpoint(token, endpoint, description):
    """Test a single endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing: {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('message', 'OK')}")
            
            # Print key metrics
            if 'data' in data:
                analytics_data = data['data']
                print(f"   📊 Total Documents: {analytics_data.get('total_documents', 0)}")
                print(f"   📋 Pending Reviews: {analytics_data.get('pending_reviews', 0)}")
                print(f"   ⏰ Expired Documents: {analytics_data.get('expired_documents', 0)}")
                print(f"   ✅ Average Approval Time: {analytics_data.get('average_approval_time', 0)} days")
                
                # Show status breakdown
                status_data = analytics_data.get('documents_by_status', {})
                if status_data:
                    print(f"   📈 Status Breakdown:")
                    for status, count in status_data.items():
                        print(f"      - {status}: {count}")
                
                return True
            else:
                print(f"   ⚠️  No data in response")
                return False
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_export_endpoint(token, format_type):
    """Test export endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing: Document Analytics Export ({format_type.upper()})")
    print(f"   Endpoint: /documents/analytics/export?format={format_type}")
    
    try:
        response = requests.get(
            f"{API_BASE}/documents/analytics/export", 
            headers=headers,
            params={"format": format_type}
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            print(f"   ✅ Success: Export generated")
            print(f"   📄 Content-Type: {content_type}")
            print(f"   📁 Filename: {content_disposition}")
            print(f"   📏 File Size: {len(response.content)} bytes")
            
            return True
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Document Analytics Endpoint Testing")
    print("=" * 50)
    
    # Login
    print("\n🔐 Logging in...")
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print("✅ Login successful")
    
    # Test analytics endpoint
    success_count = 0
    total_tests = 0
    
    # Test main analytics endpoint
    total_tests += 1
    if test_endpoint(token, "/documents/analytics", "Document Analytics"):
        success_count += 1
    
    # Test export endpoints
    for format_type in ["excel", "csv"]:
        total_tests += 1
        if test_export_endpoint(token, format_type):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! Document analytics is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - success_count} test(s) failed. Check the implementation.")

if __name__ == "__main__":
    main()
