#!/usr/bin/env python3
"""
Script to add equipment permissions to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.rbac import Permission, Module, PermissionType

def add_equipment_permissions():
    """Add equipment permissions to the database"""
    db = SessionLocal()
    try:
        # Check if equipment permissions already exist
        existing_permissions = db.query(Permission).filter(Permission.module == Module.EQUIPMENT).all()
        if existing_permissions:
            print(f"Equipment permissions already exist: {len(existing_permissions)} found")
            for perm in existing_permissions:
                print(f"  - {perm.module.value}:{perm.action.value}")
            return
        
        # Create equipment permissions
        equipment_permissions = [
            Permission(module=Module.EQUIPMENT, action=PermissionType.VIEW, description="View equipment"),
            Permission(module=Module.EQUIPMENT, action=PermissionType.CREATE, description="Create equipment"),
            Permission(module=Module.EQUIPMENT, action=PermissionType.UPDATE, description="Update equipment"),
            Permission(module=Module.EQUIPMENT, action=PermissionType.DELETE, description="Delete equipment"),
            Permission(module=Module.EQUIPMENT, action=PermissionType.APPROVE, description="Approve equipment"),
            Permission(module=Module.EQUIPMENT, action=PermissionType.EXPORT, description="Export equipment data"),
        ]
        
        db.add_all(equipment_permissions)
        db.commit()
        
        print(f"Successfully added {len(equipment_permissions)} equipment permissions:")
        for perm in equipment_permissions:
            print(f"  - {perm.module.value}:{perm.action.value}")
            
        # Assign equipment permissions to admin role
        from app.models.user import User
        from app.models.rbac import Role
        
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if admin_role:
            # Get the permissions we just created
            equipment_perms = db.query(Permission).filter(Permission.module == Module.EQUIPMENT).all()
            admin_role.permissions.extend(equipment_perms)
            db.commit()
            print(f"Assigned {len(equipment_perms)} equipment permissions to System Administrator role")
        else:
            print("Warning: System Administrator role not found")
            
    except Exception as e:
        db.rollback()
        print(f"Error adding equipment permissions: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_equipment_permissions()


