#!/usr/bin/env python3
"""
Comprehensive PRP Schema Fixes
Fix all missing columns in the PRP module
"""

import sqlite3
import sys

def fix_prp_schema():
    """Fix all missing columns in PRP module"""
    print("🔧 Fixing PRP Schema")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # 1. Fix prp_risk_matrices table
        print("\n📋 Fixing prp_risk_matrices table...")
        cursor.execute("PRAGMA table_info(prp_risk_matrices)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        missing_columns = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("version", "VARCHAR(50)"),
            ("approval_status", "VARCHAR(50)"),
            ("approved_by", "INTEGER"),
            ("approved_at", "DATETIME"),
            ("review_frequency", "VARCHAR(100)"),
            ("last_review_date", "DATETIME"),
            ("next_review_date", "DATETIME")
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE prp_risk_matrices ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 2. Fix prp_programs table (check for any missing columns)
        print("\n📋 Checking prp_programs table...")
        cursor.execute("PRAGMA table_info(prp_programs)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        # Check for common missing columns
        common_missing = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("version", "VARCHAR(50)"),
            ("approval_status", "VARCHAR(50)"),
            ("approved_by", "INTEGER"),
            ("approved_at", "DATETIME"),
            ("review_frequency", "VARCHAR(100)"),
            ("last_review_date", "DATETIME"),
            ("next_review_date", "DATETIME"),
            ("department_id", "INTEGER"),
            ("location_id", "INTEGER"),
            ("priority", "VARCHAR(50)"),
            ("budget", "DECIMAL(10,2)"),
            ("resources_required", "TEXT"),
            ("success_criteria", "TEXT"),
            ("kpis", "TEXT"),
            ("compliance_requirements", "TEXT"),
            ("regulatory_references", "TEXT")
        ]
        
        for column_name, column_type in common_missing:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE prp_programs ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 3. Fix prp_checklists table (check for any missing columns)
        print("\n📋 Checking prp_checklists table...")
        cursor.execute("PRAGMA table_info(prp_checklists)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        checklist_missing = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("version", "VARCHAR(50)"),
            ("approval_status", "VARCHAR(50)"),
            ("approved_by", "INTEGER"),
            ("approved_at", "DATETIME"),
            ("frequency", "VARCHAR(100)"),
            ("priority", "VARCHAR(50)"),
            ("department_id", "INTEGER"),
            ("location_id", "INTEGER"),
            ("compliance_percentage", "DECIMAL(5,2)"),
            ("trend_analysis", "TEXT"),
            ("improvement_actions", "TEXT"),
            ("follow_up_required", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_date", "DATETIME"),
            ("escalation_required", "BOOLEAN DEFAULT FALSE"),
            ("escalated_to", "INTEGER"),
            ("escalated_at", "DATETIME")
        ]
        
        for column_name, column_type in checklist_missing:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE prp_checklists ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 4. Fix prp_risk_assessments table (check for any missing columns)
        print("\n📋 Checking prp_risk_assessments table...")
        cursor.execute("PRAGMA table_info(prp_risk_assessments)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        risk_assessment_missing = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("version", "VARCHAR(50)"),
            ("approval_status", "VARCHAR(50)"),
            ("approved_by", "INTEGER"),
            ("approved_at", "DATETIME"),
            ("review_frequency", "VARCHAR(100)"),
            ("last_review_date", "DATETIME"),
            ("next_review_date", "DATETIME"),
            ("department_id", "INTEGER"),
            ("location_id", "INTEGER"),
            ("priority", "VARCHAR(50)"),
            ("trend_analysis", "TEXT"),
            ("improvement_actions", "TEXT"),
            ("follow_up_required", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_date", "DATETIME"),
            ("escalation_required", "BOOLEAN DEFAULT FALSE"),
            ("escalated_to", "INTEGER"),
            ("escalated_at", "DATETIME"),
            ("risk_matrix_id", "INTEGER"),
            ("risk_score", "INTEGER"),
            ("risk_level", "VARCHAR(50)"),
            ("risk_category", "VARCHAR(100)"),
            ("risk_owner", "INTEGER"),
            ("risk_mitigation_plan", "TEXT"),
            ("risk_monitoring_plan", "TEXT"),
            ("risk_review_plan", "TEXT")
        ]
        
        for column_name, column_type in risk_assessment_missing:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE prp_risk_assessments ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 5. Fix prp_corrective_actions table (check for any missing columns)
        print("\n📋 Checking prp_corrective_actions table...")
        cursor.execute("PRAGMA table_info(prp_corrective_actions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        corrective_action_missing = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("version", "VARCHAR(50)"),
            ("approval_status", "VARCHAR(50)"),
            ("approved_by", "INTEGER"),
            ("approved_at", "DATETIME"),
            ("priority", "VARCHAR(50)"),
            ("department_id", "INTEGER"),
            ("location_id", "INTEGER"),
            ("trend_analysis", "TEXT"),
            ("improvement_actions", "TEXT"),
            ("follow_up_required", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_date", "DATETIME"),
            ("escalation_required", "BOOLEAN DEFAULT FALSE"),
            ("escalated_to", "INTEGER"),
            ("escalated_at", "DATETIME"),
            ("root_cause_analysis", "TEXT"),
            ("preventive_measures", "TEXT"),
            ("effectiveness_monitoring", "TEXT"),
            ("lessons_learned", "TEXT"),
            ("documentation_updated", "BOOLEAN DEFAULT FALSE"),
            ("training_required", "BOOLEAN DEFAULT FALSE"),
            ("training_completed", "BOOLEAN DEFAULT FALSE"),
            ("training_date", "DATETIME"),
            ("verification_required", "BOOLEAN DEFAULT FALSE"),
            ("verification_completed", "BOOLEAN DEFAULT FALSE"),
            ("verification_date", "DATETIME"),
            ("verification_method", "VARCHAR(100)"),
            ("verification_results", "TEXT")
        ]
        
        for column_name, column_type in corrective_action_missing:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE prp_corrective_actions ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # Create indexes for performance
        print("\n📋 Creating performance indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_prp_risk_matrices_is_active ON prp_risk_matrices(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_prp_programs_is_active ON prp_programs(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_prp_checklists_is_active ON prp_checklists(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_prp_risk_assessments_is_active ON prp_risk_assessments(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_prp_corrective_actions_is_active ON prp_corrective_actions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_prp_programs_department_id ON prp_programs(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_prp_checklists_department_id ON prp_checklists(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_prp_risk_assessments_department_id ON prp_risk_assessments(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_prp_corrective_actions_department_id ON prp_corrective_actions(department_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
        
        conn.commit()
        print("\n✅ PRP schema fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing PRP schema: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_prp_schema()
    sys.exit(0 if success else 1)
