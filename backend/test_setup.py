#!/usr/bin/env python3
"""
Simple test to check if our setup is working
"""

import sys
import os

def test_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        from app.core.database import Base, get_db
        print("✅ Database imports successful")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from app.models.prp import PRPProgram, PRPCategory
        print("✅ PRP model imports successful")
    except Exception as e:
        print(f"❌ PRP model import failed: {e}")
        return False
    
    try:
        from app.services.prp_service import PRPService
        print("✅ PRP service import successful")
    except Exception as e:
        print(f"❌ PRP service import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 PRP Module Setup Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test database
    db_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    if imports_ok and db_ok:
        print("✅ All setup tests passed!")
        return True
    else:
        print("❌ Some setup tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
