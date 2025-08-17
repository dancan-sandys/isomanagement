#!/usr/bin/env python3
"""
Check if program_id column exists in audits table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text

def check_audits_table():
    """Check if program_id column exists in audits table"""
    try:
        with engine.connect() as conn:
            # Check if audits table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='audits'"))
            if not result.fetchone():
                print("❌ audits table does not exist")
                return False
            
            # Get table schema
            result = conn.execute(text("PRAGMA table_info(audits)"))
            columns = result.fetchall()
            
            print("📋 audits table columns:")
            program_id_exists = False
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                if col[1] == 'program_id':
                    program_id_exists = True
            
            if program_id_exists:
                print("✅ program_id column exists in audits table")
            else:
                print("❌ program_id column is missing from audits table")
            
            return program_id_exists
            
    except Exception as e:
        print(f"❌ Error checking audits table: {e}")
        return False

if __name__ == "__main__":
    check_audits_table()
