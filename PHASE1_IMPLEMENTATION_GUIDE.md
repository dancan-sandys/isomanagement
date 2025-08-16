# Phase 1 Implementation Guide - Database Schema Fixes

## 🚨 **CRITICAL: Database Schema Issues**

This guide provides step-by-step instructions to fix the critical database schema issues that are blocking the audit and traceability modules.

---

## 📋 **1.1 Fix Audit Module Database Schema**

### Step 1: Create Database Migration Script

Create a new file: `../backend/fix_audit_schema.py`

```python
#!/usr/bin/env python3
"""
Database migration script to fix audit table schema issues.
This script adds missing columns to the audits table.
"""

import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
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
    """Add missing columns to the audits table"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(audits)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns
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
        
        # Commit changes
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

def verify_migration():
    """Verify that the migration was successful"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        # Check final table structure
        cursor.execute("PRAGMA table_info(audits)")
        columns = cursor.fetchall()
        
        required_columns = ['program_id', 'actual_end_at']
        existing_columns = [col[1] for col in columns]
        
        print("\n📊 Final table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        missing = [col for col in required_columns if col not in existing_columns]
        if missing:
            print(f"❌ Still missing columns: {missing}")
            return False
        else:
            print("✅ All required columns present")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🔧 Starting Audit Schema Migration...")
    print("=" * 50)
    
    # Step 1: Backup database
    backup_file = backup_database()
    if not backup_file:
        return False
    
    # Step 2: Add missing columns
    if not add_missing_columns():
        return False
    
    # Step 3: Verify migration
    if not verify_migration():
        return False
    
    print("\n🎉 Migration completed successfully!")
    print(f"📁 Backup saved as: {backup_file}")
    print("\nNext steps:")
    print("1. Test audit endpoints")
    print("2. Verify data integrity")
    print("3. Run comprehensive testing")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

### Step 2: Run the Migration

```bash
cd ../backend
python fix_audit_schema.py
```

### Step 3: Test Audit Endpoints

Create a test script: `../backend/test_audit_endpoints.py`

```python
#!/usr/bin/env python3
"""
Test script to verify audit endpoints work after schema migration.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_audit_endpoints():
    """Test all audit endpoints"""
    print("🧪 Testing Audit Endpoints...")
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
            print(f"\n🔍 Testing: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("✅", description, "SUCCESS"))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("❌", description, f"Status {response.status_code}"))
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append(("💥", description, str(e)))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for result in results if result[0] == "✅")
    total_count = len(results)
    
    for status, description, details in results:
        print(f"{status} {description}: {details}")
    
    print(f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_audit_endpoints()
    sys.exit(0 if success else 1)
```

---

## 📋 **1.2 Fix Traceability Enum Mapping**

### Step 1: Update Backend Enum Values

Edit the file: `../backend/app/models/traceability.py`

**Find this section:**
```python
class RecallType(str, enum.Enum):
    CLASS_I = "class_i"  # Life-threatening
    CLASS_II = "class_ii"  # Temporary or reversible health effects
    CLASS_III = "class_iii"  # No health effects
```

**Replace with:**
```python
class RecallType(str, enum.Enum):
    CLASS_I = "class_i"  # Life-threatening
    CLASS_II = "class_ii"  # Temporary or reversible health effects
    CLASS_III = "class_iii"  # No health effects
```

**Note:** The enum values are already correct! The issue might be in the database or frontend handling.

### Step 2: Update Database Records (if needed)

Create a script: `../backend/fix_recall_types.py`

```python
#!/usr/bin/env python3
"""
Script to fix any existing recall records with incorrect enum values.
"""

import sqlite3
from datetime import datetime

def fix_recall_types():
    """Fix any existing recall records with incorrect enum values"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        # Check if recalls table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recalls'")
        if not cursor.fetchone():
            print("ℹ️  No recalls table found - nothing to fix")
            return True
        
        # Check current recall types
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        current_types = [row[0] for row in cursor.fetchall()]
        print(f"Current recall types in database: {current_types}")
        
        # Fix any incorrect values
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
    """Main function"""
    print("🔧 Fixing Recall Type Enum Values...")
    print("=" * 40)
    
    success = fix_recall_types()
    
    if success:
        print("\n🎉 Recall type fixes completed!")
        print("\nNext steps:")
        print("1. Test traceability endpoints")
        print("2. Verify recall creation works")
    else:
        print("\n❌ Failed to fix recall types")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

### Step 3: Test Traceability Endpoints

Create a test script: `../backend/test_traceability_endpoints.py`

```python
#!/usr/bin/env python3
"""
Test script to verify traceability endpoints work after enum fixes.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_traceability_endpoints():
    """Test traceability endpoints"""
    print("🧪 Testing Traceability Endpoints...")
    print("=" * 40)
    
    # Test endpoints
    endpoints = [
        ("GET", "/traceability/batches", "List Batches"),
        ("GET", "/traceability/recalls", "List Recalls"),
        ("GET", "/traceability/dashboard", "Traceability Dashboard"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"\n🔍 Testing: {description}")
            print(f"   URL: {method} {url}")
            
            response = requests.request(method, url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS (Status: {response.status_code})")
                results.append(("✅", description, "SUCCESS"))
            else:
                print(f"   ❌ FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(("❌", description, f"Status {response.status_code}"))
                
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append(("💥", description, str(e)))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    success_count = sum(1 for result in results if result[0] == "✅")
    total_count = len(results)
    
    for status, description, details in results:
        print(f"{status} {description}: {details}")
    
    print(f"\n🎯 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_traceability_endpoints()
    sys.exit(0 if success else 1)
```

---

## 🚀 **EXECUTION ORDER**

### Step-by-Step Execution:

1. **Backup Database**
   ```bash
   cd ../backend
   python fix_audit_schema.py
   ```

2. **Fix Recall Types**
   ```bash
   python fix_recall_types.py
   ```

3. **Test Audit Endpoints**
   ```bash
   python test_audit_endpoints.py
   ```

4. **Test Traceability Endpoints**
   ```bash
   python test_traceability_endpoints.py
   ```

5. **Verify Frontend Integration**
   - Open frontend in browser
   - Navigate to Audit pages
   - Navigate to Traceability pages
   - Check browser console for errors

---

## ✅ **VERIFICATION CHECKLIST**

After completing Phase 1, verify:

### Database Schema
- [ ] `audits` table has `program_id` column
- [ ] `audits` table has `actual_end_at` column
- [ ] All recall types use lowercase values (`class_i`, `class_ii`, `class_iii`)

### Backend Endpoints
- [ ] `GET /api/v1/audits/` returns 200 OK
- [ ] `GET /api/v1/audits/stats` returns 200 OK
- [ ] `GET /api/v1/audits/kpis/overview` returns 200 OK
- [ ] `GET /api/v1/traceability/recalls` returns 200 OK

### Frontend Integration
- [ ] Audit pages load without errors
- [ ] Traceability pages load without errors
- [ ] No console errors related to missing columns or enum values

---

## 🎯 **SUCCESS CRITERIA**

Phase 1 is complete when:
- ✅ All database schema issues are resolved
- ✅ All audit endpoints return 200 OK
- ✅ All traceability endpoints return 200 OK
- ✅ Frontend pages load without database-related errors
- ✅ No enum value mismatches in logs

**Next Phase**: Phase 2 - Backend Endpoint Implementation
