#!/usr/bin/env python3
"""
Script to create a test user for frontend development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def create_test_user():
    """Create a test user for development"""
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("Test user 'admin' already exists!")
            return
        
        # Create test user
        test_user = User(
            username="admin",
            email="admin@iso22000.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            department="Quality Assurance",
            position="System Administrator",
            is_active=True,
            is_verified=True
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Test user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Role: ADMIN")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 