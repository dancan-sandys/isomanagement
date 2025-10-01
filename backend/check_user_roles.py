#!/usr/bin/env python3
"""
Script to check user roles and permissions in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Role, Permission, role_permissions
from sqlalchemy import text

def check_user_roles():
    """Check user roles and permissions"""
    db = SessionLocal()
    try:
        # Check admin user
        admin_user = db.query(User).filter(User.username == 'admin').first()
        if admin_user:
            print(f'Admin user found:')
            print(f'  Username: {admin_user.username}')
            print(f'  Role ID: {admin_user.role_id}')
            if admin_user.role:
                print(f'  Role Name: "{admin_user.role.name}"')
            else:
                print(f'  Role: Not found (role_id={admin_user.role_id})')
        
        # Check all roles
        print(f'\nAll roles in database:')
        roles = db.query(Role).all()
        for role in roles:
            print(f'  ID: {role.id}, Name: "{role.name}"')
            
        # Check if admin user's role_id matches any role
        if admin_user and admin_user.role_id:
            matching_role = db.query(Role).filter(Role.id == admin_user.role_id).first()
            if matching_role:
                print(f'\n✅ Admin user role matches: "{matching_role.name}"')
                
                # Check role permissions
                role_perms = db.execute(text("SELECT COUNT(*) FROM role_permissions WHERE role_id = :role_id"), 
                                      {"role_id": admin_user.role_id}).scalar()
                print(f'  Role has {role_perms} permissions assigned')
                
                # Check a few specific permissions
                permissions = db.query(Permission).limit(10).all()
                print(f'\nSample permissions:')
                for perm in permissions:
                    print(f'  - {perm.module}:{perm.action} (ID: {perm.id})')
                    
            else:
                print(f'\n❌ Admin user role_id {admin_user.role_id} does not match any role')
                
        # Check total permissions
        total_permissions = db.query(Permission).count()
        print(f'\nTotal permissions in database: {total_permissions}')
        
    finally:
        db.close()

if __name__ == "__main__":
    check_user_roles()
