#!/usr/bin/env python3
"""
Test script to verify QR code and barcode functionality
"""

import requests
import json
import base64
from datetime import datetime
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if needed
TEST_BATCH_DATA = {
    "batch_type": "final_product",
    "product_name": "Test Cheese Batch",
    "quantity": 100.0,
    "unit": "kg",
    "production_date": datetime.now().isoformat(),
    "expiry_date": (datetime.now().replace(day=datetime.now().day + 30)).isoformat(),
    "lot_number": "TEST-LOT-001",
    "storage_location": "Warehouse A",
    "storage_conditions": "Refrigerated at 4°C"
}

def get_auth_token():
    """Get authentication token"""
    try:
        # Try to login with test credentials
        login_data = {
            "username": "admin@example.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print("Failed to authenticate. Using mock testing...")
            return None
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def test_batch_creation():
    """Test batch creation with QR code and barcode generation"""
    print("Testing batch creation...")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.post(
            f"{BASE_URL}/traceability/batches",
            json=TEST_BATCH_DATA,
            headers=headers
        )
        
        if response.status_code == 200:
            batch_data = response.json()
            print(f"✅ Batch created successfully: {batch_data}")
            return batch_data.get("data", {}).get("id")
        else:
            print(f"❌ Batch creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating batch: {e}")
        return None

def test_qr_code_generation(batch_id):
    """Test QR code generation and retrieval"""
    print(f"Testing QR code generation for batch {batch_id}...")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(
            f"{BASE_URL}/traceability/batches/{batch_id}/qrcode",
            headers=headers
        )
        
        if response.status_code == 200:
            qr_data = response.json()
            print(f"✅ QR code retrieved successfully")
            
            # Check if image data is present
            if qr_data.get("data", {}).get("qr_code_image"):
                print("✅ QR code image data present")
                return True
            else:
                print("⚠️ QR code image data missing")
                return False
        else:
            print(f"❌ QR code retrieval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving QR code: {e}")
        return False

def test_barcode_generation(batch_id):
    """Test barcode generation and retrieval"""
    print(f"Testing barcode generation for batch {batch_id}...")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(
            f"{BASE_URL}/traceability/batches/{batch_id}/barcode",
            headers=headers
        )
        
        if response.status_code == 200:
            barcode_data = response.json()
            print(f"✅ Barcode retrieved successfully")
            
            # Check if image data is present
            if barcode_data.get("data", {}).get("barcode_image"):
                print("✅ Barcode image data present")
                return True
            else:
                print("⚠️ Barcode image data missing")
                return False
        else:
            print(f"❌ Barcode retrieval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving barcode: {e}")
        return False

def test_batch_search():
    """Test batch search functionality"""
    print("Testing batch search...")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        response = requests.get(
            f"{BASE_URL}/traceability/batches",
            params={"search": "TEST"},
            headers=headers
        )
        
        if response.status_code == 200:
            search_data = response.json()
            print(f"✅ Batch search successful")
            return True
        else:
            print(f"❌ Batch search failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error searching batches: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing QR Code and Barcode Functionality")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Server not running or not accessible")
            print("Please start the backend server first:")
            print("cd backend && uvicorn app.main:app --reload")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please ensure the backend server is running at http://localhost:8000")
        sys.exit(1)
    
    # Run tests
    batch_id = test_batch_creation()
    if not batch_id:
        print("❌ Cannot proceed without a valid batch ID")
        sys.exit(1)
    
    qr_success = test_qr_code_generation(batch_id)
    barcode_success = test_barcode_generation(batch_id)
    search_success = test_batch_search()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Batch Creation: {'PASS' if batch_id else 'FAIL'}")
    print(f"✅ QR Code Generation: {'PASS' if qr_success else 'FAIL'}")
    print(f"✅ Barcode Generation: {'PASS' if barcode_success else 'FAIL'}")
    print(f"✅ Batch Search: {'PASS' if search_success else 'FAIL'}")
    
    if all([batch_id, qr_success, barcode_success, search_success]):
        print("\n🎉 All tests passed! QR Code and Barcode functionality is working.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the backend implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())