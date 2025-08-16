#!/usr/bin/env python3
"""
Script to create an admin user for the ISO 22000 FSMS system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User, UserStatus
from app.models.rbac import Role
from app.core.security import get_password_hash
from datetime import datetime

def create_admin_user():
    """Create an admin user for the system"""
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("✅ Admin user 'admin' already exists!")
            print(f"Username: {existing_user.username}")
            print(f"Email: {existing_user.email}")
            print(f"Role: {existing_user.role.name if existing_user.role else 'Unknown'}")
            return
        
        # Get the System Administrator role
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            print("❌ Error: 'System Administrator' role not found!")
            print("Available roles:")
            roles = db.query(Role).all()
            for role in roles:
                print(f"  - {role.name}")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@iso22000.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role_id=admin_role.id,
            status=UserStatus.ACTIVE,
            department="IT",
            position="System Administrator",
            phone="+1234567890",
            employee_id="EMP001",
            is_active=True,
            is_verified=True,
            last_login=datetime.now()
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print(f"Role: {admin_role.name}")
        print("Email: admin@iso22000.com")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

