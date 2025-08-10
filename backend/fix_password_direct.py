#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct password fix script - no app imports needed
"""
import sqlite3
import bcrypt
import os

def fix_admin_password_direct():
    """Fix admin password directly using bcrypt"""
    print("Fixing admin password directly...")
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    # Generate new password hash
    password = "admin123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    hashed_str = hashed.decode('utf-8')
    
    print(f"Generated hash: {hashed_str}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update admin user password
        cursor.execute("""
            UPDATE users 
            SET hashed_password = ?, updated_at = datetime('now')
            WHERE username = 'admin'
        """, (hashed_str,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Admin password updated successfully!")
            print("📋 Login credentials:")
            print("   Username: admin")
            print("   Password: admin123")
        else:
            print("❌ Admin user not found!")
            
        conn.close()
        
    except Exception as e:
        print(f"Error updating password: {e}")

if __name__ == "__main__":
    fix_admin_password_direct()
