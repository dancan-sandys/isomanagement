#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple password fix script using basic hashing
"""
import sqlite3
import hashlib
import os

def fix_admin_password_simple():
    """Fix admin password using simple hash"""
    print("Fixing admin password with simple hash...")
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    # Generate simple hash (temporary fix)
    password = "admin123"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"Generated hash: {hashed}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update admin user password
        cursor.execute("""
            UPDATE users 
            SET hashed_password = ?, updated_at = datetime('now')
            WHERE username = 'admin'
        """, (hashed,))
        
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
    fix_admin_password_simple()
