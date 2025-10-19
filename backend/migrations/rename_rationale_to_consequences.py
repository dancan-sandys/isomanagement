"""
Database Migration: Rename rationale column to consequences
==========================================================

This migration renames the 'rationale' column to 'consequences' in the hazards table.

For SQLite (version 3.25.0+):
    ALTER TABLE hazards RENAME COLUMN rationale TO consequences;

For older SQLite or manual execution:
    See run_sqlite_migration() function below
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Get the path to the database file"""
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / "iso22000_fsms.db"
    return str(db_path)

def check_sqlite_version(conn):
    """Check SQLite version"""
    cursor = conn.cursor()
    cursor.execute("SELECT sqlite_version()")
    version = cursor.fetchone()[0]
    print(f"SQLite version: {version}")
    
    # Parse version to check if >= 3.25.0
    major, minor, patch = map(int, version.split('.'))
    return (major, minor, patch) >= (3, 25, 0)

def run_sqlite_migration():
    """Run migration for SQLite database"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please ensure the database exists before running migration")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting migration: Rename rationale → consequences")
        print("=" * 60)
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(hazards)")
        columns_info = cursor.fetchall()
        columns = {col[1]: col for col in columns_info}
        
        print(f"📋 Current columns in hazards table:")
        has_rationale = False
        has_consequences = False
        for col in columns_info:
            col_name = col[1]
            if col_name in ['rationale', 'consequences']:
                print(f"   - {col_name}: {col[2]} (column #{col[0]})")
                if col_name == 'rationale':
                    has_rationale = True
                if col_name == 'consequences':
                    has_consequences = True
        
        if not has_rationale and not has_consequences:
            print("   - Neither 'rationale' nor 'consequences' found!")
        
        if has_consequences and not has_rationale:
            print("\n✅ Column 'consequences' already exists and 'rationale' is gone!")
            print("   Migration already completed.")
            return True
        
        if not has_rationale:
            print("\n⚠️  Column 'rationale' does not exist!")
            print("   Nothing to migrate.")
            return True
        
        # Check SQLite version
        supports_rename = check_sqlite_version(conn)
        
        if supports_rename:
            print("\n✓ SQLite supports RENAME COLUMN (version >= 3.25.0)")
            print("Renaming column...")
            
            cursor.execute("ALTER TABLE hazards RENAME COLUMN rationale TO consequences")
            conn.commit()
            
            print("✅ Column renamed successfully!")
            
        else:
            print("\n⚠️  SQLite version < 3.25.0 - Using table recreation method")
            print("This will recreate the table with the new column name...")
            
            # Get the current table schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='hazards'")
            create_table_sql = cursor.fetchone()[0]
            
            # Create new table with consequences column
            print("\n1. Creating temporary table with new schema...")
            cursor.execute("""
                CREATE TABLE hazards_new (
                    id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    process_step_id INTEGER NOT NULL,
                    hazard_type VARCHAR(10) NOT NULL,
                    hazard_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    consequences TEXT,
                    likelihood INTEGER,
                    severity INTEGER,
                    risk_score INTEGER,
                    risk_level VARCHAR(8),
                    control_measures TEXT,
                    is_controlled BOOLEAN,
                    control_effectiveness INTEGER,
                    is_ccp BOOLEAN,
                    ccp_justification TEXT,
                    decision_tree_steps TEXT,
                    decision_tree_run_at DATETIME,
                    decision_tree_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    created_by INTEGER NOT NULL,
                    prp_reference_ids JSON,
                    reference_documents JSON,
                    risk_register_item_id INTEGER,
                    risk_assessment_method VARCHAR(100),
                    risk_assessment_date DATETIME,
                    risk_assessor_id INTEGER,
                    risk_treatment_plan TEXT,
                    risk_monitoring_frequency VARCHAR(100),
                    risk_review_frequency VARCHAR(100),
                    risk_control_effectiveness INTEGER,
                    risk_residual_score INTEGER,
                    risk_residual_level VARCHAR(50),
                    risk_acceptable BOOLEAN,
                    risk_justification TEXT,
                    risk_strategy_justification TEXT,
                    subsequent_step TEXT,
                    risk_strategy VARCHAR(50),
                    opprp_justification TEXT,
                    
                    PRIMARY KEY (id),
                    FOREIGN KEY(product_id) REFERENCES products (id),
                    FOREIGN KEY(process_step_id) REFERENCES process_flows (id),
                    FOREIGN KEY(decision_tree_by) REFERENCES users (id),
                    FOREIGN KEY(created_by) REFERENCES users (id)
                )
            """)
            
            # Copy data from old table to new table
            print("2. Copying data from old table...")
            cursor.execute("""
                INSERT INTO hazards_new 
                SELECT id, product_id, process_step_id, hazard_type, hazard_name, description,
                       rationale as consequences,
                       likelihood, severity, risk_score, risk_level, control_measures,
                       is_controlled, control_effectiveness, is_ccp, ccp_justification,
                       decision_tree_steps, decision_tree_run_at, decision_tree_by,
                       created_at, updated_at, created_by,
                       prp_reference_ids, reference_documents,
                       risk_register_item_id, risk_assessment_method, risk_assessment_date,
                       risk_assessor_id, risk_treatment_plan, risk_monitoring_frequency,
                       risk_review_frequency, risk_control_effectiveness, risk_residual_score,
                       risk_residual_level, risk_acceptable, risk_justification,
                       risk_strategy_justification, subsequent_step, risk_strategy,
                       NULL as opprp_justification
                FROM hazards
            """)
            
            # Drop old table
            print("3. Dropping old table...")
            cursor.execute("DROP TABLE hazards")
            
            # Rename new table
            print("4. Renaming new table...")
            cursor.execute("ALTER TABLE hazards_new RENAME TO hazards")
            
            # Recreate indexes
            print("5. Recreating indexes...")
            cursor.execute("CREATE INDEX ix_hazards_id ON hazards (id)")
            
            conn.commit()
            print("✅ Table recreated with 'consequences' column!")
        
        # Verify the change
        print("\n🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(hazards)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        if 'consequences' in columns and 'rationale' not in columns:
            print("✅ Verification successful!")
            print("   - Column 'consequences' exists")
            print("   - Column 'rationale' removed")
        else:
            print("⚠️  Verification failed!")
            if 'rationale' in columns:
                print("   - Column 'rationale' still exists")
            if 'consequences' not in columns:
                print("   - Column 'consequences' not found")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  HAZARDS TABLE MIGRATION                                 ║")
    print("║  Rename 'rationale' column to 'consequences'             ║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    success = run_sqlite_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your backend server")
        print("   2. Test hazard creation and display")
    else:
        print("\n❌ Migration failed!")
        print("   Please check the error messages above.")
    
    print("\n")

