#!/usr/bin/env python3
"""
Script to fix any existing recall records with incorrect enum values.
"""

import sqlite3

def fix_recall_types():
    """Fix any existing recall records with incorrect enum values"""
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
        
        # Fix any incorrect values
        updates_needed = []
        
        if 'CLASS_I' in current_types:
            cursor.execute("UPDATE recalls SET recall_type = 'class_i' WHERE recall_type = 'CLASS_I'")
            updates_needed.append('CLASS_I -> class_i')
        
        if 'CLASS_II' in current_types:
            cursor.execute("UPDATE recalls SET recall_type = 'class_ii' WHERE recall_type = 'CLASS_II'")
            updates_needed.append('CLASS_II -> class_ii')
        
        if 'CLASS_III' in current_types:
            cursor.execute("UPDATE recalls SET recall_type = 'class_iii' WHERE recall_type = 'CLASS_III'")
            updates_needed.append('CLASS_III -> class_iii')
        
        if updates_needed:
            conn.commit()
            print(f"Updated recall types: {', '.join(updates_needed)}")
        else:
            print("No updates needed - recall types are already correct")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error fixing recall types: {e}")
        return False

def main():
    """Main function"""
    print("Fixing Recall Type Enum Values...")
    print("=" * 40)
    
    success = fix_recall_types()
    
    if success:
        print("\nRecall type fixes completed!")
        print("\nNext steps:")
        print("1. Test traceability endpoints")
        print("2. Verify recall creation works")
    else:
        print("\nFailed to fix recall types")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
