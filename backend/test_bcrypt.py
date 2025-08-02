#!/usr/bin/env python3
"""
Test script to verify bcrypt installation
"""

import sys

def test_bcrypt():
    """Test bcrypt functionality"""
    try:
        import bcrypt
        print("✅ bcrypt imported successfully")
        
        # Test password hashing
        password = b"test_password"
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        print("✅ Password hashing successful")
        
        # Test password verification
        if bcrypt.checkpw(password, hashed):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import bcrypt: {e}")
        return False
    except Exception as e:
        print(f"❌ bcrypt test failed: {e}")
        return False

def test_passlib():
    """Test passlib with bcrypt"""
    try:
        from passlib.context import CryptContext
        
        # Create password context
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        print("✅ passlib CryptContext created successfully")
        
        # Test password hashing
        password = "test_password"
        hashed = pwd_context.hash(password)
        print("✅ passlib password hashing successful")
        
        # Test password verification
        if pwd_context.verify(password, hashed):
            print("✅ passlib password verification successful")
        else:
            print("❌ passlib password verification failed")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import passlib: {e}")
        return False
    except Exception as e:
        print(f"❌ passlib test failed: {e}")
        return False

def main():
    print("🧪 Testing bcrypt installation...")
    print("=" * 50)
    
    bcrypt_ok = test_bcrypt()
    print()
    
    passlib_ok = test_passlib()
    print()
    
    if bcrypt_ok and passlib_ok:
        print("🎉 All tests passed! bcrypt is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please run the fix_bcrypt.py script.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 