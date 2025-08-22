#!/usr/bin/env python3
"""
Fix Audit Database Schema
This script adds missing columns to the audits table and ensures the database schema matches the model definitions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.core.database import SessionLocal, engine

def check_audit_table_schema():
    """Check the current audit table schema"""
    print("🔍 Checking audit table schema...")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('audits')
    
    print("Current audit table columns:")
    for column in columns:
        print(f"  - {column['name']}: {column['type']}")
    
    return [col['name'] for col in columns]

def add_missing_audit_columns():
    """Add missing columns to the audits table"""
    print("🔧 Adding missing audit columns...")
    
    db = SessionLocal()
    try:
        # Check current columns
        current_columns = check_audit_table_schema()
        
        # Define missing columns that should be added
        missing_columns = [
            {
                'name': 'actual_start_at',
                'sql': 'ALTER TABLE audits ADD COLUMN actual_start_at DATETIME'
            },
            {
                'name': 'schedule_lock',
                'sql': 'ALTER TABLE audits ADD COLUMN schedule_lock BOOLEAN DEFAULT 0'
            },
            {
                'name': 'lock_reason',
                'sql': 'ALTER TABLE audits ADD COLUMN lock_reason TEXT'
            },
            {
                'name': 'reschedule_count',
                'sql': 'ALTER TABLE audits ADD COLUMN reschedule_count INTEGER DEFAULT 0'
            },
            {
                'name': 'last_rescheduled_at',
                'sql': 'ALTER TABLE audits ADD COLUMN last_rescheduled_at DATETIME'
            },
            {
                'name': 'risk_register_item_id',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_register_item_id INTEGER'
            },
            {
                'name': 'risk_assessment_method',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_assessment_method VARCHAR(50)'
            },
            {
                'name': 'risk_assessment_date',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_assessment_date DATETIME'
            },
            {
                'name': 'risk_assessor_id',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_assessor_id INTEGER'
            },
            {
                'name': 'risk_treatment_plan',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_treatment_plan TEXT'
            },
            {
                'name': 'risk_monitoring_frequency',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_monitoring_frequency VARCHAR(100)'
            },
            {
                'name': 'risk_review_frequency',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_review_frequency VARCHAR(100)'
            },
            {
                'name': 'risk_control_effectiveness',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_control_effectiveness VARCHAR(50)'
            },
            {
                'name': 'risk_residual_score',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_residual_score FLOAT'
            },
            {
                'name': 'risk_residual_level',
                'sql': 'ALTER TABLE audits ADD COLUMN risk_residual_level VARCHAR(50)'
            }
        ]
        
        added_count = 0
        for column in missing_columns:
            if column['name'] not in current_columns:
                try:
                    db.execute(text(column['sql']))
                    print(f"✅ Added column: {column['name']}")
                    added_count += 1
                except Exception as e:
                    print(f"⚠️  Error adding column {column['name']}: {e}")
            else:
                print(f"ℹ️  Column already exists: {column['name']}")
        
        db.commit()
        print(f"🎉 Added {added_count} missing columns to audits table")
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        db.rollback()
    finally:
        db.close()

def verify_audit_schema():
    """Verify that all required columns exist"""
    print("🔍 Verifying audit schema...")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('audits')
    column_names = [col['name'] for col in columns]
    
    required_columns = [
        'id', 'title', 'audit_type', 'scope', 'objectives', 'criteria',
        'start_date', 'end_date', 'actual_start_at', 'actual_end_at',
        'status', 'auditor_id', 'lead_auditor_id', 'auditee_department',
        'program_id', 'created_by', 'created_at', 'updated_at',
        'schedule_lock', 'lock_reason', 'reschedule_count', 'last_rescheduled_at',
        'risk_register_item_id', 'risk_assessment_method', 'risk_assessment_date',
        'risk_assessor_id', 'risk_treatment_plan', 'risk_monitoring_frequency',
        'risk_review_frequency', 'risk_control_effectiveness', 'risk_residual_score',
        'risk_residual_level'
    ]
    
    missing_columns = [col for col in required_columns if col not in column_names]
    
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False
    else:
        print("✅ All required columns are present")
        return True

def test_audit_creation():
    """Test creating an audit to ensure the schema works"""
    print("🧪 Testing audit creation...")
    
    from app.models.audit_mgmt import Audit, AuditType, AuditStatus
    from app.models.user import User
    
    db = SessionLocal()
    try:
        # Check if we have a user to use as created_by
        user = db.query(User).first()
        if not user:
            print("❌ No users found in database")
            return False
        
        # Try to create a test audit
        test_audit = Audit(
            title="Test Audit",
            audit_type=AuditType.INTERNAL,
            scope="Test scope",
            objectives="Test objectives",
            criteria="Test criteria",
            status=AuditStatus.PLANNED,
            created_by=user.id
        )
        
        db.add(test_audit)
        db.commit()
        
        print("✅ Test audit created successfully")
        
        # Clean up
        db.delete(test_audit)
        db.commit()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test audit: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function to fix audit database"""
    print("🚀 Starting audit database fix...")
    
    # Step 1: Add missing columns
    add_missing_audit_columns()
    
    # Step 2: Verify schema
    if not verify_audit_schema():
        print("❌ Schema verification failed")
        return
    
    # Step 3: Test audit creation
    if not test_audit_creation():
        print("❌ Audit creation test failed")
        return
    
    print("🎉 Audit database fix completed successfully!")

if __name__ == "__main__":
    main()

