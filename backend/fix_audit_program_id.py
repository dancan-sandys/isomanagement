#!/usr/bin/env python3
"""
Fix audit program_id column issue
"""
import sqlite3
import os

def fix_audit_program_id():
    """Add program_id column to audits table if it doesn't exist"""
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if program_id column exists
        cursor.execute("PRAGMA table_info(audits)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'program_id' not in columns:
            print("Adding program_id column to audits table...")
            cursor.execute("ALTER TABLE audits ADD COLUMN program_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_program_id ON audits(program_id)")
            conn.commit()
            print("✅ Successfully added program_id column to audits table")
        else:
            print("✅ program_id column already exists in audits table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(audits)")
        columns = cursor.fetchall()
        program_id_col = None
        for col in columns:
            if col[1] == 'program_id':
                program_id_col = col
                break
        
        if program_id_col:
            print(f"✅ Verified: program_id column exists (type: {program_id_col[2]}, nullable: {program_id_col[3]})")
        else:
            print("❌ Error: program_id column not found after addition")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing audit program_id: {e}")
        return False

if __name__ == "__main__":
    success = fix_audit_program_id()
    if success:
        print("\n🎉 Audit program_id fix completed successfully!")
    else:
        print("\n💥 Audit program_id fix failed!")
