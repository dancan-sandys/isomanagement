#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check users in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.user import User
from app.core.security import verify_password, get_password_hash

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_users():
    """Check all users in the database"""
    print("Checking users in database...")
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        print(f"Found {len(users)} users:")
        print("-" * 80)
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"Role: {user.role.name if user.role else 'None'}")
            print(f"Active: {user.is_active}")
            print(f"Verified: {user.is_verified}")
            print(f"Status: {user.status}")
            print(f"Department: {user.department}")
            print(f"Position: {user.position}")
            print(f"Created: {user.created_at}")
            print(f"Last Login: {user.last_login}")
            print("-" * 80)
            
            # Test password verification
            if user.username == "admin":
                print("Testing admin password...")
                test_password = "admin123"
                is_valid = verify_password(test_password, user.hashed_password)
                print(f"Password 'admin123' valid: {is_valid}")
                
                # Create new hash for comparison
                new_hash = get_password_hash(test_password)
                print(f"New hash for 'admin123': {new_hash[:50]}...")
                print(f"Original hash: {user.hashed_password[:50]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()

