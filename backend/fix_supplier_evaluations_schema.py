#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix supplier_evaluations table schema
"""
import sqlite3
import os

def fix_supplier_evaluations_schema():
    """Fix the supplier_evaluations table schema"""
    print("Fixing supplier_evaluations table schema...")
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(supplier_evaluations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        # Add missing columns
        missing_columns = []
        
        if 'hygiene_score' not in columns:
            missing_columns.append('hygiene_score REAL')
            print("Adding hygiene_score column...")
            cursor.execute("ALTER TABLE supplier_evaluations ADD COLUMN hygiene_score REAL")
        
        if 'hygiene_comments' not in columns:
            missing_columns.append('hygiene_comments TEXT')
            print("Adding hygiene_comments column...")
            cursor.execute("ALTER TABLE supplier_evaluations ADD COLUMN hygiene_comments TEXT")
        
        if missing_columns:
            conn.commit()
            print(f"✅ Added {len(missing_columns)} missing columns: {missing_columns}")
        else:
            print("✅ All columns already exist!")
            
        # Verify the fix
        cursor.execute("PRAGMA table_info(supplier_evaluations)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {updated_columns}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error fixing schema: {e}")

if __name__ == "__main__":
    fix_supplier_evaluations_schema()
