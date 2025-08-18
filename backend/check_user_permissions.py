#!/usr/bin/env python3
"""
Check user permissions to debug 403 errors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Module, PermissionType
from app.services.rbac_service import RBACService

def check_user_permissions():
    """Check permissions for all users"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        
        print("🔍 Checking user permissions...")
        print("=" * 80)
        
        for user in users:
            print(f"\n👤 User: {user.username} (ID: {user.id})")
            print(f"   Role: {user.role.name if user.role else 'No role'}")
            print(f"   Active: {user.is_active}")
            
            rbac_service = RBACService(db)
            user_permissions = rbac_service.get_user_permissions(user.id)
            user_modules = rbac_service.get_user_modules(user.id)
            
            print(f"   Modules: {[m.value for m in user_modules]}")
            print(f"   Permissions: {len(user_permissions)} total")
            
            # Check specific permissions for problematic modules
            problematic_modules = ['complaints', 'maintenance', 'risk_opportunity', 'management_review']
            
            for module_name in problematic_modules:
                try:
                    module_enum = Module(module_name)
                    has_view = rbac_service.has_permission(user.id, module_enum, PermissionType.VIEW)
                    has_create = rbac_service.has_permission(user.id, module_enum, PermissionType.CREATE)
                    has_update = rbac_service.has_permission(user.id, module_enum, PermissionType.UPDATE)
                    
                    print(f"   {module_name.upper()}: VIEW={has_view}, CREATE={has_create}, UPDATE={has_update}")
                except ValueError:
                    print(f"   {module_name.upper()}: Invalid module")
            
            # Show first 10 permissions
            if user_permissions:
                print("   Sample permissions:")
                for perm in user_permissions[:10]:
                    print(f"     - {perm.module.value}:{perm.action.value}")
                if len(user_permissions) > 10:
                    print(f"     ... and {len(user_permissions) - 10} more")
            else:
                print("   No permissions assigned!")
            
            print("-" * 80)
        
        print("\n🔧 Recommendations:")
        print("1. Check if users have the correct roles assigned")
        print("2. Verify that roles have the required permissions")
        print("3. Check if the RBAC seed data was run properly")
        print("4. Ensure users have access to: complaints, maintenance, risk_opportunity, management_review")
        
    except Exception as e:
        print(f"❌ Error checking user permissions: {e}")
    finally:
        db.close()

def check_specific_user(username: str):
    """Check permissions for a specific user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        print(f"🔍 Checking permissions for user: {username}")
        print("=" * 60)
        print(f"User ID: {user.id}")
        print(f"Role: {user.role.name if user.role else 'No role'}")
        print(f"Active: {user.is_active}")
        
        rbac_service = RBACService(db)
        user_permissions = rbac_service.get_user_permissions(user.id)
        user_modules = rbac_service.get_user_modules(user.id)
        
        print(f"\nModules with access: {[m.value for m in user_modules]}")
        print(f"Total permissions: {len(user_permissions)}")
        
        # Check specific permissions
        modules_to_check = [
            Module.COMPLAINTS,
            Module.MAINTENANCE, 
            Module.RISK_OPPORTUNITY,
            Module.MANAGEMENT_REVIEW
        ]
        
        print("\nDetailed permission check:")
        for module in modules_to_check:
            print(f"\n{module.value.upper()}:")
            for action in PermissionType:
                has_perm = rbac_service.has_permission(user.id, module, action)
                print(f"  {action.value}: {'✅' if has_perm else '❌'}")
        
        print(f"\nAll permissions for {username}:")
        for perm in user_permissions:
            print(f"  - {perm.module.value}:{perm.action.value}")
        
    except Exception as e:
        print(f"❌ Error checking user permissions: {e}")
    finally:
        db.close()

def check_rbac_data():
    """Check if RBAC data exists"""
    db = SessionLocal()
    try:
        from app.models.rbac import Role, Permission, UserPermission
        
        roles_count = db.query(Role).count()
        permissions_count = db.query(Permission).count()
        user_permissions_count = db.query(UserPermission).count()
        
        print("🔍 RBAC Data Check:")
        print(f"   Roles: {roles_count}")
        print(f"   Permissions: {permissions_count}")
        print(f"   User Permissions: {user_permissions_count}")
        
        if roles_count == 0 or permissions_count == 0:
            print("\n❌ RBAC data is missing! Need to run RBAC seed data.")
            return False
        
        # Check specific permissions for problematic modules
        problematic_modules = ['complaints', 'maintenance', 'risk_opportunity', 'management_review']
        
        print("\n🔍 Checking permissions for problematic modules:")
        for module_name in problematic_modules:
            try:
                module_enum = Module(module_name)
                module_permissions = db.query(Permission).filter(Permission.module == module_enum).all()
                print(f"   {module_name.upper()}: {len(module_permissions)} permissions")
                for perm in module_permissions:
                    print(f"     - {perm.action.value}")
            except ValueError:
                print(f"   {module_name.upper()}: Invalid module")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking RBAC data: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "rbac":
            check_rbac_data()
        else:
            username = sys.argv[1]
            check_specific_user(username)
    else:
        check_user_permissions()
        print("\n" + "="*80)
        check_rbac_data()
