#!/usr/bin/env python3
"""
Check database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text

def check_tables():
    """Check what tables exist in the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            print("📋 Database tables found:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            print(f"\nTotal tables: {len(tables)}")
            
            # Check for critical tables
            critical_tables = ['users', 'roles', 'permissions', 'role_permissions']
            missing_tables = [table for table in critical_tables if table not in tables]
            
            if missing_tables:
                print(f"\n❌ Missing critical tables: {missing_tables}")
                print("🔧 Need to run database migrations!")
            else:
                print("\n✅ All critical tables present")
                
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    check_tables()
