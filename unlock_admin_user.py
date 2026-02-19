#!/usr/bin/env python3
"""
Script to unlock the admin user account by resetting failed login attempts and lockout status
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from datetime import datetime

def unlock_admin_user():
    """Unlock the admin user by resetting failed login attempts and lockout status"""
    
    # Use direct database connection to avoid model conflicts
    engine = create_engine("sqlite:///iso22000_fsms.db")
    
    try:
        with engine.connect() as conn:
            # Check if admin user exists
            result = conn.execute(text("SELECT id, username, failed_login_attempts, locked_until, is_active FROM users WHERE username = 'admin'"))
            admin_user = result.fetchone()
            
            if not admin_user:
                print("❌ Error: Admin user 'admin' not found!")
                # Show available users
                result = conn.execute(text("SELECT username, id FROM users"))
                users = result.fetchall()
                print("Available users:")
                for user in users:
                    print(f"  - {user[0]} (ID: {user[1]})")
                return False
            
            print(f"🔍 Found admin user: {admin_user[1]}")
            print(f"   Current failed attempts: {admin_user[2]}")
            print(f"   Locked until: {admin_user[3]}")
            print(f"   Is active: {admin_user[4]}")
            
            # Reset the lockout fields
            conn.execute(text("""
                UPDATE users 
                SET failed_login_attempts = 0, 
                    locked_until = NULL, 
                    is_active = 1 
                WHERE username = 'admin'
            """))
            conn.commit()
            
            print("✅ Admin user unlocked successfully!")
            print("   Failed attempts reset to: 0")
            print("   Locked until: NULL")
            print("   Is active: True")
            
            return True
        
    except Exception as e:
        print(f"❌ Error unlocking admin user: {e}")
        return False

def check_admin_status():
    """Check the current status of the admin user"""
    
    engine = create_engine("sqlite:///iso22000_fsms.db")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT username, email, full_name, is_active, is_verified, 
                       failed_login_attempts, locked_until, last_login, status 
                FROM users WHERE username = 'admin'
            """))
            admin_user = result.fetchone()
            
            if not admin_user:
                print("❌ Admin user 'admin' not found!")
                return
            
            print("📊 Admin User Status:")
            print(f"   Username: {admin_user[0]}")
            print(f"   Email: {admin_user[1]}")
            print(f"   Full Name: {admin_user[2]}")
            print(f"   Is Active: {admin_user[3]}")
            print(f"   Is Verified: {admin_user[4]}")
            print(f"   Failed Login Attempts: {admin_user[5]}")
            print(f"   Locked Until: {admin_user[6]}")
            print(f"   Last Login: {admin_user[7]}")
            print(f"   Status: {admin_user[8]}")
            
            if admin_user[6] and admin_user[6] > datetime.utcnow():
                print("🔒 User is currently LOCKED")
            else:
                print("🔓 User is currently UNLOCKED")
                
    except Exception as e:
        print(f"❌ Error checking admin status: {e}")

if __name__ == "__main__":
    print("🔧 Admin User Unlock Tool")
    print("=" * 50)
    
    # Check current status first
    print("\n1. Checking current admin status...")
    check_admin_status()
    
    # Unlock the user
    print("\n2. Unlocking admin user...")
    success = unlock_admin_user()
    
    if success:
        print("\n3. Verifying unlock...")
        check_admin_status()
        print("\n✅ Admin user has been unlocked successfully!")
        print("You can now login with:")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("\n❌ Failed to unlock admin user. Please check the error messages above.")
