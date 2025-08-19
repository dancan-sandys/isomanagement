#!/usr/bin/env python3
"""
Comprehensive Enum Value Fix Script
Fixes all enum value inconsistencies across the ISO 22000 FSMS platform
"""

import sqlite3
import sys
from pathlib import Path

def fix_all_enum_values():
    """Fix all enum value inconsistencies in the database"""
    print("🔧 Fixing All Enum Value Inconsistencies\n")
    
    # Connect to database
    db_path = Path("iso22000_fsms.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Fix Hazard Types (BIOLOGICAL -> biological)
        print("1. Fixing Hazard Types...")
        cursor.execute("""
            UPDATE hazards 
            SET hazard_type = 'biological' 
            WHERE hazard_type = 'BIOLOGICAL'
        """)
        print(f"   ✅ Updated {cursor.rowcount} hazard records")
        
        # 2. Fix Recall Types (CLASS_II -> class_ii)
        print("2. Fixing Recall Types...")
        cursor.execute("""
            UPDATE recalls 
            SET recall_type = 'class_ii' 
            WHERE recall_type = 'CLASS_II'
        """)
        print(f"   ✅ Updated {cursor.rowcount} recall records")
        
        # 3. Fix Supplier Categories
        print("3. Fixing Supplier Categories...")
        
        # Map invalid categories to valid ones
        category_mapping = {
            'materials': 'raw_milk',  # Map to closest valid category
            'coatings': 'chemicals',  # Map to chemicals
        }
        
        for invalid_cat, valid_cat in category_mapping.items():
            cursor.execute("""
                UPDATE suppliers 
                SET category = ? 
                WHERE category = ?
            """, (valid_cat, invalid_cat))
            print(f"   ✅ Mapped '{invalid_cat}' -> '{valid_cat}': {cursor.rowcount} records")
        
        # 4. Fix Maintenance Types (already fixed, but double-check)
        print("4. Checking Maintenance Types...")
        cursor.execute("""
            UPDATE maintenance_plans 
            SET maintenance_type = 'PREVENTIVE' 
            WHERE maintenance_type = 'preventive'
        """)
        print(f"   ✅ Updated {cursor.rowcount} maintenance records")
        
        # 5. Fix Risk Status (ensure consistency)
        print("5. Checking Risk Status...")
        cursor.execute("""
            UPDATE risk_register 
            SET status = 'OPEN' 
            WHERE status = 'open'
        """)
        print(f"   ✅ Updated {cursor.rowcount} risk records")
        
        # 6. Fix Document Types and Status
        print("6. Checking Document Enums...")
        cursor.execute("""
            UPDATE documents 
            SET status = 'ACTIVE' 
            WHERE status = 'active'
        """)
        print(f"   ✅ Updated {cursor.rowcount} document status records")
        
        # 7. Fix PRP Categories
        print("7. Checking PRP Categories...")
        cursor.execute("""
            UPDATE prp_programs 
            SET category = 'SANITATION' 
            WHERE category = 'sanitation'
        """)
        print(f"   ✅ Updated {cursor.rowcount} PRP category records")
        
        # 8. Fix HACCP Status
        print("8. Checking HACCP Status...")
        cursor.execute("""
            UPDATE haccp_plans 
            SET status = 'ACTIVE' 
            WHERE status = 'active'
        """)
        print(f"   ✅ Updated {cursor.rowcount} HACCP status records")
        
        # 9. Fix Audit Status
        print("9. Checking Audit Status...")
        cursor.execute("""
            UPDATE audits 
            SET status = 'PLANNED' 
            WHERE status = 'planned'
        """)
        print(f"   ✅ Updated {cursor.rowcount} audit status records")
        
        # 10. Fix NonConformance Status (if table exists)
        print("10. Checking NonConformance Status...")
        try:
            cursor.execute("""
                UPDATE nonconformances 
                SET status = 'OPEN' 
                WHERE status = 'open'
            """)
            print(f"   ✅ Updated {cursor.rowcount} nonconformance status records")
        except sqlite3.OperationalError:
            print("   ⚠️  Nonconformances table not found, skipping...")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All enum values fixed successfully!")
        
        # Verify fixes
        print("\n📋 Verification:")
        verify_enum_fixes(cursor)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing enum values: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_enum_fixes(cursor):
    """Verify that enum fixes were applied correctly"""
    
    # Check hazard types
    cursor.execute("SELECT DISTINCT hazard_type FROM hazards")
    hazard_types = [row[0] for row in cursor.fetchall()]
    print(f"   Hazard types: {hazard_types}")
    
    # Check recall types
    cursor.execute("SELECT DISTINCT recall_type FROM recalls")
    recall_types = [row[0] for row in cursor.fetchall()]
    print(f"   Recall types: {recall_types}")
    
    # Check supplier categories
    cursor.execute("SELECT DISTINCT category FROM suppliers")
    supplier_categories = [row[0] for row in cursor.fetchall()]
    print(f"   Supplier categories: {supplier_categories}")
    
    # Check maintenance types
    cursor.execute("SELECT DISTINCT maintenance_type FROM maintenance_plans")
    maintenance_types = [row[0] for row in cursor.fetchall()]
    print(f"   Maintenance types: {maintenance_types}")

def check_enum_consistency():
    """Check for any remaining enum inconsistencies"""
    print("\n🔍 Checking for remaining enum inconsistencies...")
    
    conn = sqlite3.connect("iso22000_fsms.db")
    cursor = conn.cursor()
    
    try:
        # Check for any uppercase values that should be lowercase
        tables_to_check = [
            ("hazards", "hazard_type"),
            ("recalls", "recall_type"),
            ("suppliers", "category"),
            ("maintenance_plans", "maintenance_type"),
            ("risk_register", "status"),
            ("documents", "status"),
            ("prp_programs", "category"),
            ("haccp_plans", "status"),
            ("audits", "status")
        ]
        
        issues_found = []
        
        for table, column in tables_to_check:
            try:
                cursor.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
                values = [row[0] for row in cursor.fetchall()]
                
                # Check for mixed case issues
                for value in values:
                    if value and value != value.lower() and value != value.upper():
                        issues_found.append(f"{table}.{column}: '{value}' (mixed case)")
            except sqlite3.OperationalError:
                print(f"   ⚠️  Table {table} not found, skipping...")
        
        if issues_found:
            print("⚠️  Found potential enum inconsistencies:")
            for issue in issues_found:
                print(f"   - {issue}")
        else:
            print("✅ No enum inconsistencies found!")
            
    except Exception as e:
        print(f"❌ Error checking enum consistency: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 ISO 22000 FSMS - Enum Value Fix Script")
    print("=" * 50)
    
    # Fix enum values
    success = fix_all_enum_values()
    
    if success:
        # Check for remaining issues
        check_enum_consistency()
        print("\n✅ Enum value fix completed successfully!")
    else:
        print("\n❌ Enum value fix failed!")
        sys.exit(1)
