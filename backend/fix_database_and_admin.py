#!/usr/bin/env python3
"""
Simple script to fix database and create admin user
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User, UserStatus
from app.models.rbac import Role, Permission
from app.core.security import get_password_hash
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_database():
    """Fix database and create admin user"""
    print("🔧 Fixing database and creating admin user...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("✓ Admin user already exists")
            return
        
        # Create System Administrator role if it doesn't exist
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            admin_role = Role(
                name="System Administrator",
                description="Full access to all modules and user management",
                is_default=True,
                is_editable=False
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✓ Created System Administrator role")
        
        # Create admin user with correct field names
        admin_user = User(
            username="admin",
            email="admin@iso22000.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role_id=admin_role.id,
            status=UserStatus.ACTIVE,
            department_name="Quality Assurance",  # Use department_name instead of department
            position="System Administrator",
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✓ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Role: System Administrator")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_database()
