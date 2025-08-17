#!/usr/bin/env python3
"""
Comprehensive Database Schema Fix Script
Fixes all identified foreign key and missing table issues
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

def check_table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def create_missing_tables():
    """Create missing tables that are causing foreign key errors"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        print("🔧 Creating missing tables...")
        
        # 1. Create food_safety_objectives table
        if not check_table_exists(cursor, 'food_safety_objectives'):
            cursor.execute("""
                CREATE TABLE food_safety_objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    objective_code VARCHAR(50) UNIQUE NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    category VARCHAR(100),
                    target_value VARCHAR(100),
                    measurement_unit VARCHAR(50),
                    frequency VARCHAR(100),
                    responsible_person_id INTEGER,
                    review_frequency VARCHAR(100),
                    last_review_date DATETIME,
                    next_review_date DATETIME,
                    status VARCHAR(20) DEFAULT 'active',
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created food_safety_objectives table")
        
        # 2. Create audit_risk_assessments table if it doesn't exist
        if not check_table_exists(cursor, 'audit_risk_assessments'):
            cursor.execute("""
                CREATE TABLE audit_risk_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id INTEGER,
                    risk_assessment_type VARCHAR(100),
                    risk_score INTEGER,
                    risk_level VARCHAR(20),
                    likelihood INTEGER,
                    severity INTEGER,
                    detectability INTEGER,
                    risk_factors TEXT,
                    mitigation_measures TEXT,
                    residual_risk INTEGER,
                    assessment_date DATETIME,
                    assessor_id INTEGER,
                    review_date DATETIME,
                    reviewer_id INTEGER,
                    status VARCHAR(20) DEFAULT 'draft',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created audit_risk_assessments table")
        
        # 3. Create fsms_risk_integration table if it doesn't exist
        if not check_table_exists(cursor, 'fsms_risk_integration'):
            cursor.execute("""
                CREATE TABLE fsms_risk_integration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    risk_register_item_id INTEGER NOT NULL,
                    fsms_element VARCHAR(100) NOT NULL,
                    fsms_element_id INTEGER,
                    impact_on_fsms TEXT NOT NULL,
                    food_safety_objective_id INTEGER,
                    interested_party_impact TEXT,
                    compliance_requirement TEXT,
                    integration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    integrated_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created fsms_risk_integration table")
        
        # 4. Create missing audit program columns
        cursor.execute("PRAGMA table_info(audit_programs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'risk_register_item_id' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN risk_register_item_id INTEGER")
            print("✅ Added risk_register_item_id to audit_programs")
        
        if 'risk_assessment_required' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN risk_assessment_required BOOLEAN DEFAULT 1")
            print("✅ Added risk_assessment_required to audit_programs")
        
        if 'risk_assessment_frequency' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN risk_assessment_frequency VARCHAR(100)")
            print("✅ Added risk_assessment_frequency to audit_programs")
        
        if 'risk_review_frequency' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN risk_review_frequency VARCHAR(100)")
            print("✅ Added risk_review_frequency to audit_programs")
        
        if 'last_risk_assessment_date' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN last_risk_assessment_date DATETIME")
            print("✅ Added last_risk_assessment_date to audit_programs")
        
        if 'next_risk_assessment_date' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN next_risk_assessment_date DATETIME")
            print("✅ Added next_risk_assessment_date to audit_programs")
        
        if 'risk_monitoring_plan' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN risk_monitoring_plan TEXT")
            print("✅ Added risk_monitoring_plan to audit_programs")
        
        if 'risk_improvement_plan' not in columns:
            cursor.execute("ALTER TABLE audit_programs ADD COLUMN risk_improvement_plan TEXT")
            print("✅ Added risk_improvement_plan to audit_programs")
        
        # 5. Create missing audit columns
        cursor.execute("PRAGMA table_info(audits)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'program_id' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN program_id INTEGER")
            print("✅ Added program_id to audits table")
        
        if 'actual_end_at' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN actual_end_at DATETIME")
            print("✅ Added actual_end_at to audits table")
        
        if 'risk_register_item_id' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN risk_register_item_id INTEGER")
            print("✅ Added risk_register_item_id to audits table")
        
        if 'risk_assessment_method' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN risk_assessment_method VARCHAR(100)")
            print("✅ Added risk_assessment_method to audits table")
        
        if 'risk_assessment_date' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN risk_assessment_date DATETIME")
            print("✅ Added risk_assessment_date to audits table")
        
        if 'risk_assessor_id' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN risk_assessor_id INTEGER")
            print("✅ Added risk_assessor_id to audits table")
        
        if 'risk_treatment_plan' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN risk_treatment_plan TEXT")
            print("✅ Added risk_treatment_plan to audits table")
        
        # 6. Create indexes for performance (only if tables exist)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_program_id ON audits(program_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_risk_register_item_id ON audits(risk_register_item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_programs_risk_register_item_id ON audit_programs(risk_register_item_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fsms_risk_integration_food_safety_objective_id ON fsms_risk_integration(food_safety_objective_id)")
            print("✅ Created performance indexes")
        except Exception as e:
            print(f"⚠️  Some indexes could not be created: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully created all missing tables and columns")
        return True
        
    except Exception as e:
        print(f"❌ Error creating missing tables: {e}")
        return False

def fix_foreign_key_constraints():
    """Fix foreign key constraint issues"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        print("🔧 Fixing foreign key constraints...")
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Add foreign key constraints where missing (only if tables exist)
        if check_table_exists(cursor, 'fsms_risk_integration') and check_table_exists(cursor, 'food_safety_objectives'):
            try:
                cursor.execute("""
                    ALTER TABLE fsms_risk_integration 
                    ADD CONSTRAINT fk_fsms_risk_integration_food_safety_objective 
                    FOREIGN KEY (food_safety_objective_id) REFERENCES food_safety_objectives(id)
                """)
                print("✅ Added foreign key constraint for fsms_risk_integration.food_safety_objective_id")
            except Exception as e:
                print(f"⚠️  Foreign key constraint already exists or error: {e}")
        
        if check_table_exists(cursor, 'audit_risk_assessments') and check_table_exists(cursor, 'audits'):
            try:
                cursor.execute("""
                    ALTER TABLE audit_risk_assessments 
                    ADD CONSTRAINT fk_audit_risk_assessments_audit 
                    FOREIGN KEY (audit_id) REFERENCES audits(id)
                """)
                print("✅ Added foreign key constraint for audit_risk_assessments.audit_id")
            except Exception as e:
                print(f"⚠️  Foreign key constraint already exists or error: {e}")
        
        if check_table_exists(cursor, 'audits') and check_table_exists(cursor, 'audit_programs'):
            try:
                cursor.execute("""
                    ALTER TABLE audits 
                    ADD CONSTRAINT fk_audits_program 
                    FOREIGN KEY (program_id) REFERENCES audit_programs(id)
                """)
                print("✅ Added foreign key constraint for audits.program_id")
            except Exception as e:
                print(f"⚠️  Foreign key constraint already exists or error: {e}")
        
        if check_table_exists(cursor, 'audits') and check_table_exists(cursor, 'risk_register'):
            try:
                cursor.execute("""
                    ALTER TABLE audits 
                    ADD CONSTRAINT fk_audits_risk_register_item 
                    FOREIGN KEY (risk_register_item_id) REFERENCES risk_register(id)
                """)
                print("✅ Added foreign key constraint for audits.risk_register_item_id")
            except Exception as e:
                print(f"⚠️  Foreign key constraint already exists or error: {e}")
        
        if check_table_exists(cursor, 'audit_programs') and check_table_exists(cursor, 'risk_register'):
            try:
                cursor.execute("""
                    ALTER TABLE audit_programs 
                    ADD CONSTRAINT fk_audit_programs_risk_register_item 
                    FOREIGN KEY (risk_register_item_id) REFERENCES risk_register(id)
                """)
                print("✅ Added foreign key constraint for audit_programs.risk_register_item_id")
            except Exception as e:
                print(f"⚠️  Foreign key constraint already exists or error: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully fixed foreign key constraints")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing foreign key constraints: {e}")
        return False

def verify_fixes():
    """Verify that all fixes were applied successfully"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        print("\n🔍 Verifying fixes...")
        
        # Check if all required tables exist
        required_tables = [
            'food_safety_objectives',
            'audit_risk_assessments',
            'fsms_risk_integration',
            'audits',
            'audit_programs'
        ]
        
        for table in required_tables:
            if check_table_exists(cursor, table):
                print(f"✅ Table {table} exists")
            else:
                print(f"❌ Table {table} missing")
        
        # Check if required columns exist
        if check_table_exists(cursor, 'audits'):
            cursor.execute("PRAGMA table_info(audits)")
            audit_columns = [col[1] for col in cursor.fetchall()]
            required_audit_columns = ['program_id', 'actual_end_at', 'risk_register_item_id']
            
            for col in required_audit_columns:
                if col in audit_columns:
                    print(f"✅ Column audits.{col} exists")
                else:
                    print(f"❌ Column audits.{col} missing")
        
        if check_table_exists(cursor, 'audit_programs'):
            cursor.execute("PRAGMA table_info(audit_programs)")
            program_columns = [col[1] for col in cursor.fetchall()]
            required_program_columns = ['risk_register_item_id', 'risk_assessment_required']
            
            for col in required_program_columns:
                if col in program_columns:
                    print(f"✅ Column audit_programs.{col} exists")
                else:
                    print(f"❌ Column audit_programs.{col} missing")
        
        # Check foreign key constraints
        if check_table_exists(cursor, 'fsms_risk_integration'):
            cursor.execute("PRAGMA foreign_key_list(fsms_risk_integration)")
            fk_list = cursor.fetchall()
            food_safety_fk_exists = any(fk[3] == 'food_safety_objectives' for fk in fk_list)
            
            if food_safety_fk_exists:
                print("✅ Foreign key constraint for fsms_risk_integration.food_safety_objective_id exists")
            else:
                print("❌ Foreign key constraint for fsms_risk_integration.food_safety_objective_id missing")
        
        conn.close()
        
        print("\n✅ Verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """Main function to run all fixes"""
    print("🚀 Starting comprehensive database schema fixes...")
    
    # Step 1: Backup database
    backup_file = backup_database()
    if not backup_file:
        return False
    
    # Step 2: Create missing tables and columns
    if not create_missing_tables():
        return False
    
    # Step 3: Fix foreign key constraints
    if not fix_foreign_key_constraints():
        return False
    
    # Step 4: Verify fixes
    if not verify_fixes():
        return False
    
    print("\n🎉 All database schema fixes completed successfully!")
    print(f"📁 Backup saved as: {backup_file}")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Test the API endpoints")
    print("3. Verify that authentication works")
    
    return True

if __name__ == "__main__":
    main()
