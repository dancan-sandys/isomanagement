#!/usr/bin/env python3
"""
Comprehensive Traceability Enum Fixes
Fix all enum value issues in the traceability module
"""

import sqlite3
import sys
import requests
import json

def fix_traceability_enums():
    """Fix all enum values in traceability module"""
    print("🔧 Fixing Traceability Enum Values")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # 1. Fix batch_type enum values
        print("\n📋 Fixing batch_type enum values...")
        cursor.execute("SELECT DISTINCT batch_type FROM batches")
        batch_types = [row[0] for row in cursor.fetchall()]
        print(f"Current batch_type values: {batch_types}")
        
        # Update to lowercase values
        batch_type_fixes = {
            'RAW_MILK': 'raw_milk',
            'ADDITIVE': 'additive',
            'CULTURE': 'culture',
            'PACKAGING': 'packaging',
            'FINAL_PRODUCT': 'final_product',
            'INTERMEDIATE': 'intermediate'
        }
        
        for old_value, new_value in batch_type_fixes.items():
            cursor.execute(
                "UPDATE batches SET batch_type = ? WHERE batch_type = ?",
                (new_value, old_value)
            )
            if cursor.rowcount > 0:
                print(f"✅ Updated {cursor.rowcount} batch_type records: '{old_value}' → '{new_value}'")
        
        # 2. Fix status enum values
        print("\n📋 Fixing status enum values...")
        cursor.execute("SELECT DISTINCT status FROM batches")
        statuses = [row[0] for row in cursor.fetchall()]
        print(f"Current status values: {statuses}")
        
        # Update to lowercase values
        status_fixes = {
            'IN_PRODUCTION': 'in_production',
            'COMPLETED': 'completed',
            'QUARANTINED': 'quarantined',
            'RELEASED': 'released',
            'RECALLED': 'recalled',
            'DISPOSED': 'disposed'
        }
        
        for old_value, new_value in status_fixes.items():
            cursor.execute(
                "UPDATE batches SET status = ? WHERE status = ?",
                (new_value, old_value)
            )
            if cursor.rowcount > 0:
                print(f"✅ Updated {cursor.rowcount} status records: '{old_value}' → '{new_value}'")
        
        # 3. Fix recall_type enum values (if any)
        print("\n📋 Fixing recall_type enum values...")
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        recall_types = [row[0] for row in cursor.fetchall()]
        print(f"Current recall_type values: {recall_types}")
        
        # Update to uppercase values (as per previous fixes)
        recall_type_fixes = {
            'class_i': 'CLASS_I',
            'class_ii': 'CLASS_II',
            'class_iii': 'CLASS_III'
        }
        
        for old_value, new_value in recall_type_fixes.items():
            cursor.execute(
                "UPDATE recalls SET recall_type = ? WHERE recall_type = ?",
                (new_value, old_value)
            )
            if cursor.rowcount > 0:
                print(f"✅ Updated {cursor.rowcount} recall_type records: '{old_value}' → '{new_value}'")
        
        # 4. Fix recall status enum values
        print("\n📋 Fixing recall status enum values...")
        cursor.execute("SELECT DISTINCT status FROM recalls")
        recall_statuses = [row[0] for row in cursor.fetchall()]
        print(f"Current recall status values: {recall_statuses}")
        
        # Update to lowercase values
        recall_status_fixes = {
            'DRAFT': 'draft',
            'PENDING': 'pending',
            'APPROVED': 'approved',
            'REJECTED': 'rejected',
            'IN_PROGRESS': 'in_progress',
            'COMPLETED': 'completed',
            'CANCELLED': 'cancelled'
        }
        
        for old_value, new_value in recall_status_fixes.items():
            cursor.execute(
                "UPDATE recalls SET status = ? WHERE status = ?",
                (new_value, old_value)
            )
            if cursor.rowcount > 0:
                print(f"✅ Updated {cursor.rowcount} recall status records: '{old_value}' → '{new_value}'")
        
        conn.commit()
        print("\n✅ All traceability enum fixes completed successfully!")
        
        # 5. Verify all fixes
        print("\n📋 Verifying fixes...")
        
        # Check batch types
        cursor.execute("SELECT DISTINCT batch_type FROM batches")
        final_batch_types = [row[0] for row in cursor.fetchall()]
        valid_batch_types = ['raw_milk', 'additive', 'culture', 'packaging', 'final_product', 'intermediate']
        invalid_batch_types = [v for v in final_batch_types if v not in valid_batch_types]
        
        if invalid_batch_types:
            print(f"⚠️  Invalid batch_type values found: {invalid_batch_types}")
        else:
            print("✅ All batch_type values are valid")
        
        # Check batch statuses
        cursor.execute("SELECT DISTINCT status FROM batches")
        final_statuses = [row[0] for row in cursor.fetchall()]
        valid_statuses = ['in_production', 'completed', 'quarantined', 'released', 'recalled', 'disposed']
        invalid_statuses = [v for v in final_statuses if v not in valid_statuses]
        
        if invalid_statuses:
            print(f"⚠️  Invalid status values found: {invalid_statuses}")
        else:
            print("✅ All status values are valid")
        
        # Check recall types
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        final_recall_types = [row[0] for row in cursor.fetchall()]
        valid_recall_types = ['CLASS_I', 'CLASS_II', 'CLASS_III']
        invalid_recall_types = [v for v in final_recall_types if v not in valid_recall_types]
        
        if invalid_recall_types:
            print(f"⚠️  Invalid recall_type values found: {invalid_recall_types}")
        else:
            print("✅ All recall_type values are valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing traceability enums: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_traceability_endpoints():
    """Test traceability endpoints after fixes"""
    print("\n🧪 Testing Traceability Endpoints")
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test endpoints
    test_endpoints = [
        "/traceability/batches",
        "/traceability/recalls",
        "/traceability/batches/search/enhanced",
        "/traceability/reports"
    ]
    
    for endpoint in test_endpoints:
        try:
            if endpoint == "/traceability/reports":
                # POST request for reports
                response = requests.post(f"{base_url}{endpoint}", json={
                    "report_type": "batch_traceability",
                    "batch_id": 1,
                    "include_suppliers": True,
                    "include_customers": True
                })
            elif endpoint == "/traceability/batches/search/enhanced":
                # POST request for enhanced search
                response = requests.post(f"{base_url}{endpoint}", json={
                    "batch_type": "raw_milk",
                    "status": "in_production",
                    "date_from": "2024-01-01",
                    "date_to": "2024-12-31"
                })
            else:
                # GET request
                response = requests.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            elif response.status_code == 422:
                print(f"⚠️  {endpoint}: Validation Error (422)")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Connection Error - {str(e)}")

if __name__ == "__main__":
    print("🔧 Comprehensive Traceability Enum Fixes")
    print("=" * 50)
    
    # Fix enums
    success = fix_traceability_enums()
    
    if success:
        # Test endpoints
        test_traceability_endpoints()
        print("\n✅ Traceability enum fixes and testing completed!")
    else:
        print("\n❌ Failed to fix traceability enums")
    
    sys.exit(0 if success else 1)
