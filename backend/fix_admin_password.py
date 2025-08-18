#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix admin user password
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.user import User
from app.core.security import get_password_hash

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_admin_password():
    """Fix admin user password"""
    print("Fixing admin user password...")
    
    db = SessionLocal()
    try:
        # Find admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ Admin user not found!")
            return
        
        print(f"Found admin user: {admin_user.username}")
        print(f"Current email: {admin_user.email}")
        
        # Update password
        new_password = "admin123"
        new_hash = get_password_hash(new_password)
        
        admin_user.hashed_password = new_hash
        admin_user.email = "admin@iso22000.com"  # Update email to match expected
        
        db.commit()
        
        print("✅ Admin password updated successfully!")
        print(f"Username: admin")
        print(f"Password: {new_password}")
        print(f"Email: {admin_user.email}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_password()
