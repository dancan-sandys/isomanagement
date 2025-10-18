"""
Database Migration: Add Risk Strategy to Hazards
=================================================

This migration adds the following changes to support ISO 22000 risk strategy approach:

1. Hazards table:
   - Rename 'rationale' column to 'consequences'
   - Add 'risk_strategy' enum column (CCP, OPPRP, ACCEPT, FURTHER_ANALYSIS, NOT_DETERMINED)
   - Add 'opprp_justification' text column

2. Decision Trees table:
   - Add Q5 (question 5) for OPPRP determination
   - Add 'is_opprp' boolean column

To apply this migration:
-----------------------------
Since this project uses SQLite, we'll use direct SQL commands.

For SQLite:
-----------
# Cannot directly rename or modify columns in SQLite
# Need to create new table, copy data, drop old, rename new

For PostgreSQL/MySQL:
---------------------
ALTER TABLE hazards RENAME COLUMN rationale TO consequences;
ALTER TABLE hazards ADD COLUMN risk_strategy VARCHAR(20) DEFAULT 'not_determined';
ALTER TABLE hazards ADD COLUMN opprp_justification TEXT;

ALTER TABLE decision_trees ADD COLUMN q5_answer BOOLEAN;
ALTER TABLE decision_trees ADD COLUMN q5_justification TEXT;
ALTER TABLE decision_trees ADD COLUMN q5_answered_by INTEGER REFERENCES users(id);
ALTER TABLE decision_trees ADD COLUMN q5_answered_at TIMESTAMP;
ALTER TABLE decision_trees ADD COLUMN is_opprp BOOLEAN;
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Get the path to the database file"""
    # Adjust this path based on your project structure
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / "iso22000_fsms.db"
    return str(db_path)

def run_sqlite_migration():
    """Run migration for SQLite database"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please ensure the database exists before running migration")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting migration...")
        
        # Step 1: Add new columns to hazards table
        print("1. Adding new columns to hazards table...")
        
        # Add consequences column (we'll copy rationale data to it)
        try:
            cursor.execute("ALTER TABLE hazards ADD COLUMN consequences TEXT")
            print("   - Added consequences column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - consequences column already exists")
            else:
                raise
        
        # Copy rationale to consequences
        try:
            cursor.execute("UPDATE hazards SET consequences = rationale WHERE rationale IS NOT NULL")
            print("   - Copied rationale data to consequences")
        except Exception as e:
            print(f"   - Note: {e}")
        
        # Add risk_strategy column
        try:
            cursor.execute("ALTER TABLE hazards ADD COLUMN risk_strategy VARCHAR(20) DEFAULT 'not_determined'")
            print("   - Added risk_strategy column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - risk_strategy column already exists")
            else:
                raise
        
        # Add opprp_justification column
        try:
            cursor.execute("ALTER TABLE hazards ADD COLUMN opprp_justification TEXT")
            print("   - Added opprp_justification column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - opprp_justification column already exists")
            else:
                raise
        
        # Step 2: Add new columns to decision_trees table
        print("\n2. Adding Question 5 to decision_trees table...")
        
        try:
            cursor.execute("ALTER TABLE decision_trees ADD COLUMN q5_answer BOOLEAN")
            print("   - Added q5_answer column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - q5_answer column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE decision_trees ADD COLUMN q5_justification TEXT")
            print("   - Added q5_justification column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - q5_justification column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE decision_trees ADD COLUMN q5_answered_by INTEGER REFERENCES users(id)")
            print("   - Added q5_answered_by column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - q5_answered_by column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE decision_trees ADD COLUMN q5_answered_at TIMESTAMP")
            print("   - Added q5_answered_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - q5_answered_at column already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE decision_trees ADD COLUMN is_opprp BOOLEAN")
            print("   - Added is_opprp column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   - is_opprp column already exists")
            else:
                raise
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
        
    finally:
        conn.close()

def rollback_migration():
    """Rollback migration (not recommended for production)"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Rolling back migration...")
        # Note: SQLite doesn't support DROP COLUMN directly
        # This is a placeholder for the rollback logic
        print("⚠️  Rollback not fully implemented for SQLite")
        print("   Manual intervention may be required")
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_migration()
    else:
        run_sqlite_migration()


