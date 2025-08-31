#!/usr/bin/env python3
"""
Quick fix for the missing roles issue in signup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.rbac import Role, Permission, Module, PermissionType

def fix_roles_issue():
    """Create default roles if they don't exist"""
    print("🔧 Fixing missing roles issue...")
    
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        print(f"📊 Found {existing_roles} existing roles")
        
        if existing_roles > 0:
            print("✅ Roles already exist. No fix needed.")
            return
        
        print("⚠️  No roles found. Creating default roles...")
        
        # Create System Administrator role
        admin_role = Role(
            name="System Administrator",
            description="Full access to all modules and user management",
            is_default=True,
            is_editable=False,
            is_active=True
        )
        db.add(admin_role)
        
        # Create QA Manager role
        qa_role = Role(
            name="QA Manager",
            description="Quality Assurance management and oversight",
            is_default=True,
            is_editable=True,
            is_active=True
        )
        db.add(qa_role)
        
        # Create Viewer role
        viewer_role = Role(
            name="Viewer",
            description="Read-only access to most modules",
            is_default=True,
            is_editable=True,
            is_active=True
        )
        db.add(viewer_role)
        
        db.commit()
        print("✅ Default roles created successfully!")
        print("   - System Administrator")
        print("   - QA Manager") 
        print("   - Viewer")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating roles: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_roles_issue()
