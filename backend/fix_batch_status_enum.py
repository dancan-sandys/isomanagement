#!/usr/bin/env python3
"""
Fix Batch Status Enum Values
Update status values in batches table to match enum definition
"""

import sqlite3
import sys

def fix_batch_status_enum():
    """Fix status enum values in batches table"""
    print("🔧 Fixing Batch Status Enum Values")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # Get current status values
        cursor.execute("SELECT DISTINCT status FROM batches")
        current_values = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current status values: {current_values}")
        
        # Define the correct enum values (lowercase as defined in enum)
        correct_values = {
            'IN_PRODUCTION': 'in_production',
            'in_production': 'in_production',  # already correct
            'COMPLETED': 'completed',
            'completed': 'completed',  # already correct
            'QUARANTINED': 'quarantined',
            'quarantined': 'quarantined',  # already correct
            'RELEASED': 'released',
            'released': 'released',  # already correct
            'RECALLED': 'recalled',
            'recalled': 'recalled',  # already correct
            'DISPOSED': 'disposed',
            'disposed': 'disposed'  # already correct
        }
        
        # Update incorrect values
        updates_made = 0
        for old_value, new_value in correct_values.items():
            if old_value != new_value:  # Only update if different
                cursor.execute(
                    "UPDATE batches SET status = ? WHERE status = ?",
                    (new_value, old_value)
                )
                if cursor.rowcount > 0:
                    print(f"✅ Updated {cursor.rowcount} records: '{old_value}' → '{new_value}'")
                    updates_made += cursor.rowcount
        
        if updates_made == 0:
            print("✅ All status values are already correct")
        
        # Verify the fix
        cursor.execute("SELECT DISTINCT status FROM batches")
        final_values = [row[0] for row in cursor.fetchall()]
        print(f"📋 Final status values: {final_values}")
        
        # Check if all values are valid enum values
        valid_enum_values = ['in_production', 'completed', 'quarantined', 'released', 'recalled', 'disposed']
        invalid_values = [v for v in final_values if v not in valid_enum_values]
        
        if invalid_values:
            print(f"⚠️  Warning: Found invalid values: {invalid_values}")
            return False
        else:
            print("✅ All status values are now valid enum values")
        
        conn.commit()
        print("✅ Batch status enum fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing batch status enum: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_batch_status_enum()
    sys.exit(0 if success else 1)
