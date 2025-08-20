#!/usr/bin/env python3
"""
Comprehensive script to initialize the database with all required roles, permissions, and users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.rbac import Role, Permission, UserPermission
from app.models.user import User, UserStatus
from app.core.security import get_password_hash
from app.models.rbac import Module, PermissionType
from datetime import datetime

def create_permissions():
    """Create all permissions for the system"""
    print("🔐 Creating permissions...")
    
    db = SessionLocal()
    try:
        # Check if permissions already exist
        existing_permissions = db.query(Permission).count()
        if existing_permissions > 0:
            print(f"Found {existing_permissions} existing permissions. Skipping creation.")
            return
        
        # Create permissions for all modules and actions
        permissions = []
        for module in Module:
            for action in PermissionType:
                permission = Permission(
                    module=module,
                    action=action,
                    description=f"{action.value.title()} permission for {module.value}"
                )
                permissions.append(permission)
        
        db.add_all(permissions)
        db.commit()
        print(f"✅ Created {len(permissions)} permissions")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating permissions: {e}")
        raise
    finally:
        db.close()

def create_default_roles():
    """Create default roles with appropriate permissions"""
    print("👥 Creating default roles...")
    
    db = SessionLocal()
    try:
        # Get all permissions
        all_permissions = db.query(Permission).all()
        permissions_dict = {(p.module, p.action): p for p in all_permissions}
        
        # Define default roles and their permissions
        roles_data = [
            {
                "name": "System Administrator",
                "description": "Full access to all modules and user management",
                "is_default": True,
                "is_editable": False,
                "permissions": [(module, action) for module in Module for action in PermissionType]
            },
            {
                "name": "QA Manager",
                "description": "Quality Assurance management and oversight",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.CREATE),
                    (Module.HACCP, PermissionType.UPDATE),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.CREATE),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.SUPPLIERS, PermissionType.CREATE),
                    (Module.SUPPLIERS, PermissionType.UPDATE),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.CREATE),
                    (Module.DOCUMENTS, PermissionType.UPDATE),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.CREATE),
                    (Module.AUDITS, PermissionType.UPDATE),
                    (Module.COMPLAINTS, PermissionType.VIEW),
                    (Module.COMPLAINTS, PermissionType.CREATE),
                    (Module.COMPLAINTS, PermissionType.UPDATE),
                    (Module.NONCONFORMANCE, PermissionType.VIEW),
                    (Module.NONCONFORMANCE, PermissionType.CREATE),
                    (Module.NONCONFORMANCE, PermissionType.UPDATE),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.CREATE),
                    (Module.EQUIPMENT, PermissionType.UPDATE),
                    (Module.ALLERGEN_LABEL, PermissionType.VIEW),
                    (Module.ALLERGEN_LABEL, PermissionType.CREATE),
                    (Module.ALLERGEN_LABEL, PermissionType.UPDATE),
                    (Module.MANAGEMENT_REVIEW, PermissionType.VIEW),
                    (Module.MANAGEMENT_REVIEW, PermissionType.CREATE),
                    (Module.MANAGEMENT_REVIEW, PermissionType.UPDATE),
                    (Module.RISK, PermissionType.VIEW),
                    (Module.RISK, PermissionType.CREATE),
                    (Module.RISK, PermissionType.UPDATE),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.CREATE),
                    (Module.TRACEABILITY, PermissionType.UPDATE),
                ]
            },
            {
                "name": "Production Manager",
                "description": "Production operations and management",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.CREATE),
                    (Module.EQUIPMENT, PermissionType.UPDATE),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.CREATE),
                    (Module.TRACEABILITY, PermissionType.UPDATE),
                ]
            },
            {
                "name": "Line Operator",
                "description": "Basic operational access",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                ]
            }
        ]
        
        # Create roles
        for role_data in roles_data:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if existing_role:
                print(f"⏭️  Role already exists: {role_data['name']}")
                continue
            
            # Create role
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                is_default=role_data["is_default"],
                is_editable=role_data["is_editable"],
                is_active=True
            )
            
            # Add permissions
            role_permissions = []
            for module, action in role_data["permissions"]:
                permission = permissions_dict.get((module, action))
                if permission:
                    role_permissions.append(permission)
            
            role.permissions = role_permissions
            db.add(role)
            print(f"✅ Created role: {role_data['name']} with {len(role_permissions)} permissions")
        
        db.commit()
        print("✅ All default roles created successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating roles: {e}")
        raise
    finally:
        db.close()

def create_admin_user():
    """Create the default admin user"""
    print("👤 Creating admin user...")
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("⏭️  Admin user already exists")
            return
        
        # Get System Administrator role
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            print("❌ System Administrator role not found!")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@iso22000.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role_id=admin_role.id,
            status=UserStatus.ACTIVE,
            department="Quality Assurance",
            position="System Administrator",
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Role: System Administrator")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()

def main():
    """Main function to initialize the database"""
    print("🚀 Starting comprehensive database initialization...")
    
    try:
        # Create all tables first
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Create permissions
        create_permissions()
        
        # Create roles
        create_default_roles()
        
        # Create admin user
        create_admin_user()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n📋 Summary:")
        print("  - Database tables created")
        print("  - Permissions created")
        print("  - Default roles created")
        print("  - Admin user created")
        print("\n🔑 Login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: System Administrator")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
