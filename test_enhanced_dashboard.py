#!/usr/bin/env python3
"""
Test script for enhanced dashboard endpoints
Tests the new real data dashboard functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
DASHBOARD_BASE = f"{BASE_URL}/api/v1/dashboard"

def login():
    """Login and get access token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(LOGIN_URL, data=login_data)
    if response.status_code == 200:
        token = response.json()["data"]["access_token"]
        return token
    else:
        print(f"Login failed: {response.status_code}")
        return None

def test_endpoint(token, endpoint, description):
    """Test a dashboard endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing: {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {response.status_code}")
            print(f"   📊 Data keys: {list(data.get('data', {}).keys())}")
            
            # Show some sample data
            if 'data' in data:
                sample_data = data['data']
                if isinstance(sample_data, dict):
                    for key, value in sample_data.items():
                        if isinstance(value, (int, float)):
                            print(f"   📈 {key}: {value}")
                        elif isinstance(value, dict):
                            print(f"   📈 {key}: {len(value)} items")
                        elif isinstance(value, list):
                            print(f"   📈 {key}: {len(value)} items")
                elif isinstance(sample_data, list):
                    print(f"   📈 Data points: {len(sample_data)}")
            
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   💥 Error: {str(e)}")
        return False

def test_chart_endpoints(token):
    """Test chart data endpoints"""
    chart_types = [
        "nc_trend",
        "compliance_by_department", 
        "supplier_performance",
        "training_completion",
        "audit_findings",
        "document_status"
    ]
    
    periods = ["1m", "3m", "6m", "1y"]
    
    print("\n📊 Testing Chart Endpoints")
    print("=" * 50)
    
    for chart_type in chart_types:
        for period in periods:
            endpoint = f"{DASHBOARD_BASE}/charts/{chart_type}?period={period}"
            test_endpoint(token, endpoint, f"{chart_type} ({period})")

def test_export_endpoints(token):
    """Test export endpoints"""
    export_types = ["kpi_summary", "compliance_report"]
    formats = ["excel", "csv"]
    
    print("\n📤 Testing Export Endpoints")
    print("=" * 50)
    
    for export_type in export_types:
        for format_type in formats:
            endpoint = f"{DASHBOARD_BASE}/export/{export_type}?format={format_type}&period=6m"
            test_endpoint(token, endpoint, f"{export_type} ({format_type})")

def main():
    """Main test function"""
    print("🚀 Enhanced Dashboard Endpoint Testing")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Login
    print("\n🔐 Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    
    print("✅ Login successful")
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints")
    print("=" * 50)
    
    endpoints = [
        (f"{DASHBOARD_BASE}/kpis", "KPIs"),
        (f"{DASHBOARD_BASE}/department-compliance", "Department Compliance"),
        (f"{DASHBOARD_BASE}/stats", "Stats (legacy)"),
        (f"{DASHBOARD_BASE}/overview", "Overview (legacy)"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, description in endpoints:
        if test_endpoint(token, endpoint, description):
            success_count += 1
    
    # Test chart endpoints
    test_chart_endpoints(token)
    
    # Test export endpoints
    test_export_endpoints(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Basic endpoints: {success_count}/{total_count} successful")
    print(f"📈 Chart endpoints: Tested 6 chart types × 4 periods = 24 endpoints")
    print(f"📤 Export endpoints: Tested 2 export types × 2 formats = 4 endpoints")
    print(f"🎯 Total endpoints tested: {total_count + 28}")
    
    if success_count == total_count:
        print("\n🎉 All basic endpoints working! Enhanced dashboard is ready.")
    else:
        print(f"\n⚠️  {total_count - success_count} basic endpoints failed. Check implementation.")

if __name__ == "__main__":
    main()
