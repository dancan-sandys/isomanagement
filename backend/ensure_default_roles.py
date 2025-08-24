#!/usr/bin/env python3
"""
Script to ensure default roles exist in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.rbac import Role, Permission
from app.models.rbac import Module, PermissionType

def ensure_default_roles():
    """Ensure default roles exist in the database"""
    db = SessionLocal()
    try:
        print("Checking for default roles...")
        
        # Check if System Administrator role exists
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            print("Creating System Administrator role...")
            
            # Get all permissions
            all_permissions = db.query(Permission).all()
            if not all_permissions:
                print("No permissions found. Creating basic permissions...")
                # Create basic permissions
                for module in Module:
                    for action in PermissionType:
                        permission = Permission(
                            module=module,
                            action=action,
                            description=f"{action.value} permission for {module.value}"
                        )
                        db.add(permission)
                db.commit()
                all_permissions = db.query(Permission).all()
            
            # Create System Administrator role with all permissions
            admin_role = Role(
                name="System Administrator",
                description="Full access to all modules and user management",
                is_default=True,
                is_editable=False,
                is_active=True
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            
            # Assign all permissions to admin role
            admin_role.permissions = all_permissions
            db.commit()
            
            print("✅ System Administrator role created successfully")
        else:
            print("✅ System Administrator role already exists")
        
        # Check if QA Manager role exists
        qa_manager_role = db.query(Role).filter(Role.name == "QA Manager").first()
        if not qa_manager_role:
            print("Creating QA Manager role...")
            
            # Get permissions for QA Manager
            qa_permissions = db.query(Permission).filter(
                Permission.module.in_([
                    Module.DASHBOARD,
                    Module.DOCUMENTS,
                    Module.HACCP,
                    Module.PRP,
                    Module.AUDITS,
                    Module.NC_CAPA,
                    Module.SUPPLIERS,
                    Module.TRACEABILITY,
                    Module.TRAINING,
                    Module.COMPLAINTS
                ])
            ).all()
            
            qa_manager_role = Role(
                name="QA Manager",
                description="Manage documents, audits, HACCP, PRPs, CAPAs",
                is_default=True,
                is_editable=True,
                is_active=True
            )
            db.add(qa_manager_role)
            db.commit()
            db.refresh(qa_manager_role)
            
            # Assign permissions to QA Manager role
            qa_manager_role.permissions = qa_permissions
            db.commit()
            
            print("✅ QA Manager role created successfully")
        else:
            print("✅ QA Manager role already exists")
        
        # List all roles
        all_roles = db.query(Role).all()
        print(f"\n📋 Available roles ({len(all_roles)}):")
        for role in all_roles:
            print(f"  - {role.name} (Default: {role.is_default})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error ensuring default roles: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = ensure_default_roles()
    if success:
        print("\n✅ Default roles check completed successfully")
    else:
        print("\n❌ Default roles check failed")
        sys.exit(1)
