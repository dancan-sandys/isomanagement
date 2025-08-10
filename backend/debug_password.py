#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check password hash and test verification
"""
import sqlite3
import hashlib
import os

def debug_password():
    """Debug the current password hash"""
    print("Debugging password hash...")
    
    # Database path
    db_path = "iso22000_fsms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current password hash
        cursor.execute("SELECT hashed_password FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result:
            current_hash = result[0]
            print(f"Current hash in DB: {current_hash}")
            print(f"Hash length: {len(current_hash)}")
            
            # Test simple hash generation
            password = "admin123"
            test_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"Test hash for 'admin123': {test_hash}")
            print(f"Test hash length: {len(test_hash)}")
            
            # Test verification
            matches = (test_hash == current_hash)
            print(f"Hash matches: {matches}")
            
            # Update with correct hash if needed
            if not matches:
                print("Updating with correct hash...")
                cursor.execute("""
                    UPDATE users 
                    SET hashed_password = ?, updated_at = datetime('now')
                    WHERE username = 'admin'
                """, (test_hash,))
                conn.commit()
                print("✅ Password hash updated!")
            else:
                print("✅ Hash is correct!")
                
        else:
            print("❌ Admin user not found!")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_password()
