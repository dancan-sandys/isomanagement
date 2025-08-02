#!/usr/bin/env python3
"""
Test script for Traceability API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_traceability_endpoints():
    """Test the traceability API endpoints"""
    
    print("Testing Traceability API Endpoints")
    print("=" * 50)
    
    # Test 1: Get dashboard data
    print("\n1. Testing Dashboard Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/traceability/dashboard")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Dashboard data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get batches
    print("\n2. Testing Get Batches Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/traceability/batches")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Batches: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Create a batch
    print("\n3. Testing Create Batch Endpoint...")
    try:
        batch_data = {
            "batch_type": "raw_milk",
            "product_name": "Test Raw Milk",
            "quantity": 1000,
            "unit": "liters",
            "production_date": datetime.now().isoformat(),
            "lot_number": "TEST-001",
            "storage_location": "Cold Storage A"
        }
        response = requests.post(f"{API_BASE}/traceability/batches", json=batch_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Created batch: {json.dumps(data, indent=2)}")
            batch_id = data.get("id")
        else:
            print(f"Error: {response.text}")
            batch_id = None
    except Exception as e:
        print(f"Error: {e}")
        batch_id = None
    
    # Test 4: Get recalls
    print("\n4. Testing Get Recalls Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/traceability/recalls")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Recalls: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Create a recall
    print("\n5. Testing Create Recall Endpoint...")
    try:
        recall_data = {
            "recall_type": "class_ii",
            "title": "Test Recall",
            "description": "Test recall for demonstration",
            "reason": "Quality issue detected",
            "total_quantity_affected": 500,
            "issue_discovered_date": datetime.now().isoformat()
        }
        response = requests.post(f"{API_BASE}/traceability/recalls", json=recall_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Created recall: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Get traceability reports
    print("\n6. Testing Get Traceability Reports Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/traceability/trace/reports")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Reports: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 7: Create a traceability report (if we have a batch)
    if batch_id:
        print(f"\n7. Testing Create Traceability Report Endpoint (using batch {batch_id})...")
        try:
            trace_data = {
                "starting_batch_id": batch_id,
                "report_type": "full_trace",
                "trace_depth": 3
            }
            response = requests.post(f"{API_BASE}/traceability/trace", json=trace_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Created trace report: {json.dumps(data, indent=2)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Traceability API Testing Complete")

if __name__ == "__main__":
    test_traceability_endpoints() 