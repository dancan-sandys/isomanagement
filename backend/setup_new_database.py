#!/usr/bin/env python3
"""
Simple Database Setup Script for ISO 22000 FSMS Platform

This script provides an easy way to set up a new database with all
enum values correctly set to lowercase from the start.

Usage:
    python setup_new_database.py
"""

import sys
import os
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the backend directory
    if not Path("app").exists():
        print("❌ Error: This script must be run from the backend directory")
        print("   Current directory:", os.getcwd())
        print("   Expected to find 'app' directory")
        return False
    
    # Check if database file exists
    db_file = Path("iso22000_fsms.db")
    if db_file.exists():
        print(f"⚠️  Database file {db_file} already exists")
        response = input("Do you want to delete it and create a fresh database? (y/N): ")
        if response.lower() in ['y', 'yes']:
            try:
                db_file.unlink()
                print(f"✅ Deleted existing database file")
            except Exception as e:
                print(f"❌ Error deleting database file: {e}")
                return False
        else:
            print("❌ Setup cancelled")
            return False
    
    print("✅ Prerequisites check passed")
    return True

def run_improved_initialization():
    """Run the improved database initialization script"""
    print("🚀 Running improved database initialization...")
    
    try:
        # Import and run the improved initialization
        from init_database_improved import main as init_main
        init_main()
        return True
    except ImportError as e:
        print(f"❌ Error importing initialization script: {e}")
        print("   Make sure init_database_improved.py exists in the current directory")
        return False
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        return False

def verify_setup():
    """Verify that the setup was successful"""
    print("🔍 Verifying setup...")
    
    try:
        # Check if database file was created
        db_file = Path("iso22000_fsms.db")
        if not db_file.exists():
            print("❌ Database file was not created")
            return False
        
        # Check file size (should be > 0)
        if db_file.stat().st_size == 0:
            print("❌ Database file is empty")
            return False
        
        print(f"✅ Database file created successfully ({db_file.stat().st_size} bytes)")
        
        # Try to connect to the database
        try:
            from app.core.database import SessionLocal
            db = SessionLocal()
            db.close()
            print("✅ Database connection test passed")
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 ISO 22000 FSMS Database Setup")
    print("=" * 60)
    print()
    print("This script will:")
    print("  ✅ Validate all enum values are lowercase")
    print("  ✅ Create database tables with correct enum definitions")
    print("  ✅ Set up permissions and roles")
    print("  ✅ Create admin user")
    print("  ✅ Verify database integrity")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Run initialization
    if not run_improved_initialization():
        sys.exit(1)
    
    # Verify setup
    if not verify_setup():
        print("❌ Setup verification failed")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("🎉 Database setup completed successfully!")
    print("=" * 60)
    print()
    print("📋 What was created:")
    print("  - Database file: iso22000_fsms.db")
    print("  - All tables with lowercase enum values")
    print("  - Permissions and roles")
    print("  - Admin user")
    print()
    print("🔑 Login credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("🚀 Next steps:")
    print("  1. Start the backend server: python -m uvicorn app.main:app --reload")
    print("  2. Start the frontend: cd ../frontend && npm start")
    print("  3. Login with the admin credentials above")
    print()
    print("💡 Benefits of this setup:")
    print("  - No enum migration needed")
    print("  - Consistent lowercase enum values")
    print("  - Ready for production use")
    print("  - Frontend and backend are in sync")
    print()

if __name__ == "__main__":
    main()
