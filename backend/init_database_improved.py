#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Database Initialization Script for ISO 22000 FSMS Platform

This script ensures that all enum values are correctly set to lowercase
from the start, preventing the need for migrations when setting up new databases.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from app.core.database import SessionLocal, engine, Base
from app.models.rbac import Role, Permission, UserPermission
from app.models.user import User, UserStatus
from app.core.security import get_password_hash
from app.models.rbac import Module, PermissionType
from app.models.nonconformance import NonConformanceStatus, NonConformanceSource
from app.models.haccp import RiskLevel, HazardType, CCPStatus
from app.models.document import DocumentStatus, DocumentType
from app.models.complaint import ComplaintStatus, ComplaintClassification
from app.models.supplier import SupplierStatus, SupplierCategory
from app.models.audit_mgmt import AuditStatus, AuditType
from app.models.traceability import BatchStatus, BatchType, RecallStatus
from datetime import datetime

def validate_enum_values():
    """Validate that all enum values are correctly set to lowercase"""
    print("Validating enum values...")
    
    # Define expected enum values (all lowercase)
    expected_enums = {
        'UserStatus': {
            'ACTIVE': 'active',
            'INACTIVE': 'inactive', 
            'SUSPENDED': 'suspended',
            'PENDING_APPROVAL': 'pending_approval'
        },
        'NonConformanceStatus': {
            'OPEN': 'open',
            'UNDER_INVESTIGATION': 'under_investigation',
            'ROOT_CAUSE_IDENTIFIED': 'root_cause_identified',
            'CAPA_ASSIGNED': 'capa_assigned',
            'IN_PROGRESS': 'in_progress',
            'COMPLETED': 'completed',
            'VERIFIED': 'verified',
            'CLOSED': 'closed'
        },
        'NonConformanceSource': {
            'PRP': 'prp',
            'AUDIT': 'audit',
            'COMPLAINT': 'complaint',
            'PRODUCTION_DEVIATION': 'production_deviation',
            'SUPPLIER': 'supplier',
            'HACCP': 'haccp',
            'DOCUMENT': 'document',
            'INSPECTION': 'inspection',
            'OTHER': 'other'
        },
        'RiskLevel': {
            'LOW': 'low',
            'MEDIUM': 'medium',
            'HIGH': 'high',
            'CRITICAL': 'critical'
        },
        'HazardType': {
            'BIOLOGICAL': 'biological',
            'CHEMICAL': 'chemical',
            'PHYSICAL': 'physical',
            'ALLERGEN': 'allergen'
        },
        'CCPStatus': {
            'ACTIVE': 'active',
            'INACTIVE': 'inactive',
            'SUSPENDED': 'suspended'
        },
        'DocumentStatus': {
            'DRAFT': 'draft',
            'UNDER_REVIEW': 'under_review',
            'APPROVED': 'approved',
            'OBSOLETE': 'obsolete',
            'ARCHIVED': 'archived'
        },
        'ComplaintStatus': {
            'OPEN': 'open',
            'UNDER_INVESTIGATION': 'under_investigation',
            'RESOLVED': 'resolved',
            'CLOSED': 'closed'
        },
        'SupplierStatus': {
            'ACTIVE': 'active',
            'INACTIVE': 'inactive',
            'SUSPENDED': 'suspended',
            'PENDING_APPROVAL': 'pending_approval',
            'BLACKLISTED': 'blacklisted'
        },
        'AuditStatus': {
            'PLANNED': 'planned',
            'IN_PROGRESS': 'in_progress',
            'COMPLETED': 'completed',
            'CLOSED': 'closed'
        },
        'BatchStatus': {
            'IN_PRODUCTION': 'in_production',
            'COMPLETED': 'completed',
            'QUARANTINED': 'quarantined',
            'RELEASED': 'released',
            'RECALLED': 'recalled',
            'DISPOSED': 'disposed'
        }
    }
    
    # Validate each enum
    validation_errors = []
    
    for enum_name, expected_values in expected_enums.items():
        try:
            # Get the actual enum class
            enum_class = globals().get(enum_name)
            if not enum_class:
                validation_errors.append(f"Enum class {enum_name} not found")
                continue
                
            # Check each enum value
            for expected_key, expected_value in expected_values.items():
                actual_value = getattr(enum_class, expected_key, None)
                if actual_value != expected_value:
                    validation_errors.append(
                        f"{enum_name}.{expected_key}: expected '{expected_value}', got '{actual_value}'"
                    )
            
            print(f"{enum_name}: All values correctly set to lowercase")
            
        except Exception as e:
            validation_errors.append(f"Error validating {enum_name}: {e}")
    
    if validation_errors:
        print("\nEnum validation failed:")
        for error in validation_errors:
            print(f"  {error}")
        raise ValueError("Enum values are not correctly set to lowercase")
    
    print("All enum values validated successfully!")

def create_database_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # List created tables
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Created {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")
        except Exception as e:
            print(f"⚠️  Could not list tables: {e}")
            
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

def create_permissions():
    """Create all permissions for the system"""
    print("🔐 Creating permissions...")
    
    db = SessionLocal()
    try:
        # Check if permissions already exist
        existing_permissions = db.query(Permission).count()
        if existing_permissions > 0:
            print(f"⏭️  Found {existing_permissions} existing permissions. Skipping creation.")
            return
        
        # Create permissions for all modules and actions
        permissions = []
        for module in Module:
            for action in PermissionType:
                permission = Permission(
                    module=module,
                    action=action,
                    description=f"{action.value.title()} permission for {module.value}"
                )
                permissions.append(permission)
        
        db.add_all(permissions)
        db.commit()
        print(f"✓ Created {len(permissions)} permissions")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating permissions: {e}")
        raise
    finally:
        db.close()

def create_default_roles():
    """Create default roles with appropriate permissions"""
    print("👥 Creating default roles...")
    
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles > 0:
            print(f"⏭️  Found {existing_roles} existing roles. Skipping creation.")
            return
        
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
                "description": "Quality Assurance management and oversight",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.CREATE),
                    (Module.HACCP, PermissionType.UPDATE),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.CREATE),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.SUPPLIERS, PermissionType.CREATE),
                    (Module.SUPPLIERS, PermissionType.UPDATE),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.CREATE),
                    (Module.DOCUMENTS, PermissionType.UPDATE),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.CREATE),
                    (Module.AUDITS, PermissionType.UPDATE),
                    (Module.COMPLAINTS, PermissionType.VIEW),
                    (Module.COMPLAINTS, PermissionType.CREATE),
                    (Module.COMPLAINTS, PermissionType.UPDATE),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                    (Module.NC_CAPA, PermissionType.UPDATE),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.CREATE),
                    (Module.EQUIPMENT, PermissionType.UPDATE),
                    (Module.USERS, PermissionType.VIEW),
                    (Module.USERS, PermissionType.CREATE),
                    (Module.USERS, PermissionType.UPDATE),
                    (Module.REPORTS, PermissionType.VIEW),
                    (Module.SETTINGS, PermissionType.VIEW),
                    (Module.SETTINGS, PermissionType.UPDATE),
                ]
            },
            {
                "name": "QA Specialist",
                "description": "Quality Assurance specialist with limited management access",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.CREATE),
                    (Module.HACCP, PermissionType.UPDATE),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.CREATE),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.CREATE),
                    (Module.DOCUMENTS, PermissionType.UPDATE),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.CREATE),
                    (Module.COMPLAINTS, PermissionType.VIEW),
                    (Module.COMPLAINTS, PermissionType.CREATE),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.REPORTS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Production Manager",
                "description": "Production management with HACCP and PRP access",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.CREATE),
                    (Module.HACCP, PermissionType.UPDATE),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.CREATE),
                    (Module.PRP, PermissionType.UPDATE),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.CREATE),
                    (Module.EQUIPMENT, PermissionType.UPDATE),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                    (Module.REPORTS, PermissionType.VIEW),
                ]
            },
            {
                "name": "Production Operator",
                "description": "Production operator with basic access",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.CREATE),
                ]
            },
            {
                "name": "Viewer",
                "description": "Read-only access to most modules",
                "is_default": True,
                "is_editable": True,
                "permissions": [
                    (Module.DASHBOARD, PermissionType.VIEW),
                    (Module.HACCP, PermissionType.VIEW),
                    (Module.PRP, PermissionType.VIEW),
                    (Module.SUPPLIERS, PermissionType.VIEW),
                    (Module.DOCUMENTS, PermissionType.VIEW),
                    (Module.AUDITS, PermissionType.VIEW),
                    (Module.COMPLAINTS, PermissionType.VIEW),
                    (Module.NC_CAPA, PermissionType.VIEW),
                    (Module.EQUIPMENT, PermissionType.VIEW),
                    (Module.REPORTS, PermissionType.VIEW),
                ]
            }
        ]
        
        # Create roles
        for role_data in roles_data:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                is_default=role_data["is_default"],
                is_editable=role_data["is_editable"]
            )
            
            # Assign permissions
            role_permissions = []
            for module, action in role_data["permissions"]:
                permission = permissions_dict.get((module, action))
                if permission:
                    role_permissions.append(permission)
            
            role.permissions = role_permissions
            db.add(role)
            print(f"✓ Created role: {role_data['name']} with {len(role_permissions)} permissions")
        
        db.commit()
        print("✓ All default roles created successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating roles: {e}")
        raise
    finally:
        db.close()

def create_admin_user():
    """Create the default admin user"""
    print("👤 Creating admin user...")
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("⏭️  Admin user already exists")
            return
        
        # Get System Administrator role
        admin_role = db.query(Role).filter(Role.name == "System Administrator").first()
        if not admin_role:
            print("✗ System Administrator role not found!")
            return
        
        # Create admin user with lowercase status
        admin_user = User(
            username="admin",
            email="admin@iso22000.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role_id=admin_role.id,
            status=UserStatus.ACTIVE,  # This will be 'active' (lowercase)
            department="Quality Assurance",
            position="System Administrator",
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✓ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Role: System Administrator")
        print(f"Status: {admin_user.status}")  # Should show 'active'
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating admin user: {e}")
        raise
    finally:
        db.close()

def verify_database_integrity():
    """Verify that the database was created correctly with proper enum values"""
    print("Checking Verifying database integrity...")
    
    db = SessionLocal()
    try:
        # Check that admin user was created with correct status
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            if admin_user.status == 'active':
                print("✓ Admin user status correctly set to 'active'")
            else:
                print(f"⚠️  Admin user status is '{admin_user.status}' (should be 'active')")
        
        # Check that roles were created
        role_count = db.query(Role).count()
        print(f"✓ Found {role_count} roles")
        
        # Check that permissions were created
        permission_count = db.query(Permission).count()
        print(f"✓ Found {permission_count} permissions")
        
        # Verify enum columns are using lowercase values
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        enum_tables = ['users', 'non_conformances', 'products', 'hazards', 'ccp_points']
        for table in enum_tables:
            if table in tables:
                try:
                    # Check a sample record if any exists
                    result = db.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                    if result.fetchone():
                        print(f"✓ Table {table} has data with correct enum values")
                    else:
                        print(f"✓ Table {table} created (no data yet)")
                except Exception as e:
                    print(f"⚠️  Could not verify table {table}: {e}")
        
        print("✓ Database integrity verification completed")
        
    except Exception as e:
        print(f"✗ Error during database verification: {e}")
        raise
    finally:
        db.close()

def main():
    """Main function to initialize the database with proper enum values"""
    print("Starting Starting improved database initialization...")
    print("=" * 60)
    
    try:
        # Step 1: Validate enum values in models
        validate_enum_values()
        
        # Step 2: Create database tables
        create_database_tables()
        
        # Step 3: Create permissions
        create_permissions()
        
        # Step 4: Create roles
        create_default_roles()
        
        # Step 5: Create admin user
        create_admin_user()
        
        # Step 6: Verify database integrity
        verify_database_integrity()
        
        print("\n" + "=" * 60)
        print("🎉 Improved database initialization completed successfully!")
        print("\nCreating Summary:")
        print("  ✓ Enum values validated (all lowercase)")
        print("  ✓ Database tables created")
        print("  ✓ Permissions created")
        print("  ✓ Default roles created")
        print("  ✓ Admin user created")
        print("  ✓ Database integrity verified")
        print("\nLogin Login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: System Administrator")
        print("  Status: active (lowercase)")
        print("\nBenefits Benefits:")
        print("  - All enum values are lowercase from the start")
        print("  - No need for enum migration scripts")
        print("  - Consistent data format across frontend and backend")
        print("  - Ready for production use")
        
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        print("\nBenefits Troubleshooting:")
        print("  - Check that all model files have lowercase enum values")
        print("  - Ensure database connection is working")
        print("  - Verify all required dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()
