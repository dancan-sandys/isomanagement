#!/usr/bin/env python3
"""
Database Reset Script
This script completely resets the database by dropping all tables and recreating them
Use this if you encounter persistent table creation issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from sqlalchemy import create_engine, text
from app.core.config import settings

def reset_database():
    """Completely reset the database"""
    print("🗑️  Resetting database...")
    
    # Get database URL
    database_url = settings.DATABASE_URL
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        
        # Delete the database file
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"  ✓ Deleted database file: {db_path}")
        else:
            print(f"  ⚠️  Database file not found: {db_path}")
        
        # Create new empty database
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # Test connection
        print("  ✓ Created new empty database")
        
        print("✅ Database reset complete!")
        print("  💡 You can now run setup_database_complete.py to populate the database")
        
    else:
        print("❌ This reset script only works with SQLite databases")
        print(f"  Current database URL: {database_url}")

if __name__ == "__main__":
    reset_database()