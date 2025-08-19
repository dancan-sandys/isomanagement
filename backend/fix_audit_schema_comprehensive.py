#!/usr/bin/env python3
"""
Comprehensive Audit Schema Fix Script
Fixes all missing columns in the audits table and related schema issues
"""

import sqlite3
import os
from datetime import datetime

def fix_audit_schema_comprehensive():
    """Fix all missing columns in the audits table and related schema issues"""
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Starting comprehensive audit schema fix...")
        
        # Get current columns in audits table
        cursor.execute("PRAGMA table_info(audits)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current columns in audits table: {existing_columns}")
        
        # Define missing columns to add
        missing_columns = [
            ("risk_monitoring_frequency", "VARCHAR(100)"),
            ("risk_review_frequency", "VARCHAR(100)"),
            ("risk_control_effectiveness", "INTEGER"),
            ("risk_residual_score", "INTEGER"),
            ("risk_residual_level", "VARCHAR(50)")
        ]
        
        # Add missing columns
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                print(f"➕ Adding column: {column_name} ({column_type})")
                cursor.execute(f"ALTER TABLE audits ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added {column_name} column")
            else:
                print(f"✅ Column {column_name} already exists")
        
        # Check PRP risk assessments table
        print("\n🔍 Checking PRP risk assessments table...")
        cursor.execute("PRAGMA table_info(prp_risk_assessments)")
        prp_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current columns in prp_risk_assessments table: {prp_columns}")
        
        # Add missing column to prp_risk_assessments if needed
        if "escalated_to_risk_register" not in prp_columns:
            print("➕ Adding column: escalated_to_risk_register (BOOLEAN)")
            cursor.execute("ALTER TABLE prp_risk_assessments ADD COLUMN escalated_to_risk_register BOOLEAN DEFAULT FALSE")
            print("✅ Added escalated_to_risk_register column")
        else:
            print("✅ Column escalated_to_risk_register already exists")
        
        # Create indexes for performance
        print("\n🔍 Creating performance indexes...")
        indexes_to_create = [
            ("idx_audits_program_id", "audits(program_id)"),
            ("idx_audits_status", "audits(status)"),
            ("idx_audits_audit_type", "audits(audit_type)"),
            ("idx_audits_created_by", "audits(created_by)"),
            ("idx_audits_start_date", "audits(start_date)"),
            ("idx_audits_end_date", "audits(end_date)"),
            ("idx_audits_risk_register_item_id", "audits(risk_register_item_id)")
        ]
        
        for index_name, index_def in indexes_to_create:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
                print(f"✅ Created index: {index_name}")
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"✅ Index {index_name} already exists")
                else:
                    print(f"⚠️ Could not create index {index_name}: {e}")
        
        # Verify the fixes
        print("\n🔍 Verifying fixes...")
        cursor.execute("PRAGMA table_info(audits)")
        final_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Final columns in audits table: {final_columns}")
        
        # Test a simple query
        try:
            cursor.execute("SELECT COUNT(*) FROM audits")
            count = cursor.fetchone()[0]
            print(f"✅ Audits table is accessible, contains {count} records")
        except Exception as e:
            print(f"❌ Error accessing audits table: {e}")
            return False
        
        # Commit changes
        conn.commit()
        print("\n🎉 Comprehensive audit schema fix completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing audit schema: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = fix_audit_schema_comprehensive()
    
    if success:
        print("\n🎉 Audit schema fix completed successfully!")
    else:
        print("\n💥 Audit schema fix failed!")

