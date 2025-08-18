#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to fix risk permissions for users
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "sqlite:///./iso22000.db"
engine = create_engine(DATABASE_URL)

def fix_risk_permissions():
    """Fix risk permissions for all users"""
    print("Fixing risk permissions...")
    
    try:
        with engine.connect() as conn:
            # Check if risk permissions exist
            result = conn.execute(text("""
                SELECT id, module, action FROM permissions 
                WHERE module = 'risk_opportunity'
            """))
            risk_permissions = result.fetchall()
            
            if not risk_permissions:
                print("❌ No risk permissions found in database")
                print("Creating risk permissions...")
                
                # Create risk permissions
                permissions_data = [
                    ('risk_opportunity', 'view', 'View risk & opportunity records'),
                    ('risk_opportunity', 'create', 'Create risk & opportunity records'),
                    ('risk_opportunity', 'update', 'Update risk & opportunity records'),
                    ('risk_opportunity', 'delete', 'Delete risk & opportunity records'),
                    ('risk_opportunity', 'assign', 'Assign risk & opportunity tasks'),
                    ('risk_opportunity', 'export', 'Export risk & opportunity data'),
                ]
                
                for module, action, description in permissions_data:
                    conn.execute(text("""
                        INSERT INTO permissions (module, action, description, created_at)
                        VALUES (:module, :action, :description, datetime('now'))
                    """), {"module": module, "action": action, "description": description})
                
                conn.commit()
                print("✅ Risk permissions created")
                
                # Get the created permissions
                result = conn.execute(text("""
                    SELECT id, module, action FROM permissions 
                    WHERE module = 'risk_opportunity'
                """))
                risk_permissions = result.fetchall()
            
            print(f"Found {len(risk_permissions)} risk permissions")
            
            # Get all roles
            result = conn.execute(text("SELECT id, name FROM roles"))
            roles = result.fetchall()
            
            print(f"Found {len(roles)} roles")
            
            # Add risk permissions to all roles
            for role in roles:
                role_id = role[0]
                role_name = role[1]
                
                print(f"Processing role: {role_name}")
                
                # Check if role already has risk permissions
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM role_permissions rp
                    JOIN permissions p ON rp.permission_id = p.id
                    WHERE rp.role_id = :role_id AND p.module = 'risk_opportunity'
                """), {"role_id": role_id})
                
                existing_count = result.fetchone()[0]
                
                if existing_count == 0:
                    print(f"  Adding risk permissions to {role_name}...")
                    
                    # Add all risk permissions to this role
                    for perm in risk_permissions:
                        perm_id = perm[0]
                        conn.execute(text("""
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (:role_id, :permission_id)
                        """), {"role_id": role_id, "permission_id": perm_id})
                    
                    print(f"  ✅ Added {len(risk_permissions)} permissions to {role_name}")
                else:
                    print(f"  ✅ {role_name} already has {existing_count} risk permissions")
            
            conn.commit()
            print("\n✅ Risk permissions fixed for all roles!")
            
            # Check admin user
            result = conn.execute(text("""
                SELECT u.username, u.is_active, r.name as role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.username = 'admin'
            """))
            admin_user = result.fetchone()
            
            if admin_user:
                print(f"\nAdmin user status:")
                print(f"  Username: {admin_user[0]}")
                print(f"  Active: {admin_user[1]}")
                print(f"  Role: {admin_user[2]}")
            else:
                print("\n❌ Admin user not found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Risk Permission Fix Script ===\n")
    success = fix_risk_permissions()
    
    if success:
        print("\n=== Script completed successfully ===")
        print("\nTo test risk access:")
        print("1. Restart your backend server")
        print("2. Login with admin/admin123")
        print("3. Try accessing the risk module")
        print("4. Check browser console for any remaining 403 errors")
    else:
        print("\n=== Script failed ===")
