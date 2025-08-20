#!/usr/bin/env python3
"""
Fix Audit Findings Schema
Add missing risk-related columns to audit_findings table
"""

import sqlite3
import sys

def fix_audit_findings_schema():
    """Add missing columns to audit_findings table"""
    print("🔧 Fixing Audit Findings Schema")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # Get current columns
        cursor.execute("PRAGMA table_info(audit_findings)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current columns: {existing_columns}")
        
        # Define missing columns
        missing_columns = [
            ("risk_register_item_id", "INTEGER"),
            ("risk_assessment_method", "VARCHAR(100)"),
            ("risk_assessment_date", "DATETIME"),
            ("risk_assessor_id", "INTEGER"),
            ("risk_treatment_plan", "TEXT"),
            ("risk_monitoring_frequency", "VARCHAR(100)"),
            ("risk_review_frequency", "VARCHAR(100)"),
            ("risk_control_effectiveness", "INTEGER"),
            ("risk_residual_score", "INTEGER"),
            ("risk_residual_level", "VARCHAR(50)"),
            ("risk_acceptable", "BOOLEAN"),
            ("risk_justification", "TEXT")
        ]
        
        # Add missing columns
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE audit_findings ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_audit_findings_risk_register_item_id ON audit_findings(risk_register_item_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_findings_risk_assessor_id ON audit_findings(risk_assessor_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_findings_risk_assessment_date ON audit_findings(risk_assessment_date)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
        
        conn.commit()
        print("✅ Audit findings schema fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing audit findings schema: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_audit_findings_schema()
    sys.exit(0 if success else 1)
