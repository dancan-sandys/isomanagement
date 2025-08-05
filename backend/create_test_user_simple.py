#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to create a test user for frontend development
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from app.core.security import get_password_hash
from sqlalchemy import text

def create_test_user_simple():
    """Create a test admin user"""
    print("Creating test admin user...")
    
    # Hash the password
    password = "admin123"
    hashed_password = get_password_hash(password)
    
    try:
        with engine.connect() as conn:
            # First, get the System Administrator role ID
            result = conn.execute(text("SELECT id FROM roles WHERE name = 'System Administrator'"))
            role = result.fetchone()
            
            if not role:
                print("❌ System Administrator role not found!")
                return
            
            role_id = role[0]
            
            # Check if user already exists
            result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            existing_user = result.fetchone()
            
            if existing_user:
                print("⏭️  Admin user already exists")
                return
            
            # Create the admin user
            conn.execute(text("""
                INSERT INTO users (
                    username, email, full_name, hashed_password, 
                    role_id, status, department, position, 
                    is_active, is_verified, created_at, updated_at
                ) VALUES (
                    'admin', 'admin@iso22000.com', 'System Administrator', :password,
                    :role_id, 'ACTIVE', 'Quality Assurance', 'System Administrator',
                    true, true, datetime('now'), datetime('now')
                )
            """), {"password": hashed_password, "role_id": role_id})
            
            conn.commit()
            print("✅ Test user created successfully!")
            print("📋 Login credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Role: System Administrator (Full access)")
            
    except Exception as e:
        print("Error creating test user: {}".format(e))

if __name__ == "__main__":
    create_test_user_simple() 