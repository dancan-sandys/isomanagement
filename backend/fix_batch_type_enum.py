#!/usr/bin/env python3
"""
Fix Batch Type Enum Values
Update batch_type values in batches table to match enum definition
"""

import sqlite3
import sys

def fix_batch_type_enum():
    """Fix batch_type enum values in batches table"""
    print("🔧 Fixing Batch Type Enum Values")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # Get current batch_type values
        cursor.execute("SELECT DISTINCT batch_type FROM batches")
        current_values = [row[0] for row in cursor.fetchall()]
        print(f"📋 Current batch_type values: {current_values}")
        
        # Define the correct enum values (lowercase as defined in enum)
        correct_values = {
            'RAW_MILK': 'raw_milk',
            'raw_milk': 'raw_milk',  # already correct
            'ADDITIVE': 'additive',
            'additive': 'additive',  # already correct
            'CULTURE': 'culture',
            'culture': 'culture',  # already correct
            'PACKAGING': 'packaging',
            'packaging': 'packaging',  # already correct
            'FINAL_PRODUCT': 'final_product',
            'final_product': 'final_product',  # already correct
            'INTERMEDIATE': 'intermediate',
            'intermediate': 'intermediate'  # already correct
        }
        
        # Update incorrect values
        updates_made = 0
        for old_value, new_value in correct_values.items():
            if old_value != new_value:  # Only update if different
                cursor.execute(
                    "UPDATE batches SET batch_type = ? WHERE batch_type = ?",
                    (new_value, old_value)
                )
                if cursor.rowcount > 0:
                    print(f"✅ Updated {cursor.rowcount} records: '{old_value}' → '{new_value}'")
                    updates_made += cursor.rowcount
        
        if updates_made == 0:
            print("✅ All batch_type values are already correct")
        
        # Verify the fix
        cursor.execute("SELECT DISTINCT batch_type FROM batches")
        final_values = [row[0] for row in cursor.fetchall()]
        print(f"📋 Final batch_type values: {final_values}")
        
        # Check if all values are valid enum values
        valid_enum_values = ['raw_milk', 'additive', 'culture', 'packaging', 'final_product', 'intermediate']
        invalid_values = [v for v in final_values if v not in valid_enum_values]
        
        if invalid_values:
            print(f"⚠️  Warning: Found invalid values: {invalid_values}")
            return False
        else:
            print("✅ All batch_type values are now valid enum values")
        
        conn.commit()
        print("✅ Batch type enum fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing batch type enum: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_batch_type_enum()
    sys.exit(0 if success else 1)
