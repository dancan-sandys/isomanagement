#!/usr/bin/env python3
"""
Script to fix recall enum values in the database to match the expected uppercase format.
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

def fix_recall_enum_values():
    """Fix recall enum values to use uppercase format"""
    try:
        conn = sqlite3.connect('iso22000_fsms.db')
        cursor = conn.cursor()
        
        # Check if recalls table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recalls'")
        if not cursor.fetchone():
            print("No recalls table found - nothing to fix")
            return True
        
        # Check current recall types
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        current_types = [row[0] for row in cursor.fetchall()]
        print(f"Current recall types in database: {current_types}")
        
        # Define the mapping from lowercase to uppercase
        enum_mapping = {
            'class_i': 'CLASS_I',
            'class_ii': 'CLASS_II', 
            'class_iii': 'CLASS_III'
        }
        
        # Update recall types
        updated_count = 0
        for old_value, new_value in enum_mapping.items():
            cursor.execute(
                "UPDATE recalls SET recall_type = ? WHERE recall_type = ?",
                (new_value, old_value)
            )
            if cursor.rowcount > 0:
                print(f"Updated {cursor.rowcount} records: {old_value} -> {new_value}")
                updated_count += cursor.rowcount
        
        # Check recall status values
        cursor.execute("SELECT DISTINCT status FROM recalls")
        current_statuses = [row[0] for row in cursor.fetchall()]
        print(f"Current recall statuses in database: {current_statuses}")
        
        # Define status mapping
        status_mapping = {
            'draft': 'DRAFT',
            'initiated': 'INITIATED',
            'in_progress': 'IN_PROGRESS',
            'completed': 'COMPLETED',
            'cancelled': 'CANCELLED'
        }
        
        # Update recall statuses
        for old_value, new_value in status_mapping.items():
            cursor.execute(
                "UPDATE recalls SET status = ? WHERE status = ?",
                (new_value, old_value)
            )
            if cursor.rowcount > 0:
                print(f"Updated {cursor.rowcount} status records: {old_value} -> {new_value}")
                updated_count += cursor.rowcount
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("SELECT DISTINCT recall_type FROM recalls")
        final_types = [row[0] for row in cursor.fetchall()]
        print(f"Final recall types in database: {final_types}")
        
        cursor.execute("SELECT DISTINCT status FROM recalls")
        final_statuses = [row[0] for row in cursor.fetchall()]
        print(f"Final recall statuses in database: {final_statuses}")
        
        conn.close()
        
        print(f"\n✅ Successfully updated {updated_count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing recall enum values: {str(e)}")
        return False

def main():
    """Main function to run the enum value fix"""
    print("🔧 Fixing Recall Enum Values in Database")
    print("=" * 50)
    
    # Create backup
    backup_file = backup_database()
    if not backup_file:
        return False
    
    # Fix enum values
    success = fix_recall_enum_values()
    
    if success:
        print("\n✅ Recall enum values fixed successfully!")
        print("📝 Next steps:")
        print("   1. Restart the backend server")
        print("   2. Test the traceability endpoints again")
    else:
        print("\n❌ Failed to fix recall enum values")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        import sys
        sys.exit(1)
