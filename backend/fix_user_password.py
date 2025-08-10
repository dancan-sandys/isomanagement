#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix the admin user's password hash
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from app.core.security import get_password_hash
from sqlalchemy import text

def fix_admin_password():
    """Fix the admin user's password hash"""
    print("Fixing admin user password...")
    
    # New password hash
    password = "admin123"
    hashed_password = get_password_hash(password)
    
    print(f"Generated hash: {hashed_password}")
    
    try:
        with engine.connect() as conn:
            # Update the admin user's password
            result = conn.execute(text("""
                UPDATE users 
                SET hashed_password = :password, updated_at = datetime('now')
                WHERE username = 'admin'
            """), {"password": hashed_password})
            
            if result.rowcount > 0:
                conn.commit()
                print("✅ Admin password updated successfully!")
                print("📋 Login credentials:")
                print("   Username: admin")
                print("   Password: admin123")
            else:
                print("❌ Admin user not found!")
                
    except Exception as e:
        print(f"Error updating admin password: {e}")

if __name__ == "__main__":
    fix_admin_password()
