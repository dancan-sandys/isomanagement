#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check and fix user permissions for risk access
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.rbac import Role, Permission, Module, PermissionType
from app.models.user import User

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user_permissions():
    """Check user permissions and fix risk access issues"""
    print("Checking user permissions for risk access...")
    
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        
        # Get risk permissions
        risk_permissions = db.query(Permission).filter(
            Permission.module == Module.RISK_OPPORTUNITY
        ).all()
        
        print(f"Found {len(risk_permissions)} risk permissions:")
        for perm in risk_permissions:
            print(f"  - {perm.module.value}:{perm.action.value}")
        
        print(f"\nChecking {len(users)} users...")
        
        for user in users:
            print(f"\nUser: {user.username} (ID: {user.id})")
            print(f"  Role: {user.role.name if user.role else 'None'}")
            print(f"  Active: {user.is_active}")
            
            if not user.role:
                print("  ❌ No role assigned - this will cause 403 errors")
                continue
            
            # Check role permissions
            role_permissions = user.role.permissions
            risk_perms = [p for p in role_permissions if p.module == Module.RISK_OPPORTUNITY]
            
            if not risk_perms:
                print("  ❌ No risk permissions in role")
                print("  🔧 Adding risk permissions to role...")
                
                # Add risk permissions to the role
                for perm in risk_permissions:
                    if perm not in user.role.permissions:
                        user.role.permissions.append(perm)
                
                db.commit()
                print("  ✅ Risk permissions added to role")
            else:
                print("  ✅ Has risk permissions:")
                for perm in risk_perms:
                    print(f"    - {perm.module.value}:{perm.action.value}")
        
        print("\n✅ User permission check completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def create_admin_user_with_risk_permissions():
    """Create an admin user with full risk permissions"""
    print("Creating admin user with risk permissions...")
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if admin_user:
            print("Admin user already exists")
            return admin_user
        
        # Get or create admin role with all permissions
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        
        if not admin_role:
            print("❌ System Administrator role not found")
            return None
        
        # Create admin user
        from app.core.security import get_password_hash
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role_id=admin_role.id,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully")
        print("  Username: admin")
        print("  Password: admin123")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Risk Permission Fix Script ===\n")
    
    # Check and fix user permissions
    check_user_permissions()
    
    print("\n" + "="*50 + "\n")
    
    # Create admin user if needed
    create_admin_user_with_risk_permissions()
    
    print("\n=== Script completed ===")
    print("\nTo test risk access:")
    print("1. Login with admin/admin123")
    print("2. Try accessing the risk module")
    print("3. Check browser console for any remaining 403 errors")
