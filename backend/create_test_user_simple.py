#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to create a test user for frontend development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_test_user_simple():
    """Create a test user using raw SQL"""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if user already exists
            result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            if result.fetchone():
                print("Test user 'admin' already exists!")
                return
            
            # Create test user with hashed password (admin123)
            # This is a bcrypt hash of "admin123"
            hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO"
            
            conn.execute(text("""
                INSERT INTO users (
                    username, email, full_name, hashed_password, 
                    role, status, department, position, 
                    is_active, is_verified, created_at, updated_at
                ) VALUES (
                    'admin', 'admin@iso22000.com', 'System Administrator', :password,
                    'admin', 'active', 'Quality Assurance', 'System Administrator',
                    true, true, datetime('now'), datetime('now')
                )
            """), {"password": hashed_password})
            
            conn.commit()
            
            print("Test user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("Role: admin")
            
    except Exception as e:
        print("Error creating test user: {}".format(e))

if __name__ == "__main__":
    create_test_user_simple() 