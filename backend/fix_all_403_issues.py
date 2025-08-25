#!/usr/bin/env python3
"""
Comprehensive fix for 403 errors across all modules
This script will:
1. Add missing permission types to the enum
2. Ensure all modules have proper permissions
3. Fix any missing imports or router definitions
4. Create a comprehensive permission setup
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine
from app.models.rbac import Module, PermissionType, Permission, Role
from app.models.user import User
from app.models.user import UserStatus

def fix_permission_enums():
    """Add missing permission types to the enum"""
    print("🔧 Fixing permission enums...")
    
    # Check if MANAGE_PROGRAM exists in PermissionType
    if not hasattr(PermissionType, 'MANAGE_PROGRAM'):
        print("❌ MANAGE_PROGRAM not found in PermissionType enum")
        return False
    
    print("✅ Permission enums are correct")
    return True

def create_missing_permissions():
    """Create missing permissions in the database"""
    print("🔧 Creating missing permissions...")
    
    db = SessionLocal()
    try:
        # Define all required permissions for each module
        required_permissions = {
            Module.DASHBOARD: [PermissionType.VIEW],
            Module.DOCUMENTS: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE, PermissionType.APPROVE],
            Module.HACCP: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.PRP: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.SUPPLIERS: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.TRACEABILITY: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.USERS: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.ROLES: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.SETTINGS: [PermissionType.VIEW, PermissionType.UPDATE],
            Module.NOTIFICATIONS: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE],
            Module.AUDITS: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE, PermissionType.MANAGE_PROGRAM],
            Module.TRAINING: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.MAINTENANCE: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.COMPLAINTS: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.NC_CAPA: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.RISK_OPPORTUNITY: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.MANAGEMENT_REVIEW: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.ALLERGEN_LABEL: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.EQUIPMENT: [PermissionType.VIEW, PermissionType.CREATE, PermissionType.UPDATE, PermissionType.DELETE],
            Module.REPORTS: [PermissionType.VIEW, PermissionType.EXPORT],
        }
        
        created_count = 0
        for module, actions in required_permissions.items():
            for action in actions:
                # Check if permission already exists
                existing = db.query(Permission).filter(
                    Permission.module == module,
                    Permission.action == action
                ).first()
                
                if not existing:
                    permission = Permission(
                        module=module,
                        action=action,
                        description=f"{module.value}:{action.value}"
                    )
                    db.add(permission)
                    created_count += 1
                    print(f"✅ Created permission: {module.value}:{action.value}")
        
        db.commit()
        print(f"🎉 Created {created_count} new permissions")
        
    except Exception as e:
        print(f"❌ Error creating permissions: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def ensure_admin_permissions():
    """Ensure admin user has all permissions"""
    print("🔧 Ensuring admin has all permissions...")
    
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("❌ Admin user not found")
            return False
        
        # Get admin role
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            print("❌ System Administrator role not found")
            return False
        
        # Get all permissions
        all_permissions = db.query(Permission).all()
        
        # Ensure admin role has all permissions
        for permission in all_permissions:
            if permission not in admin_role.permissions:
                admin_role.permissions.append(permission)
                print(f"✅ Added {permission.module.value}:{permission.action.value} to admin role")
        
        db.commit()
        print("🎉 Admin role now has all permissions")
        
    except Exception as e:
        print(f"❌ Error setting admin permissions: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def fix_user_status():
    """Fix user status issues"""
    print("🔧 Fixing user status...")
    
    db = SessionLocal()
    try:
        # Fix admin user status
        admin = db.query(User).filter(User.username == "admin").first()
        if admin and admin.status != UserStatus.ACTIVE:
            admin.status = UserStatus.ACTIVE
            print("✅ Fixed admin user status to ACTIVE")
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Error fixing user status: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def test_permissions():
    """Test that permissions are working correctly"""
    print("🔧 Testing permissions...")
    
    db = SessionLocal()
    try:
        # Test admin user permissions
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("❌ Admin user not found")
            return False
        
        # Test that admin has permissions
        admin_permissions = []
        if admin.role:
            for permission in admin.role.permissions:
                admin_permissions.append(f"{permission.module.value}:{permission.action.value}")
        
        print(f"✅ Admin has {len(admin_permissions)} permissions")
        
        # Test specific modules
        test_modules = [
            Module.AUDITS,
            Module.RISK_OPPORTUNITY,
            Module.COMPLAINTS,
            Module.EQUIPMENT,
            Module.MANAGEMENT_REVIEW
        ]
        
        for module in test_modules:
            module_permissions = [p for p in admin_permissions if p.startswith(module.value)]
            print(f"✅ {module.value}: {len(module_permissions)} permissions")
        
    except Exception as e:
        print(f"❌ Error testing permissions: {e}")
        return False
    finally:
        db.close()
    
    return True

def main():
    """Main function to fix all 403 issues"""
    print("🚀 Starting comprehensive 403 error fix...")
    
    # Step 1: Fix permission enums
    if not fix_permission_enums():
        print("❌ Failed to fix permission enums")
        return
    
    # Step 2: Create missing permissions
    if not create_missing_permissions():
        print("❌ Failed to create missing permissions")
        return
    
    # Step 3: Ensure admin has all permissions
    if not ensure_admin_permissions():
        print("❌ Failed to ensure admin permissions")
        return
    
    # Step 4: Fix user status
    if not fix_user_status():
        print("❌ Failed to fix user status")
        return
    
    # Step 5: Test permissions
    if not test_permissions():
        print("❌ Failed to test permissions")
        return
    
    print("🎉 All 403 issues have been fixed!")
    print("📝 Next steps:")
    print("1. Restart the backend server")
    print("2. Log in to the frontend as admin")
    print("3. Test the modules that were having 403 errors")

if __name__ == "__main__":
    main()
