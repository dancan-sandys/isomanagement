#!/usr/bin/env python3
"""
Fix Recall Enum Issue
The database has 'class_ii' but SQLAlchemy expects 'CLASS_II'
"""

import sqlite3
import sys

def fix_recall_enum():
    """Fix recall enum values to use enum names instead of values"""
    print("🔧 Fixing Recall Enum Values (class_ii -> CLASS_II)")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # Update recall_type values to use enum names
        cursor.execute("""
            UPDATE recalls 
            SET recall_type = 'CLASS_II' 
            WHERE recall_type = 'class_ii'
        """)
        
        print(f"✅ Updated {cursor.rowcount} recall records")
        
        # Verify the fix
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        recall_types = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current recall types: {recall_types}")
        
        conn.commit()
        print("✅ Recall enum fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing recall enum: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_recall_enum()
    sys.exit(0 if success else 1)
