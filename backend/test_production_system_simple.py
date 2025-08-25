# -*- coding: utf-8 -*-
"""
Simplified Test Script for Production System
Tests the API endpoints with minimal data
"""

import requests
import json
from datetime import datetime

def test_production_api():
    """Test the production API endpoints"""
    
    base_url = "http://127.0.0.1:8000/api/v1"
    
    print("🧪 Testing Production API Endpoints...")
    
    try:
        # Test 1: Get enhanced analytics
        print("\n1. Testing Enhanced Analytics...")
        response = requests.get(f"{base_url}/production/analytics/enhanced")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics retrieved successfully")
            print(f"   - Total processes: {data.get('total_processes', 0)}")
            print(f"   - Active processes: {data.get('active_processes', 0)}")
            print(f"   - Total deviations: {data.get('total_deviations', 0)}")
            print(f"   - Total alerts: {data.get('total_alerts', 0)}")
        else:
            print(f"❌ Analytics failed: {response.status_code} - {response.text}")
        
        # Test 2: Get process templates
        print("\n2. Testing Process Templates...")
        response = requests.get(f"{base_url}/production/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Templates retrieved successfully: {len(templates)} templates")
            for template in templates:
                print(f"   - {template.get('template_name')} ({template.get('product_type')})")
        else:
            print(f"❌ Templates failed: {response.status_code} - {response.text}")
        
        # Test 3: Get basic analytics
        print("\n3. Testing Basic Analytics...")
        response = requests.get(f"{base_url}/production/analytics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic analytics retrieved successfully")
            print(f"   - Total records: {data.get('total_records', 0)}")
            print(f"   - Average overrun: {data.get('avg_overrun_percent', 0)}%")
        else:
            print(f"❌ Basic analytics failed: {response.status_code} - {response.text}")
        
        print("\n🎉 Production API testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🌐 Testing Frontend Integration...")
    
    try:
        # Test if frontend is accessible
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running. Make sure the React app is started.")
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")

if __name__ == "__main__":
    test_production_api()
    test_frontend_integration()
