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
        print(f"Database backed up as: {backup_name}")
        return backup_name
    else:
        print("Database file not found!")
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
            print("Added program_id column")
        
        if 'actual_end_at' not in columns:
            cursor.execute("ALTER TABLE audits ADD COLUMN actual_end_at DATETIME")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_actual_end_at ON audits(actual_end_at)")
            missing_columns.append('actual_end_at')
            print("Added actual_end_at column")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        if missing_columns:
            print(f"Successfully added columns: {missing_columns}")
        else:
            print("All required columns already exist")
            
        return True
        
    except Exception as e:
        print(f"Error adding columns: {e}")
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
        
        print("\nFinal table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        missing = [col for col in required_columns if col not in existing_columns]
        if missing:
            print(f"Still missing columns: {missing}")
            return False
        else:
            print("All required columns present")
            return True
            
    except Exception as e:
        print(f"Error verifying migration: {e}")
        return False

def main():
    """Main migration function"""
    print("Starting Audit Schema Migration...")
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
    
    print("\nMigration completed successfully!")
    print(f"Backup saved as: {backup_file}")
    print("\nNext steps:")
    print("1. Test audit endpoints")
    print("2. Verify data integrity")
    print("3. Run comprehensive testing")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
