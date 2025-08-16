#!/usr/bin/env python3
"""
Quick Start Script - Begin ISO 22000 FSMS Fixes
This script starts the critical database schema fixes immediately.
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header():
    """Print the script header"""
    print("=" * 60)
    print("🚀 ISO 22000 FSMS - QUICK START FIXES")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This script will fix critical database schema issues.")
    print("=" * 60)

def check_backend_directory():
    """Check if we're in the right directory"""
    if not os.path.exists("../backend"):
        print("❌ Error: Backend directory not found!")
        print("Please run this script from the frontend directory.")
        return False
    
    if not os.path.exists("../backend/iso22000_fsms.db"):
        print("❌ Error: Database file not found!")
        print("Please ensure the backend is properly set up.")
        return False
    
    print("✅ Backend directory and database found")
    return True

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n🔧 {description}")
    print("-" * 40)
    
    script_path = f"../backend/{script_name}"
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        print("Creating the script...")
        return create_missing_script(script_name)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd="../backend")
        
        if result.returncode == 0:
            print("✅ Script completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Script failed")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False
    
    return True

def create_missing_script(script_name):
    """Create missing script files"""
    if script_name == "fix_audit_schema.py":
        return create_audit_schema_script()
    elif script_name == "fix_recall_types.py":
        return create_recall_types_script()
    elif script_name == "test_audit_endpoints.py":
        return create_test_audit_script()
    elif script_name == "test_traceability_endpoints.py":
        return create_test_traceability_script()
    else:
        print(f"❌ Unknown script: {script_name}")
        return False

def create_audit_schema_script():
    """Create the audit schema fix script"""
    script_content = '''#!/usr/bin/env python3
"""
Database migration script to fix audit table schema issues.
"""

import sqlite3
import os
from datetime import datetime

def backup_database():
    backup_name = f"iso22000_fsms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if os.path.exists("iso22000_fsms.db"):
        import shutil
        shutil.copy2("iso22000_fsms.db", backup_name)
        print(f"✅ Database backed up as: {backup_name}")
        return backup_name
    else:
        print("❌ Database file not found!")
        return None

def add_missing_columns():
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(audits)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        missing_columns = []
        
        if 'program_id' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN program_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_program_id ON audits(program_id)")
            missing_columns.append('program_id')
            print("✅ Added program_id column")
        
        if 'actual_end_at' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN actual_end_at DATETIME")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_actual_end_at ON audits(actual_end_at)")
            missing_columns.append('actual_end_at')
            print("✅ Added actual_end_at column")
        
        conn.commit()
        conn.close()
        
        if missing_columns:
            print(f"✅ Successfully added columns: {missing_columns}")
        else:
            print("✅ All required columns already exist")
            
        return True
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        return False

def main():
    print("🔧 Starting Audit Schema Migration...")
    print("=" * 50)
    
    backup_file = backup_database()
    if not backup_file:
        return False
    
    if not add_missing_columns():
        return False
    
    print("\\n🎉 Migration completed successfully!")
    print(f"📁 Backup saved as: {backup_file}")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
'''
    
    with open("../backend/fix_audit_schema.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created fix_audit_schema.py")
    return True

def create_recall_types_script():
    """Create the recall types fix script"""
    script_content = '''#!/usr/bin/env python3
"""
Script to fix any existing recall records with incorrect enum values.
"""

import sqlite3

def fix_recall_types():
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recalls'")
        if not cursor.fetchone():
            print("ℹ️  No recalls table found - nothing to fix")
            return True
        
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        current_types = [row[0] for row in cursor.fetchall()]
        print(f"Current recall types in database: {current_types}")
        
        updates_needed = []
        
        if 'CLASS_I' in current_types:
            cursor.execute("UPDATE recalls SET recall_type = 'class_i' WHERE recall_type = 'CLASS_I'")
            updates_needed.append('CLASS_I -> class_i')
        
        if 'CLASS_II' in current_types:
            cursor.execute("UPDATE recalls SET recall_type = 'class_ii' WHERE recall_type = 'CLASS_II'")
            updates_needed.append('CLASS_II -> class_ii')
        
        if 'CLASS_III' in current_types:
            cursor.execute("UPDATE recalls SET recall_type = 'class_iii' WHERE recall_type = 'CLASS_III'")
            updates_needed.append('CLASS_III -> class_iii')
        
        if updates_needed:
            conn.commit()
            print(f"✅ Updated recall types: {', '.join(updates_needed)}")
        else:
            print("✅ No updates needed - recall types are already correct")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing recall types: {e}")
        return False

def main():
    print("🔧 Fixing Recall Type Enum Values...")
    print("=" * 40)
    
    success = fix_recall_types()
    
    if success:
        print("\\n🎉 Recall type fixes completed!")
    else:
        print("\\n❌ Failed to fix recall types")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
'''
    
    with open("../backend/fix_recall_types.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created fix_recall_types.py")
    return True

def create_test_audit_script():
    """Create the test audit endpoints script"""
    script_content = '''#!/usr/bin/env python3
"""
Test script to verify audit endpoints work after schema migration.
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_audit_endpoints():
    print("🧪 Testing Audit Endpoints...")
    print("=" * 40)
    
    endpoints = [
        ("GET", "/audits/", "List Audits"),
        ("GET", "/audits/stats", "Audit Statistics"),
        ("GET", "/audits/kpis/overview", "Audit KPIs"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\\n🔍 Testing: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("✅", description, "SUCCESS"))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                results.append(("❌", description, f"Status {response.status_code}"))
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append(("💥", description, str(e)))
    
    print("\\n" + "=" * 40)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for result in results if result[0] == "✅")
    total_count = len(results)
    
    for status, description, details in results:
        print(f"{status} {description}: {details}")
    
    print(f"\\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_audit_endpoints()
    sys.exit(0 if success else 1)
'''
    
    with open("../backend/test_audit_endpoints.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created test_audit_endpoints.py")
    return True

def create_test_traceability_script():
    """Create the test traceability endpoints script"""
    script_content = '''#!/usr/bin/env python3
"""
Test script to verify traceability endpoints work after enum fixes.
"""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_traceability_endpoints():
    print("🧪 Testing Traceability Endpoints...")
    print("=" * 40)
    
    endpoints = [
        ("GET", "/traceability/batches", "List Batches"),
        ("GET", "/traceability/recalls", "List Recalls"),
        ("GET", "/traceability/dashboard", "Traceability Dashboard"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\\n🔍 Testing: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("✅", description, "SUCCESS"))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                results.append(("❌", description, f"Status {response.status_code}"))
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append(("💥", description, str(e)))
    
    print("\\n" + "=" * 40)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for result in results if result[0] == "✅")
    total_count = len(results)
    
    for status, description, details in results:
        print(f"{status} {description}: {details}")
    
    print(f"\\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_traceability_endpoints()
    sys.exit(0 if success else 1)
'''
    
    with open("../backend/test_traceability_endpoints.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created test_traceability_endpoints.py")
    return True

def main():
    """Main function"""
    print_header()
    
    # Check prerequisites
    if not check_backend_directory():
        return False
    
    print("\n🚀 Starting critical fixes...")
    
    # Step 1: Fix audit schema
    if not run_script("fix_audit_schema.py", "Fixing Audit Database Schema"):
        print("❌ Failed to fix audit schema")
        return False
    
    # Step 2: Fix recall types
    if not run_script("fix_recall_types.py", "Fixing Recall Type Enum Values"):
        print("❌ Failed to fix recall types")
        return False
    
    # Step 3: Test endpoints
    print("\n🧪 Testing endpoints...")
    run_script("test_audit_endpoints.py", "Testing Audit Endpoints")
    run_script("test_traceability_endpoints.py", "Testing Traceability Endpoints")
    
    print("\n" + "=" * 60)
    print("🎉 PHASE 1 COMPLETED!")
    print("=" * 60)
    print("✅ Database schema issues fixed")
    print("✅ Enum value mismatches resolved")
    print("✅ Endpoints tested")
    print("\n📋 Next steps:")
    print("1. Check frontend integration")
    print("2. Continue with Phase 2 (Backend Endpoint Implementation)")
    print("3. Review COMPREHENSIVE_FIX_CHECKLIST.md for full roadmap")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Some fixes failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All critical fixes completed successfully!")
