#!/usr/bin/env python3
"""
Final PRP Schema Fixes
Fix all remaining schema issues in the PRP module
"""

import sqlite3
import sys

def fix_prp_final_schema():
    """Fix all remaining PRP schema issues"""
    print("🔧 Final PRP Schema Fixes")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # 1. Fix prp_preventive_actions table
        print("\n📋 Fixing prp_preventive_actions table...")
        cursor.execute("PRAGMA table_info(prp_preventive_actions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        missing_columns = [
            ("progress_percentage", "INTEGER DEFAULT 0"),
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
            ("trend_analysis", "TEXT"),
            ("improvement_actions", "TEXT"),
            ("follow_up_required", "BOOLEAN DEFAULT FALSE"),
            ("follow_up_date", "DATETIME"),
            ("escalation_required", "BOOLEAN DEFAULT FALSE"),
            ("escalated_to", "INTEGER"),
            ("escalated_at", "DATETIME"),
            ("effectiveness_measurement", "TEXT"),
            ("effectiveness_result", "VARCHAR(50)"),
            ("reviewed_by", "INTEGER"),
            ("reviewed_at", "DATETIME")
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE prp_preventive_actions ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 2. Verify prp_corrective_actions table
        print("\n📋 Verifying prp_corrective_actions table...")
        cursor.execute("PRAGMA table_info(prp_corrective_actions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        # Check if program_id is nullable
        cursor.execute("PRAGMA table_info(prp_corrective_actions)")
        columns_info = cursor.fetchall()
        program_id_info = [col for col in columns_info if col[1] == 'program_id'][0]
        if program_id_info[3] == 1:  # NOT NULL
            print("⚠️  program_id is still NOT NULL, but this should be fixed")
        else:
            print("✅ program_id is nullable")
        
        # 3. Check for any other missing columns in other PRP tables
        print("\n📋 Checking for any other missing columns...")
        
        # Check prp_risk_matrices
        cursor.execute("PRAGMA table_info(prp_risk_matrices)")
        risk_matrices_columns = [col[1] for col in cursor.fetchall()]
        if 'is_active' not in risk_matrices_columns:
            cursor.execute("ALTER TABLE prp_risk_matrices ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("✅ Added is_active to prp_risk_matrices")
        
        # Check prp_programs
        cursor.execute("PRAGMA table_info(prp_programs)")
        programs_columns = [col[1] for col in cursor.fetchall()]
        if 'is_active' not in programs_columns:
            cursor.execute("ALTER TABLE prp_programs ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("✅ Added is_active to prp_programs")
        
        # Check prp_checklists
        cursor.execute("PRAGMA table_info(prp_checklists)")
        checklists_columns = [col[1] for col in cursor.fetchall()]
        if 'is_active' not in checklists_columns:
            cursor.execute("ALTER TABLE prp_checklists ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("✅ Added is_active to prp_checklists")
        
        # Check prp_risk_assessments
        cursor.execute("PRAGMA table_info(prp_risk_assessments)")
        risk_assessments_columns = [col[1] for col in cursor.fetchall()]
        if 'is_active' not in risk_assessments_columns:
            cursor.execute("ALTER TABLE prp_risk_assessments ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            print("✅ Added is_active to prp_risk_assessments")
        
        # 4. Create any missing indexes
        print("\n📋 Creating performance indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_prp_preventive_actions_is_active ON prp_preventive_actions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_prp_preventive_actions_program_id ON prp_preventive_actions(program_id)",
            "CREATE INDEX IF NOT EXISTS idx_prp_preventive_actions_status ON prp_preventive_actions(status)",
            "CREATE INDEX IF NOT EXISTS idx_prp_corrective_actions_program_id ON prp_corrective_actions(program_id)",
            "CREATE INDEX IF NOT EXISTS idx_prp_corrective_actions_status ON prp_corrective_actions(status)",
            "CREATE INDEX IF NOT EXISTS idx_prp_corrective_actions_source_type ON prp_corrective_actions(source_type)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
        
        # 5. Test the fixes
        print("\n📋 Testing the fixes...")
        
        # Test inserting a corrective action without program_id
        try:
            cursor.execute("""
                INSERT INTO prp_corrective_actions 
                (action_code, source_type, source_id, non_conformance_description, non_conformance_date, 
                 severity, action_description, action_type, responsible_person, assigned_to, 
                 target_completion_date, status, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, ('TEST001', 'inspection', 1, 'Test description', '2025-08-19', 
                  'medium', 'Test action', 'corrective', 1, 1, '2025-12-31', 'open', 12))
            
            # Get the inserted ID
            test_id = cursor.lastrowid
            
            # Clean up the test record
            cursor.execute("DELETE FROM prp_corrective_actions WHERE id = ?", (test_id,))
            
            print("✅ Corrective action creation test passed (program_id can be NULL)")
        except Exception as e:
            print(f"❌ Corrective action creation test failed: {str(e)}")
            return False
        
        # Test inserting a preventive action with progress_percentage
        try:
            cursor.execute("""
                INSERT INTO prp_preventive_actions 
                (action_code, trigger_type, trigger_description, program_id, action_description, 
                 objective, responsible_person, assigned_to, planned_start_date, planned_completion_date, 
                 status, created_by, created_at, progress_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
            """, ('TEST001', 'scheduled', 'Test trigger', 1, 'Test action', 
                  'Test objective', 1, 1, '2025-08-19', '2025-12-31', 'open', 12, 50))
            
            # Get the inserted ID
            test_id = cursor.lastrowid
            
            # Clean up the test record
            cursor.execute("DELETE FROM prp_preventive_actions WHERE id = ?", (test_id,))
            
            print("✅ Preventive action creation test passed (progress_percentage works)")
        except Exception as e:
            print(f"❌ Preventive action creation test failed: {str(e)}")
            return False
        
        conn.commit()
        print("\n✅ Final PRP schema fixes completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing PRP schema: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_prp_final_schema()
    sys.exit(0 if success else 1)
