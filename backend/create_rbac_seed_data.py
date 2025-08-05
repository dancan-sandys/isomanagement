#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create default roles and permissions for RBAC system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.rbac import Role, Permission, Module, PermissionType
from app.models.user import User
from app.core.security import get_password_hash

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_permissions():
    """Create all permissions for the system"""
    print("Creating permissions...")
    
    permissions_data = [
        # Dashboard permissions
        (Module.DASHBOARD, PermissionType.VIEW, "View dashboard"),
        
        # Document permissions
        (Module.DOCUMENTS, PermissionType.VIEW, "View documents"),
        (Module.DOCUMENTS, PermissionType.CREATE, "Create documents"),
        (Module.DOCUMENTS, PermissionType.UPDATE, "Update documents"),
        (Module.DOCUMENTS, PermissionType.DELETE, "Delete documents"),
        (Module.DOCUMENTS, PermissionType.APPROVE, "Approve documents"),
        (Module.DOCUMENTS, PermissionType.EXPORT, "Export documents"),
        
        # HACCP permissions
        (Module.HACCP, PermissionType.VIEW, "View HACCP plans"),
        (Module.HACCP, PermissionType.CREATE, "Create HACCP plans"),
        (Module.HACCP, PermissionType.UPDATE, "Update HACCP plans"),
        (Module.HACCP, PermissionType.DELETE, "Delete HACCP plans"),
        (Module.HACCP, PermissionType.APPROVE, "Approve HACCP plans"),
        (Module.HACCP, PermissionType.EXPORT, "Export HACCP data"),
        
        # PRP permissions
        (Module.PRP, PermissionType.VIEW, "View PRP programs"),
        (Module.PRP, PermissionType.CREATE, "Create PRP programs"),
        (Module.PRP, PermissionType.UPDATE, "Update PRP programs"),
        (Module.PRP, PermissionType.DELETE, "Delete PRP programs"),
        (Module.PRP, PermissionType.APPROVE, "Approve PRP programs"),
        (Module.PRP, PermissionType.EXPORT, "Export PRP data"),
        
        # Supplier permissions
        (Module.SUPPLIERS, PermissionType.VIEW, "View suppliers"),
        (Module.SUPPLIERS, PermissionType.CREATE, "Create suppliers"),
        (Module.SUPPLIERS, PermissionType.UPDATE, "Update suppliers"),
        (Module.SUPPLIERS, PermissionType.DELETE, "Delete suppliers"),
        (Module.SUPPLIERS, PermissionType.APPROVE, "Approve suppliers"),
        (Module.SUPPLIERS, PermissionType.EXPORT, "Export supplier data"),
        
        # Traceability permissions
        (Module.TRACEABILITY, PermissionType.VIEW, "View traceability data"),
        (Module.TRACEABILITY, PermissionType.CREATE, "Create traceability records"),
        (Module.TRACEABILITY, PermissionType.UPDATE, "Update traceability records"),
        (Module.TRACEABILITY, PermissionType.DELETE, "Delete traceability records"),
        (Module.TRACEABILITY, PermissionType.EXPORT, "Export traceability data"),
        
        # User permissions
        (Module.USERS, PermissionType.VIEW, "View users"),
        (Module.USERS, PermissionType.CREATE, "Create users"),
        (Module.USERS, PermissionType.UPDATE, "Update users"),
        (Module.USERS, PermissionType.DELETE, "Delete users"),
        (Module.USERS, PermissionType.ASSIGN, "Assign user roles"),
        
        # Role permissions
        (Module.ROLES, PermissionType.VIEW, "View roles"),
        (Module.ROLES, PermissionType.CREATE, "Create roles"),
        (Module.ROLES, PermissionType.UPDATE, "Update roles"),
        (Module.ROLES, PermissionType.DELETE, "Delete roles"),
        (Module.ROLES, PermissionType.ASSIGN, "Assign role permissions"),
        
        # Settings permissions
        (Module.SETTINGS, PermissionType.VIEW, "View settings"),
        (Module.SETTINGS, PermissionType.UPDATE, "Update settings"),
        (Module.SETTINGS, PermissionType.EXPORT, "Export settings"),
        (Module.SETTINGS, PermissionType.IMPORT, "Import settings"),
        
        # Notification permissions
        (Module.NOTIFICATIONS, PermissionType.VIEW, "View notifications"),
        (Module.NOTIFICATIONS, PermissionType.CREATE, "Create notifications"),
        (Module.NOTIFICATIONS, PermissionType.UPDATE, "Update notifications"),
        (Module.NOTIFICATIONS, PermissionType.DELETE, "Delete notifications"),
        
        # Audit permissions
        (Module.AUDITS, PermissionType.VIEW, "View audits"),
        (Module.AUDITS, PermissionType.CREATE, "Create audits"),
        (Module.AUDITS, PermissionType.UPDATE, "Update audits"),
        (Module.AUDITS, PermissionType.DELETE, "Delete audits"),
        (Module.AUDITS, PermissionType.APPROVE, "Approve audits"),
        (Module.AUDITS, PermissionType.EXPORT, "Export audit data"),
        
        # Training permissions
        (Module.TRAINING, PermissionType.VIEW, "View training records"),
        (Module.TRAINING, PermissionType.CREATE, "Create training records"),
        (Module.TRAINING, PermissionType.UPDATE, "Update training records"),
        (Module.TRAINING, PermissionType.DELETE, "Delete training records"),
        (Module.TRAINING, PermissionType.ASSIGN, "Assign training"),
        (Module.TRAINING, PermissionType.EXPORT, "Export training data"),
        
        # Maintenance permissions
        (Module.MAINTENANCE, PermissionType.VIEW, "View maintenance records"),
        (Module.MAINTENANCE, PermissionType.CREATE, "Create maintenance records"),
        (Module.MAINTENANCE, PermissionType.UPDATE, "Update maintenance records"),
        (Module.MAINTENANCE, PermissionType.DELETE, "Delete maintenance records"),
        (Module.MAINTENANCE, PermissionType.ASSIGN, "Assign maintenance tasks"),
        (Module.MAINTENANCE, PermissionType.EXPORT, "Export maintenance data"),
        
        # Complaint permissions
        (Module.COMPLAINTS, PermissionType.VIEW, "View complaints"),
        (Module.COMPLAINTS, PermissionType.CREATE, "Create complaints"),
        (Module.COMPLAINTS, PermissionType.UPDATE, "Update complaints"),
        (Module.COMPLAINTS, PermissionType.DELETE, "Delete complaints"),
        (Module.COMPLAINTS, PermissionType.ASSIGN, "Assign complaints"),
        (Module.COMPLAINTS, PermissionType.EXPORT, "Export complaint data"),
        
        # NC/CAPA permissions
        (Module.NC_CAPA, PermissionType.VIEW, "View NC/CAPA records"),
        (Module.NC_CAPA, PermissionType.CREATE, "Create NC/CAPA records"),
        (Module.NC_CAPA, PermissionType.UPDATE, "Update NC/CAPA records"),
        (Module.NC_CAPA, PermissionType.DELETE, "Delete NC/CAPA records"),
        (Module.NC_CAPA, PermissionType.ASSIGN, "Assign NC/CAPA tasks"),
        (Module.NC_CAPA, PermissionType.APPROVE, "Approve NC/CAPA actions"),
        (Module.NC_CAPA, PermissionType.EXPORT, "Export NC/CAPA data"),
        
        # Risk & Opportunity permissions
        (Module.RISK_OPPORTUNITY, PermissionType.VIEW, "View risk & opportunity records"),
        (Module.RISK_OPPORTUNITY, PermissionType.CREATE, "Create risk & opportunity records"),
        (Module.RISK_OPPORTUNITY, PermissionType.UPDATE, "Update risk & opportunity records"),
        (Module.RISK_OPPORTUNITY, PermissionType.DELETE, "Delete risk & opportunity records"),
        (Module.RISK_OPPORTUNITY, PermissionType.ASSIGN, "Assign risk & opportunity tasks"),
        (Module.RISK_OPPORTUNITY, PermissionType.EXPORT, "Export risk & opportunity data"),
        
        # Management Review permissions
        (Module.MANAGEMENT_REVIEW, PermissionType.VIEW, "View management review records"),
        (Module.MANAGEMENT_REVIEW, PermissionType.CREATE, "Create management review records"),
        (Module.MANAGEMENT_REVIEW, PermissionType.UPDATE, "Update management review records"),
        (Module.MANAGEMENT_REVIEW, PermissionType.DELETE, "Delete management review records"),
        (Module.MANAGEMENT_REVIEW, PermissionType.APPROVE, "Approve management review records"),
        (Module.MANAGEMENT_REVIEW, PermissionType.EXPORT, "Export management review data"),
        
        # Allergen & Label permissions
        (Module.ALLERGEN_LABEL, PermissionType.VIEW, "View allergen & label records"),
        (Module.ALLERGEN_LABEL, PermissionType.CREATE, "Create allergen & label records"),
        (Module.ALLERGEN_LABEL, PermissionType.UPDATE, "Update allergen & label records"),
        (Module.ALLERGEN_LABEL, PermissionType.DELETE, "Delete allergen & label records"),
        (Module.ALLERGEN_LABEL, PermissionType.APPROVE, "Approve allergen & label records"),
        (Module.ALLERGEN_LABEL, PermissionType.EXPORT, "Export allergen & label data"),
    ]
    
    db = SessionLocal()
    try:
        for module, action, description in permissions_data:
            # Check if permission already exists
            existing = db.query(Permission).filter(
                Permission.module == module,
                Permission.action == action
            ).first()
            
            if not existing:
                permission = Permission(
                    module=module,
                    action=action,
                    description=description
                )
                db.add(permission)
                print(f"✅ Created permission: {module.value}:{action.value}")
            else:
                print(f"⏭️  Permission already exists: {module.value}:{action.value}")
        
        db.commit()
        print("✅ All permissions created successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating permissions: {e}")
        raise
    finally:
        db.close()

def create_default_roles():
    """Create default roles with appropriate permissions"""
    print("Creating default roles...")
    
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
                "description": "Manage documents, audits, HACCP, PRPs, CAPAs",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.CREATE),
                    (Module.DOCUMENTS, PermissionType.UPDATE),
                    (Module.DOCUMENTS, PermissionType.APPROVE),
                    (Module.DOCUMENTS, PermissionType.EXPORT),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.CREATE),
                    (Module.HACCP, PermissionType.UPDATE),
                    (Module.HACCP, PermissionType.APPROVE),
                    (Module.HACCP, PermissionType.EXPORT),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.CREATE),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.PRP, PermissionType.APPROVE),
                    (Module.PRP, PermissionType.EXPORT),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.CREATE),
                    (Module.AUDITS, PermissionType.UPDATE),
                    (Module.AUDITS, PermissionType.APPROVE),
                    (Module.AUDITS, PermissionType.EXPORT),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                    (Module.NC_CAPA, PermissionType.UPDATE),
                    (Module.NC_CAPA, PermissionType.ASSIGN),
                    (Module.NC_CAPA, PermissionType.APPROVE),
                    (Module.NC_CAPA, PermissionType.EXPORT),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.SUPPLIERS, PermissionType.CREATE),
                    (Module.SUPPLIERS, PermissionType.UPDATE),
                    (Module.SUPPLIERS, PermissionType.APPROVE),
                    (Module.SUPPLIERS, PermissionType.EXPORT),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.CREATE),
                    (Module.TRACEABILITY, PermissionType.UPDATE),
                    (Module.TRACEABILITY, PermissionType.EXPORT),
                    (Module.TRAINING, PermissionType.VIEW),
                    (Module.TRAINING, PermissionType.CREATE),
                    (Module.TRAINING, PermissionType.UPDATE),
                    (Module.TRAINING, PermissionType.ASSIGN),
                    (Module.TRAINING, PermissionType.EXPORT),
                    (Module.COMPLAINTS, PermissionType.VIEW),
                    (Module.COMPLAINTS, PermissionType.CREATE),
                    (Module.COMPLAINTS, PermissionType.UPDATE),
                    (Module.COMPLAINTS, PermissionType.ASSIGN),
                    (Module.COMPLAINTS, PermissionType.EXPORT),
                    (Module.RISK_OPPORTUNITY, PermissionType.VIEW),
                    (Module.RISK_OPPORTUNITY, PermissionType.CREATE),
                    (Module.RISK_OPPORTUNITY, PermissionType.UPDATE),
                    (Module.RISK_OPPORTUNITY, PermissionType.ASSIGN),
                    (Module.RISK_OPPORTUNITY, PermissionType.EXPORT),
                    (Module.MANAGEMENT_REVIEW, PermissionType.VIEW),
                    (Module.MANAGEMENT_REVIEW, PermissionType.CREATE),
                    (Module.MANAGEMENT_REVIEW, PermissionType.UPDATE),
                    (Module.MANAGEMENT_REVIEW, PermissionType.APPROVE),
                    (Module.MANAGEMENT_REVIEW, PermissionType.EXPORT),
                    (Module.ALLERGEN_LABEL, PermissionType.VIEW),
                    (Module.ALLERGEN_LABEL, PermissionType.CREATE),
                    (Module.ALLERGEN_LABEL, PermissionType.UPDATE),
                    (Module.ALLERGEN_LABEL, PermissionType.APPROVE),
                    (Module.ALLERGEN_LABEL, PermissionType.EXPORT),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                    (Module.NOTIFICATIONS, PermissionType.CREATE),
                    (Module.NOTIFICATIONS, PermissionType.UPDATE),
                    (Module.SETTINGS, PermissionType.VIEW),
                    (Module.SETTINGS, PermissionType.UPDATE),
                ]
            },
            {
                "name": "Production Manager",
                "description": "View/edit HACCP and PRP logs, limited write access to NCs",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.UPDATE),
                    (Module.HACCP, PermissionType.EXPORT),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.PRP, PermissionType.EXPORT),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                    (Module.NC_CAPA, PermissionType.UPDATE),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.CREATE),
                    (Module.TRACEABILITY, PermissionType.UPDATE),
                    (Module.MAINTENANCE, PermissionType.VIEW),
                    (Module.MAINTENANCE, PermissionType.CREATE),
                    (Module.MAINTENANCE, PermissionType.UPDATE),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Line Operator",
                "description": "Input/checklists only",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.CREATE),
                    (Module.MAINTENANCE, PermissionType.VIEW),
                    (Module.MAINTENANCE, PermissionType.CREATE),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Auditor",
                "description": "Access audit logs, initiate audits, raise NCs",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.CREATE),
                    (Module.AUDITS, PermissionType.UPDATE),
                    (Module.AUDITS, PermissionType.EXPORT),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                    (Module.NC_CAPA, PermissionType.UPDATE),
                    (Module.NC_CAPA, PermissionType.EXPORT),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Compliance Officer",
                "description": "Read-only across the system",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.EXPORT),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.EXPORT),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.EXPORT),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.SUPPLIERS, PermissionType.EXPORT),
                    (Module.TRACEABILITY, PermissionType.VIEW),
                    (Module.TRACEABILITY, PermissionType.EXPORT),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.EXPORT),
                    (Module.TRAINING, PermissionType.VIEW),
                    (Module.TRAINING, PermissionType.EXPORT),
                    (Module.MAINTENANCE, PermissionType.VIEW),
                    (Module.MAINTENANCE, PermissionType.EXPORT),
                    (Module.COMPLAINTS, PermissionType.VIEW),
                    (Module.COMPLAINTS, PermissionType.EXPORT),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.EXPORT),
                    (Module.RISK_OPPORTUNITY, PermissionType.VIEW),
                    (Module.RISK_OPPORTUNITY, PermissionType.EXPORT),
                    (Module.MANAGEMENT_REVIEW, PermissionType.VIEW),
                    (Module.MANAGEMENT_REVIEW, PermissionType.EXPORT),
                    (Module.ALLERGEN_LABEL, PermissionType.VIEW),
                    (Module.ALLERGEN_LABEL, PermissionType.EXPORT),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Maintenance Engineer",
                "description": "Manage maintenance/calibration logs",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.MAINTENANCE, PermissionType.VIEW),
                    (Module.MAINTENANCE, PermissionType.CREATE),
                    (Module.MAINTENANCE, PermissionType.UPDATE),
                    (Module.MAINTENANCE, PermissionType.DELETE),
                    (Module.MAINTENANCE, PermissionType.ASSIGN),
                    (Module.MAINTENANCE, PermissionType.EXPORT),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Trainer",
                "description": "Assign and track training, update training matrix",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.TRAINING, PermissionType.VIEW),
                    (Module.TRAINING, PermissionType.CREATE),
                    (Module.TRAINING, PermissionType.UPDATE),
                    (Module.TRAINING, PermissionType.DELETE),
                    (Module.TRAINING, PermissionType.ASSIGN),
                    (Module.TRAINING, PermissionType.EXPORT),
                    (Module.USERS, PermissionType.VIEW),
                    (Module.NOTIFICATIONS, PermissionType.VIEW),
                    (Module.NOTIFICATIONS, PermissionType.CREATE),
                ]
            },
        ]
        
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

def update_existing_users():
    """Update existing users to have the default System Administrator role"""
    print("Updating existing users...")
    
    db = SessionLocal()
    try:
        # Get the System Administrator role
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            print("❌ System Administrator role not found")
            return
        
        # Update existing users to have the admin role
        users = db.query(User).all()
        for user in users:
            if not hasattr(user, 'role_id') or user.role_id is None:
                user.role_id = admin_role.id
                print(f"✅ Updated user {user.username} to System Administrator role")
        
        db.commit()
        print("✅ All existing users updated successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating users: {e}")
        raise
    finally:
        db.close()

def main():
    """Main function to create RBAC seed data"""
    print("🚀 Creating RBAC seed data...")
    
    try:
        # Create permissions first
        create_permissions()
        
        # Create default roles
        create_default_roles()
        
        # Update existing users
        update_existing_users()
        
        print("🎉 RBAC seed data created successfully!")
        print("\n📋 Summary:")
        print("- All permissions created")
        print("- 8 default roles created with appropriate permissions")
        print("- Existing users updated to System Administrator role")
        print("\n🔐 Default roles:")
        print("1. System Administrator - Full access")
        print("2. QA Manager - Document, HACCP, PRP, Audit, NC/CAPA management")
        print("3. Production Manager - HACCP/PRP logs, limited NC access")
        print("4. Line Operator - Input/checklists only")
        print("5. Auditor - Audit logs, initiate audits, raise NCs")
        print("6. Compliance Officer - Read-only across system")
        print("7. Maintenance Engineer - Maintenance/calibration logs")
        print("8. Trainer - Training assignment and tracking")
        
    except Exception as e:
        print(f"❌ Error creating RBAC seed data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 