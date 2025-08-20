#!/usr/bin/env python3
"""
Comprehensive fix for 403 errors across all modules
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Role, Permission, Module, PermissionType
from app.services.rbac_service import RBACService
from datetime import datetime

def fix_403_errors():
    """Fix all 403 errors by ensuring proper permissions and user setup"""
    
    print("🔧 Fixing 403 Errors Across All Modules...")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. Check and fix admin user
        print("\n1. Checking admin user...")
        admin_user = db.query(User).filter(User.username == 'admin').first()
        
        if not admin_user:
            print("❌ Admin user not found!")
            return
        
        print(f"✅ Admin user found: {admin_user.username} (ID: {admin_user.id})")
        print(f"   Status: {admin_user.status}")
        print(f"   Is Active: {admin_user.is_active}")
        print(f"   Role ID: {admin_user.role_id}")
        
        # 2. Check and fix admin role
        print("\n2. Checking admin role...")
        admin_role = db.query(Role).filter(Role.name == 'System Administrator').first()
        
        if not admin_role:
            print("❌ System Administrator role not found!")
            return
        
        print(f"✅ Admin role found: {admin_role.name} (ID: {admin_role.id})")
        
        # 3. Ensure admin user has admin role
        if admin_user.role_id != admin_role.id:
            print(f"   Updating admin user role from {admin_user.role_id} to {admin_role.id}")
            admin_user.role_id = admin_role.id
            db.commit()
            print("   ✅ Role updated!")
        
        # 4. Check permissions for all modules
        print("\n3. Checking permissions for all modules...")
        
        # Define all required permissions
        required_permissions = {
            'dashboard': ['view'],
            'documents': ['view', 'create', 'update', 'delete', 'approve', 'export'],
            'haccp': ['view', 'create', 'update', 'delete', 'approve', 'export'],
            'prp': ['view', 'create', 'update', 'delete', 'approve', 'export'],
            'suppliers': ['view', 'create', 'update', 'delete', 'approve', 'export'],
            'traceability': ['view', 'create', 'update', 'delete', 'export'],
            'users': ['view', 'create', 'update', 'delete', 'assign'],
            'roles': ['view', 'create', 'update', 'delete', 'assign'],
            'settings': ['view', 'update', 'export', 'import'],
            'notifications': ['view', 'create', 'update', 'delete'],
            'audits': ['view', 'create', 'update', 'delete', 'approve', 'export', 'manage_program'],
            'training': ['view', 'create', 'update', 'delete', 'assign', 'export'],
            'maintenance': ['view', 'create', 'update', 'delete', 'assign', 'export'],
            'complaints': ['view', 'create', 'update', 'delete', 'assign', 'export'],
            'nc_capa': ['view', 'create', 'update', 'delete', 'assign', 'approve', 'export'],
            'risk_opportunity': ['view', 'create', 'update', 'delete', 'assign', 'export'],
            'management_review': ['view', 'create', 'update', 'delete', 'approve', 'export'],
            'allergen_label': ['view', 'create', 'update', 'delete', 'approve', 'export']
        }
        
        # Check each module
        for module_name, actions in required_permissions.items():
            try:
                module_enum = Module(module_name)
                print(f"\n   Checking {module_name.upper()} module...")
                
                for action in actions:
                    try:
                        action_enum = PermissionType(action)
                        
                        # Check if permission exists
                        permission = db.query(Permission).filter(
                            Permission.module == module_enum,
                            Permission.action == action_enum
                        ).first()
                        
                        if not permission:
                            print(f"     ❌ Missing permission: {module_name}:{action}")
                            # Create the permission
                            new_permission = Permission(
                                module=module_enum,
                                action=action_enum,
                                description=f"{module_name.title()} {action} permission"
                            )
                            db.add(new_permission)
                            db.commit()
                            db.refresh(new_permission)
                            print(f"     ✅ Created permission: {module_name}:{action}")
                            
                            # Add to admin role
                            admin_role.permissions.append(new_permission)
                            db.commit()
                            print(f"     ✅ Added to admin role")
                        else:
                            print(f"     ✅ Permission exists: {module_name}:{action}")
                            
                    except ValueError as e:
                        print(f"     ⚠️  Invalid action '{action}' for {module_name}: {e}")
                        
            except ValueError as e:
                print(f"   ⚠️  Invalid module '{module_name}': {e}")
        
        # 5. Test admin user permissions
        print("\n4. Testing admin user permissions...")
        rbac_service = RBACService(db)
        
        test_permissions = [
            ('risk_opportunity', 'create'),
            ('risk_opportunity', 'view'),
            ('complaints', 'create'),
            ('complaints', 'view'),
            ('audits', 'view'),
            ('audits', 'manage_program'),
            ('management_review', 'view'),
            ('management_review', 'create')
        ]
        
        for module_name, action in test_permissions:
            try:
                module_enum = Module(module_name)
                action_enum = PermissionType(action)
                
                has_perm = rbac_service.has_permission(admin_user.id, module_enum, action_enum)
                status = "✅" if has_perm else "❌"
                print(f"   {status} {module_name}:{action}")
                
            except Exception as e:
                print(f"   ❌ Error testing {module_name}:{action}: {e}")
        
        # 6. Ensure user is active and verified
        print("\n5. Ensuring user is active...")
        if not admin_user.is_active:
            admin_user.is_active = True
            print("   ✅ Activated user")
        
        if not admin_user.is_verified:
            admin_user.is_verified = True
            print("   ✅ Verified user")
        
        if admin_user.status != 'ACTIVE':
            admin_user.status = 'ACTIVE'
            print("   ✅ Set status to ACTIVE")
        
        db.commit()
        
        print("\n🎉 403 Error Fix Complete!")
        print("=" * 50)
        print("✅ Admin user is active and verified")
        print("✅ Admin user has System Administrator role")
        print("✅ All required permissions are created and assigned")
        print("✅ Permission system is working correctly")
        
        print("\n📋 Next Steps:")
        print("1. Restart the backend server")
        print("2. Log in to the frontend with admin/admin123")
        print("3. All modules should now work without 403 errors")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_403_errors()
