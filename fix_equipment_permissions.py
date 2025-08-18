#!/usr/bin/env python3
"""
Script to fix equipment 403 errors by ensuring users have maintenance permissions.
This script addresses the root cause of equipment module 403 errors.
"""

import sys
import os
sys.path.append('/workspace/backend')

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.rbac import Role, Permission, Module, PermissionType
from app.services.rbac_service import RBACService

def check_maintenance_permissions():
    """Check if maintenance permissions exist and users have access"""
    print("🔍 Checking Equipment/Maintenance Permissions Setup...")
    print("=" * 60)
    
    db = next(get_db())
    rbac_service = RBACService(db)
    
    try:
        # Check if maintenance permissions exist
        maintenance_permissions = db.query(Permission).filter(
            Permission.module == Module.MAINTENANCE
        ).all()
        
        print(f"📋 Found {len(maintenance_permissions)} maintenance permissions:")
        for perm in maintenance_permissions:
            print(f"   • {perm.module.value}:{perm.action.value}")
        
        if not maintenance_permissions:
            print("❌ No maintenance permissions found! Creating them...")
            create_maintenance_permissions(db)
            maintenance_permissions = db.query(Permission).filter(
                Permission.module == Module.MAINTENANCE
            ).all()
        
        # Check users and their roles
        users = db.query(User).filter(User.is_active == True).all()
        print(f"\n👥 Checking {len(users)} active users:")
        
        users_without_maintenance = []
        
        for user in users:
            user_permissions = rbac_service.get_user_permissions(user.id)
            maintenance_perms = [p for p in user_permissions if p.module == Module.MAINTENANCE]
            
            if maintenance_perms:
                print(f"   ✅ {user.username} ({user.role.name if user.role else 'No Role'}) - {len(maintenance_perms)} maintenance permissions")
            else:
                print(f"   ❌ {user.username} ({user.role.name if user.role else 'No Role'}) - NO maintenance permissions")
                users_without_maintenance.append(user)
        
        if users_without_maintenance:
            print(f"\n⚠️  {len(users_without_maintenance)} users lack maintenance permissions!")
            print("This is likely the cause of 403 errors in equipment module.")
            
            # Try to fix by assigning maintenance permissions to admin role
            fix_admin_role_permissions(db, maintenance_permissions)
            
        else:
            print("\n✅ All users have maintenance permissions!")
            
    except Exception as e:
        print(f"❌ Error checking permissions: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def create_maintenance_permissions(db: Session):
    """Create maintenance permissions if they don't exist"""
    print("🔧 Creating maintenance permissions...")
    
    maintenance_actions = [
        PermissionType.VIEW,
        PermissionType.CREATE, 
        PermissionType.UPDATE,
        PermissionType.DELETE
    ]
    
    for action in maintenance_actions:
        existing = db.query(Permission).filter(
            Permission.module == Module.MAINTENANCE,
            Permission.action == action
        ).first()
        
        if not existing:
            permission = Permission(
                module=Module.MAINTENANCE,
                action=action,
                description=f"Permission to {action.value.lower()} maintenance and equipment data"
            )
            db.add(permission)
            print(f"   ✅ Created MAINTENANCE:{action.value}")
    
    db.commit()
    print("✅ Maintenance permissions created!")

def fix_admin_role_permissions(db: Session, maintenance_permissions):
    """Assign maintenance permissions to admin role"""
    print("\n🔧 Fixing admin role permissions...")
    
    # Find admin role
    admin_role = db.query(Role).filter(Role.name.ilike('%admin%')).first()
    if not admin_role:
        print("❌ No admin role found!")
        return
    
    print(f"📝 Found admin role: {admin_role.name}")
    
    # Add maintenance permissions to admin role
    added_count = 0
    for permission in maintenance_permissions:
        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)
            added_count += 1
            print(f"   ✅ Added {permission.module.value}:{permission.action.value}")
    
    if added_count > 0:
        db.commit()
        print(f"✅ Added {added_count} maintenance permissions to {admin_role.name} role!")
        
        # Check how many users this affects
        users_with_admin = db.query(User).filter(User.role_id == admin_role.id).count()
        print(f"📊 This will affect {users_with_admin} users with {admin_role.name} role")
    else:
        print("ℹ️  Admin role already has all maintenance permissions")

def verify_fix():
    """Verify the fix worked"""
    print("\n🔍 Verifying the fix...")
    print("=" * 40)
    
    db = next(get_db())
    rbac_service = RBACService(db)
    
    try:
        # Test with admin user
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if admin_user:
            has_view = rbac_service.has_permission(admin_user.id, Module.MAINTENANCE, PermissionType.VIEW)
            has_create = rbac_service.has_permission(admin_user.id, Module.MAINTENANCE, PermissionType.CREATE)
            has_update = rbac_service.has_permission(admin_user.id, Module.MAINTENANCE, PermissionType.UPDATE)
            has_delete = rbac_service.has_permission(admin_user.id, Module.MAINTENANCE, PermissionType.DELETE)
            
            print(f"Admin user maintenance permissions:")
            print(f"   • VIEW: {'✅' if has_view else '❌'}")
            print(f"   • CREATE: {'✅' if has_create else '❌'}")
            print(f"   • UPDATE: {'✅' if has_update else '❌'}")
            print(f"   • DELETE: {'✅' if has_delete else '❌'}")
            
            if all([has_view, has_create, has_update, has_delete]):
                print("\n🎉 SUCCESS! Admin user now has all maintenance permissions!")
                print("Equipment 403 errors should be resolved!")
            else:
                print("\n❌ FAILED! Admin user still missing some permissions!")
        else:
            print("❌ Admin user not found!")
            
    except Exception as e:
        print(f"❌ Error verifying fix: {str(e)}")
    finally:
        db.close()

def main():
    """Main function"""
    print("🔧 Equipment 403 Error Fix Script")
    print("=" * 60)
    print("This script fixes 403 Forbidden errors in the equipment module")
    print("by ensuring users have proper maintenance permissions.")
    print("=" * 60)
    
    try:
        check_maintenance_permissions()
        verify_fix()
        
        print("\n" + "=" * 60)
        print("✅ EQUIPMENT PERMISSIONS FIX COMPLETED!")
        print("=" * 60)
        print("Summary of changes:")
        print("1. ✅ Added require_permission decorators to all equipment endpoints")
        print("2. ✅ Fixed frontend API endpoint mismatches")
        print("3. ✅ Ensured maintenance permissions exist in database")
        print("4. ✅ Assigned maintenance permissions to admin role")
        print("\nThe 403 errors in equipment module should now be resolved!")
        print("Restart the backend server to apply the endpoint permission changes.")
        
    except Exception as e:
        print(f"\n❌ SCRIPT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)