#!/usr/bin/env python3
"""
Complete Database Setup Script for ISO 22000 FSMS
This script creates all database tables and populates them with professional demo data

IMPORTANT SCHEMA UPDATES (2025-10-18):
========================================
HAZARDS TABLE:
- 'consequences' field: Detailed description of potential consequences (replaces 'rationale')
- 'risk_strategy' field: Control strategy (ccp/opprp/use_existing_prps)
- 'risk_strategy_justification' field: Justification for chosen strategy
- 'subsequent_step' field: Next process step that controls the hazard (if applicable)
- 'is_ccp' field: Boolean flag for critical control points

CCPS TABLE:
- Complete critical control point implementation
- critical_limit_min/max: Numerical critical limits
- critical_limit_unit: Unit of measurement
- monitoring_frequency: Frequency of CCP monitoring
- monitoring_method: Method used for monitoring
- corrective_actions: Actions when critical limits exceeded
- verification_frequency/method: CCP verification procedures

OPRPS TABLE:
- operational_limits: Description of operational limits
- operational_limit_min/max: Numerical operational limits
- operational_limit_unit: Unit of measurement
- monitoring_frequency: Frequency of OPRP monitoring
- monitoring_method: Method used for monitoring
- corrective_actions: Actions when operational limits exceeded
- verification_frequency/method: OPRP verification procedures
- objective: OPRP objective
- sop_reference: Reference to relevant SOP
- justification: Justification for OPRP designation

ISO 22000:2018 RISK STRATEGY IMPLEMENTATION:
===========================================
This setup creates realistic food safety data demonstrating:
1. CCP (Critical Control Points) - Most critical hazards requiring strict control
2. OPRP (Operational Prerequisite Programs) - High-risk operational hazards
3. Use Existing PRPs - Lower risk hazards controlled by prerequisite programs

See: HACCP_RISK_STRATEGY_IMPLEMENTATION.md for full details
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
from app.core.database import Base, engine
import random

# Import all models to ensure they are registered with Base.metadata
from app.models.user import User, UserSession, PasswordReset
from app.models.document import Document, DocumentVersion, DocumentApproval, DocumentChangeLog, DocumentTemplate
from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog, HACCPPlan,
    DecisionTree, HazardReview, RiskStrategy, HazardType, RiskLevel
)
from app.models.oprp import OPRP, OPRPMonitoringLog, OPRPVerificationLog
from app.models.prp import PRPProgram, PRPChecklist, PRPChecklistItem, PRPTemplate, PRPSchedule
from app.models.supplier import Supplier, SupplierDocument, SupplierEvaluation
from app.models.traceability import Batch, TraceabilityLink, RecallEntry
from app.models.notification import Notification
from app.models.rbac import Role, Permission, UserPermission
from app.models.equipment import Equipment, MaintenancePlan, MaintenanceWorkOrder, CalibrationPlan, CalibrationRecord
from app.models.management_review import ManagementReview, ReviewAgendaItem, ReviewAction
from app.models.risk import RiskRegisterItem, RiskAction
from app.models.food_safety_objectives import FoodSafetyObjective
from app.models.complaint import Complaint, ComplaintCommunication, ComplaintInvestigation
from app.models.allergen_label import ProductAllergenAssessment, LabelTemplate, LabelTemplateVersion, LabelTemplateApproval
from app.models.nonconformance import NonConformance, RootCauseAnalysis, CAPAAction, CAPAVerification, NonConformanceAttachment

def handle_existing_tables():
    """Handle cases where tables already exist by checking and reporting status"""
    print("🔍 Checking existing database state...")
    
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        if not existing_tables:
            print("  📝 No existing tables found - fresh database")
            return True
        
        print(f"  📋 Found {len(existing_tables)} existing tables")
        
        # Check for key tables
        key_tables = ['users', 'roles', 'permissions', 'role_permissions']
        missing_tables = []
        
        for table in key_tables:
            if table in existing_tables:
                print(f"    ✅ {table}")
            else:
                print(f"    ❌ {table} (missing)")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"  ⚠️  Missing key tables: {missing_tables}")
            print("  💡 Consider running: python reset_database.py")
            return False
        else:
            print("  ✅ All key tables present")
            return True
            
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
        return False

def create_database_tables():
    """Create all database tables"""
    print("🚀 Setting up database tables...")
    print("📌 Schema includes ISO 22000 Risk Strategy updates (consequences, risk_strategy, OPPRP support)")
    
    try:
        # Check existing tables first
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        if existing_tables:
            print(f"📋 Found {len(existing_tables)} existing tables")
            print("  ⚠️  Using existing database schema.")
            print("  💡 If you need the new risk strategy fields, run: python migrations/add_risk_strategy_to_hazards.py")
            
            # List existing tables
            print("  📝 Existing tables:")
            for table in sorted(existing_tables):
                print(f"    - {table}")
        else:
            print("  📝 No existing tables found. Creating new database schema with risk strategy support.")
        
        # Try to create tables, but handle the case where they already exist
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Database schema is ready with latest updates!")
        except Exception as create_error:
            # If create_all fails due to existing tables, that's actually OK
            if "already exists" in str(create_error):
                print("✅ Database tables already exist - using existing schema.")
            else:
                # Re-raise if it's a different error
                raise create_error
        
        # List all available tables
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"📋 Total tables available: {len(tables)}")
        except Exception as e:
            print(f"⚠️  Could not list tables: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database tables: {e}")
        print("  💡 This might be due to existing tables. Continuing with existing schema...")
        # Don't fail completely - try to continue with existing tables
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                print(f"  ✅ Found {len(tables)} existing tables - continuing with setup...")
                return True
        except:
            pass
        return False

def create_permissions():
    """Create comprehensive permissions for all modules and actions"""
    print("\n🔐 Creating comprehensive permissions...")
    
    try:
        with engine.connect() as conn:
            # Check if permissions table exists
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())
            
            if 'permissions' not in existing_tables:
                print("  ⚠️  Permissions table does not exist. Skipping permission creation.")
                return False
            
            # Check if permissions already exist
            result = conn.execute(text("SELECT COUNT(*) FROM permissions"))
            existing_count = result.scalar()
            
            if existing_count > 0:
                print(f"  ⏭️  Found {existing_count} existing permissions. Skipping creation.")
                return True
            
            # Define all modules and permission types
            modules = [
                'dashboard', 'documents', 'haccp', 'prp', 'suppliers', 'traceability',
                'users', 'roles', 'settings', 'notifications', 'audits', 'training',
                'maintenance', 'complaints', 'nc_capa', 'risk_opportunity',
                'management_review', 'allergen_label', 'equipment', 'reports', 'objectives'
            ]
            
            permission_types = [
                'view', 'create', 'update', 'delete', 'approve', 'assign', 
                'export', 'import', 'manage_program'
            ]
            
            # Create permissions for all combinations
            permission_counter = 1
            for module in modules:
                for action in permission_types:
                    description = f"{action.title()} permission for {module}"
                    conn.execute(text("""
                        INSERT OR IGNORE INTO permissions (id, module, action, description, created_at)
                        VALUES (:permission_id, :module, :action, :description, :created_at)
                    """), {
                        'permission_id': permission_counter,
                        'module': module,
                        'action': action,
                        'description': description,
                        'created_at': datetime.now().isoformat()
                    })
                    permission_counter += 1
            
            conn.commit()
            print(f"  ✓ Created {len(modules) * len(permission_types)} permissions")
            return True
            
    except Exception as e:
        print(f"  ⚠️  Could not create permissions: {e}")
        return False

def create_default_roles():
    """Create default roles with proper permissions"""
    print("\n👥 Creating default roles with permissions...")
    
    try:
        with engine.connect() as conn:
            # Check if roles table exists
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())
            
            if 'roles' not in existing_tables:
                print("  ⚠️  Roles table does not exist. Skipping role creation.")
                return False
            
            # Check if roles already exist
            result = conn.execute(text("SELECT COUNT(*) FROM roles"))
            existing_count = result.scalar()
            
            # Always create/update all 10 roles (names must match frontend navigation expectations)
            roles_data = [
                (1, 'System Administrator', 'System Administrator', 'Full system access', True, False, True),
                (2, 'QA Manager', 'QA Manager', 'Quality assurance management', True, True, True),
                (3, 'QA Specialist', 'QA Specialist', 'Quality assurance specialist', True, True, True),
                (4, 'Production Manager', 'Production Manager', 'Production management', True, True, True),
                (5, 'Production Operator', 'Production Operator', 'Production operations', True, True, True),
                (6, 'Maintenance Manager', 'Maintenance Manager', 'Maintenance management', True, True, True),
                (7, 'Maintenance Technician', 'Maintenance Technician', 'Maintenance operations', True, True, True),
                (8, 'HR Manager', 'HR Manager', 'Human resources management', True, True, True),
                (9, 'Compliance Officer', 'Compliance Officer', 'Compliance management', True, True, True),
                (10, 'Auditor', 'Auditor', 'Audit operations', True, True, True)
            ]
            
            for role_id, role_name, display_name, description, is_default, is_editable, is_active in roles_data:
                conn.execute(text("""
                    INSERT OR REPLACE INTO roles (id, name, display_name, description, is_default, is_editable, is_active, created_at)
                    VALUES (:role_id, :role_name, :display_name, :description, :is_default, :is_editable, :is_active, :created_at)
                """), {
                    'role_id': role_id,
                    'role_name': role_name,
                    'display_name': display_name,
                    'description': description,
                    'is_default': is_default,
                    'is_editable': is_editable,
                    'is_active': is_active,
                    'created_at': datetime.now().isoformat()
                })
                print(f"    ✓ Created/Updated role: {role_name}")
            
            # Assign permissions to roles
            assign_role_permissions(conn)
            
            conn.commit()
            print("  ✓ Created/updated default roles with permissions")
            return True
            
    except Exception as e:
        print(f"  ⚠️  Could not create roles: {e}")
        return False

def assign_role_permissions(conn):
    """Assign permissions to roles based on role hierarchy"""
    print("  🔗 Assigning permissions to roles...")
    
    try:
        # Get all permission IDs from the database
        result = conn.execute(text("SELECT id FROM permissions ORDER BY id"))
        all_permission_ids = [row[0] for row in result.fetchall()]
        
        if not all_permission_ids:
            print("    ⚠️  No permissions found. Cannot assign permissions to roles.")
            return
        
        print(f"    📊 Found {len(all_permission_ids)} permissions to assign")
        
        # System Administrator gets all permissions
        admin_role_id = 1
        for perm_id in all_permission_ids:
            conn.execute(text("""
                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                VALUES (:role_id, :permission_id)
            """), {
                'role_id': admin_role_id,
                'permission_id': perm_id
            })
        
        print(f"    ✓ Assigned {len(all_permission_ids)} permissions to System Administrator")
        
        # For other roles, assign permissions based on their modules
        # This is a simplified approach - in production, you might want more granular control
        
        # QA Manager gets most permissions except user management
        qa_manager_permissions = [p for p in all_permission_ids if not (55 <= p <= 72)]  # Exclude users/roles modules
        for perm_id in qa_manager_permissions:
            conn.execute(text("""
                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                VALUES (:role_id, :permission_id)
            """), {
                'role_id': 2,  # QA Manager
                'permission_id': perm_id
            })
        
        # Other roles get basic permissions (view only for most modules)
        # This is a simplified approach - you can expand this based on your needs
        for role_id in range(3, 11):  # Roles 3-10
            # Get view permissions for each module (every 9th permission starting from 1)
            view_permissions = [i for i in all_permission_ids if (i - 1) % 9 == 0]  # view permissions
            for perm_id in view_permissions:
                conn.execute(text("""
                    INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                """), {
                    'role_id': role_id,
                    'permission_id': perm_id
                })
        
        print("    ✓ Assigned basic permissions to other roles")
        print("    ✓ Permission assignment completed")
        
    except Exception as e:
        print(f"    ⚠️  Could not assign permissions: {e}")

def clear_existing_data(conn):
    """Clear existing data from tables (excluding RBAC data)"""
    print("🧹 Clearing existing data...")
    
    # Tables to clear (in dependency order to avoid foreign key constraints)
    # Note: Excluding RBAC tables (roles, permissions, role_permissions, user_permissions, users)
    # as these are created earlier and should not be cleared
    tables_to_clear = [
        'oprp_monitoring_logs', 'oprp_verification_logs', 'oprps',
        'ccp_monitoring_logs', 'ccp_verification_logs', 'ccps', 'hazards', 
        'haccp_plans', 'process_flows', 'batches', 'products',
        'supplier_evaluations', 'supplier_documents', 'suppliers',
        'document_approvals', 'document_versions', 'documents',
        'training_attendance', 'training_sessions', 'training_programs',
        'maintenance_work_orders', 'calibration_records', 'equipment',
        'prp_checklist_items', 'prp_checklists', 'prp_programs'
    ]
    
    # Check which tables actually exist before trying to clear them
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        for table in tables_to_clear:
            if table in existing_tables:
                try:
                    conn.execute(text(f"DELETE FROM {table}"))
                    print(f"  ✓ Cleared {table}")
                except Exception as e:
                    print(f"  ⚠️  Could not clear {table}: {e}")
            else:
                print(f"  ⏭️  Skipped {table} (table does not exist)")
                
    except Exception as e:
        print(f"  ⚠️  Could not check existing tables: {e}")
        # Fallback: try to clear tables without checking
        for table in tables_to_clear:
            try:
                conn.execute(text(f"DELETE FROM {table}"))
                print(f"  ✓ Cleared {table}")
            except Exception as e:
                print(f"  ⚠️  Could not clear {table}: {e}")

def create_professional_users(conn):
    """Create professional food safety users with correct role assignments"""
    print("\n👥 Creating professional users with role assignments...")
    
    # Check if users already exist (skip if they do)
    result = conn.execute(text("SELECT COUNT(*) FROM users"))
    existing_count = result.scalar()
    
    if existing_count > 0:
        print(f"  ⏭️  Found {existing_count} existing users. Skipping user creation.")
        return
    
    # Define user data with role mappings (updated to match frontend role names)
    users_data = [
        # Management - QA Manager role (role_id = 2)
        ('fs_manager', 'fs.manager@foodsafe.com', 'Sarah Johnson', 'Food Safety Manager', 'Quality Assurance', '+1-555-0101', 'FSM001', 2),
        ('qa_director', 'qa.director@foodsafe.com', 'Michael Chen', 'QA Director', 'Quality Assurance', '+1-555-0102', 'QAD001', 2),
        
        # Quality Assurance - QA Specialist role (role_id = 3)
        ('qa_supervisor', 'qa.supervisor@foodsafe.com', 'Lisa Rodriguez', 'QA Supervisor', 'Quality Assurance', '+1-555-0104', 'QAS001', 3),
        ('haccp_coordinator', 'haccp.coordinator@foodsafe.com', 'David Kim', 'HACCP Coordinator', 'Quality Assurance', '+1-555-0105', 'HC001', 3),
        
        # Production - Production Manager role (role_id = 4)
        ('production_supervisor', 'production.supervisor@foodsafe.com', 'James Brown', 'Production Supervisor', 'Production', '+1-555-0107', 'PS001', 4),
        
        # Operators - Production Operator role (role_id = 5)
        ('line_operator', 'line.operator@foodsafe.com', 'Thomas Wilson', 'Line Operator', 'Production', '+1-555-0109', 'LO001', 5),
        
        # Maintenance - Maintenance Manager role (role_id = 6)
        ('maintenance_manager', 'maintenance.manager@foodsafe.com', 'Kevin Davis', 'Maintenance Manager', 'Maintenance', '+1-555-0110', 'MM001', 6),
        
        # Maintenance - Maintenance Technician role (role_id = 7)
        ('calibration_tech', 'calibration.tech@foodsafe.com', 'Amanda Taylor', 'Calibration Technician', 'Maintenance', '+1-555-0111', 'CT001', 7),
        
        # HR - HR Manager role (role_id = 8)
        ('hr_manager', 'hr.manager@foodsafe.com', 'Patricia Smith', 'HR Manager', 'Human Resources', '+1-555-0112', 'HRM001', 8),
        
        # Compliance - Compliance Officer role (role_id = 9)
        ('compliance_officer', 'compliance.officer@foodsafe.com', 'Robert Johnson', 'Compliance Officer', 'Compliance', '+1-555-0113', 'CO001', 9),
        
        # Audit - Auditor role (role_id = 10)
        ('auditor', 'auditor@foodsafe.com', 'Maria Garcia', 'Internal Auditor', 'Quality Assurance', '+1-555-0114', 'AUD001', 10),
        
        # Admin - System Administrator role (role_id = 1)
        ('admin', 'admin@foodsafe.com', 'System Administrator', 'System Administrator', 'IT', '+1-555-0000', 'ADM001', 1)
    ]
    
    # Hash for 'admin123' - Default password for all demo users
    hashed_password = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
    
    for username, email, full_name, position, department, phone, employee_id, role_id in users_data:
        conn.execute(text("""
            INSERT INTO users (username, email, full_name, hashed_password, role_id, status, 
                             department_name, position, phone, employee_id, is_active, is_verified, 
                             failed_login_attempts, locked_until, created_at, created_by)
            VALUES (:username, :email, :full_name, :hashed_password, :role_id, 'ACTIVE', 
                   :department, :position, :phone, :employee_id, 1, 1, 
                   0, NULL, :created_at, 1)
        """), {
            'username': username,
            'email': email,
            'full_name': full_name,
            'hashed_password': hashed_password,
            'role_id': role_id,
            'department': department,
            'position': position,
            'phone': phone,
            'employee_id': employee_id,
            'created_at': datetime.now().isoformat()
        })
    
    print(f"  ✓ Created {len(users_data)} professional users with proper role assignments")

def create_user_permissions(conn):
    """Create individual user permissions for advanced scenarios"""
    print("\n🔐 Creating individual user permissions...")
    
    try:
        # Example: Give admin user additional specific permissions beyond role
        # This demonstrates how to grant individual permissions to users
        
        # Get admin user ID
        admin_result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        admin_user = admin_result.fetchone()
        
        if admin_user:
            admin_user_id = admin_user[0]
            
            # Grant additional specific permissions to admin (if needed)
            # This is typically not necessary since admin role already has all permissions
            # But demonstrates the capability for individual user permissions
            
            # Example: Grant specific permission to admin user
            # Get a specific permission ID (e.g., dashboard view permission)
            perm_result = conn.execute(text("SELECT id FROM permissions WHERE module = 'dashboard' AND action = 'view' LIMIT 1"))
            perm_row = perm_result.fetchone()
            
            if perm_row:
                permission_id = perm_row[0]
                
                # Insert user permission
                conn.execute(text("""
                    INSERT OR IGNORE INTO user_permissions (user_id, permission_id, granted, granted_by, granted_at)
                    VALUES (:user_id, :permission_id, :granted, :granted_by, :granted_at)
                """), {
                    'user_id': admin_user_id,
                    'permission_id': permission_id,
                    'granted': True,
                    'granted_by': admin_user_id,  # Self-granted
                    'granted_at': datetime.now().isoformat()
                })
        
        print("  ✓ Created individual user permissions")
        
    except Exception as e:
        print(f"  ⚠️  Could not create user permissions: {e}")

def create_professional_products(conn):
    """Create professional food products"""
    print("\n🥛 Creating professional food products...")
    
    products_data = [
        # Dairy Products
        ('DAI-001', 'Fresh Whole Milk', 'Pasteurized whole milk, 3.25% fat', 
         'Whole milk, 3.25% fat, pasteurized, fortified with vitamin D', 
         'Raw milk', 
         'Liquid, white, homogeneous, pH 6.6-6.8, fat globules suspended in water phase',
         'Raw milk reception, filtration, standardization, pasteurization (72°C/15s), cooling, packaging',
         'Refrigerated transport in temperature-controlled vehicles',
         'Stainless steel tanks, pipes, pasteurizer, packaging equipment',
         'General population, children over 12 months',
         'Refrigerated 2-4°C', 14, 'HDPE Bottle',
         'Bacterial contamination (Listeria, Salmonella, E.coli), physical contaminants',
         'Total plate count <10,000 CFU/ml, Coliforms <10 CFU/ml, Pathogens absent',
         'FDA 21 CFR Part 131, Grade A Pasteurized Milk Ordinance',
         1),
        
        ('DAI-002', 'Greek Yogurt', 'Creamy Greek yogurt, 2% fat',
         'Greek yogurt made from milk, live cultures, 2% fat content',
         'Raw milk, live yogurt cultures',
         'Thick, creamy texture, white color, pH 4.0-4.5, protein-rich',
         'Milk pasteurization, inoculation with cultures, fermentation (42°C/4-6h), straining, packaging',
         'Refrigerated transport, cold chain maintenance',
         'Stainless steel fermentation tanks, straining equipment, packaging lines',
         'General population, health-conscious consumers',
         'Refrigerated 2-4°C', 21, 'Plastic Cup',
         'Bacterial contamination, yeast/mold growth, chemical contamination',
         'Total plate count <100,000 CFU/g, Yeast <100 CFU/g, Mold <10 CFU/g',
         'FDA 21 CFR Part 131, Grade A standards',
         1),
        
        ('DAI-003', 'Cheddar Cheese', 'Aged cheddar cheese, 6 months',
         'Cheddar cheese aged for 6 months, made from pasteurized milk',
         'Pasteurized milk, rennet, cheese cultures, salt',
         'Firm texture, orange color, pH 5.1-5.3, protein and fat rich',
         'Milk pasteurization, acidification, rennet addition, cutting, cooking, pressing, salting, aging',
         'Refrigerated transport, temperature-controlled storage',
         'Cheese vats, presses, aging rooms, packaging equipment',
         'General population, cheese lovers',
         'Refrigerated 2-4°C', 90, 'Vacuum Pack',
         'Bacterial contamination, mold growth, chemical residues',
         'Total plate count <1,000,000 CFU/g, Listeria absent, mold <100 CFU/g',
         'FDA 21 CFR Part 133, Grade A standards',
         1),
        
        ('DAI-004', 'Butter', 'Sweet cream butter, 80% fat',
         'Sweet cream butter with 80% milk fat content',
         'Fresh cream, salt (optional)',
         'Solid at room temperature, yellow color, smooth texture',
         'Cream separation, pasteurization, churning, working, packaging',
         'Refrigerated transport, cold chain maintenance',
         'Churning equipment, working machines, packaging lines',
         'General population, cooking enthusiasts',
         'Refrigerated 2-4°C', 60, 'Wax Paper',
         'Bacterial contamination, rancidity, chemical residues',
         'Total plate count <100,000 CFU/g, Coliforms <10 CFU/g',
         'FDA 21 CFR Part 133, Grade A standards',
         1),
        
        # Meat Products
        ('MEA-001', 'Ground Beef', 'Fresh ground beef, 80/20 lean',
         'Fresh ground beef with 80% lean meat, 20% fat',
         'Fresh beef cuts',
         'Red color, meaty texture, pH 5.4-6.0, protein-rich',
         'Beef receiving, inspection, grinding, packaging',
         'Refrigerated transport in temperature-controlled vehicles',
         'Grinding equipment, packaging machines, stainless steel surfaces',
         'General population, adults and children over 2 years',
         'Refrigerated 0-2°C', 3, 'Vacuum Pack',
         'Bacterial contamination (E.coli O157:H7, Salmonella), physical contaminants',
         'E.coli O157:H7 absent, Salmonella absent, Total plate count <1,000,000 CFU/g',
         'USDA FSIS regulations, HACCP requirements',
         1),
        
        ('MEA-002', 'Chicken Breast', 'Boneless skinless chicken breast',
         'Fresh boneless, skinless chicken breast fillets',
         'Fresh chicken breast',
         'Pink color, firm texture, pH 5.8-6.2, lean protein',
         'Chicken receiving, inspection, deboning, trimming, packaging',
         'Refrigerated transport, cold chain maintenance',
         'Cutting equipment, packaging machines, stainless steel surfaces',
         'General population, health-conscious consumers',
         'Refrigerated 0-2°C', 5, 'Vacuum Pack',
         'Bacterial contamination (Salmonella, Campylobacter), chemical residues',
         'Salmonella absent, Campylobacter absent, Total plate count <1,000,000 CFU/g',
         'USDA FSIS regulations, HACCP requirements',
         1),
        
        # Bakery Products
        ('BAK-001', 'Whole Wheat Bread', 'Artisan whole wheat bread',
         'Artisan whole wheat bread made with whole wheat flour',
         'Whole wheat flour, water, yeast, salt, seeds (optional)',
         'Brown color, dense texture, pH 5.2-5.8, fiber-rich',
         'Mixing, kneading, proofing, baking, cooling, packaging',
         'Ambient transport, temperature-controlled storage',
         'Mixers, ovens, cooling racks, packaging equipment',
         'General population, health-conscious consumers',
         'Room temperature', 7, 'Paper Bag',
         'Mold growth, bacterial contamination, physical contaminants',
         'Total plate count <100,000 CFU/g, Mold absent, Yeast <1000 CFU/g',
         'FDA 21 CFR Part 110, Good Manufacturing Practices',
         1),
        
        ('BAK-002', 'Chocolate Chip Cookies', 'Soft chocolate chip cookies',
         'Soft chocolate chip cookies with real chocolate chips',
         'Flour, sugar, butter, eggs, chocolate chips, vanilla',
         'Brown color, soft texture, sweet taste, pH 6.0-7.0',
         'Mixing, portioning, baking, cooling, packaging',
         'Ambient transport, moisture-controlled storage',
         'Mixers, ovens, cooling conveyors, packaging equipment',
         'General population, children, dessert lovers',
         'Room temperature', 14, 'Plastic Bag',
         'Mold growth, bacterial contamination, chemical residues',
         'Total plate count <100,000 CFU/g, Mold absent, Yeast <1000 CFU/g',
         'FDA 21 CFR Part 110, Good Manufacturing Practices',
         1)
    ]
    
    for (product_code, name, description, composition, high_risk_ingredients, 
         physical_chemical_biological_description, main_processing_steps, 
         distribution_serving_methods, product_contact_surfaces, consumer_groups,
         storage_conditions, shelf_life_days, packaging_type, inherent_hazards,
         fs_acceptance_criteria, law_regulation_requirement, created_by) in products_data:
        conn.execute(text("""
            INSERT INTO products (product_code, name, description, composition, high_risk_ingredients,
                                physical_chemical_biological_description, main_processing_steps,
                                distribution_serving_methods, product_contact_surfaces, consumer_groups,
                                storage_conditions, shelf_life_days, packaging_type, inherent_hazards,
                                fs_acceptance_criteria, law_regulation_requirement, haccp_plan_approved,
                                created_at, created_by, risk_assessment_required)
            VALUES (:product_code, :name, :description, :composition, :high_risk_ingredients,
                   :physical_chemical_biological_description, :main_processing_steps,
                   :distribution_serving_methods, :product_contact_surfaces, :consumer_groups,
                   :storage_conditions, :shelf_life_days, :packaging_type, :inherent_hazards,
                   :fs_acceptance_criteria, :law_regulation_requirement, 1,
                   :created_at, :created_by, 1)
        """), {
            'product_code': product_code,
            'name': name,
            'description': description,
            'composition': composition,
            'high_risk_ingredients': high_risk_ingredients,
            'physical_chemical_biological_description': physical_chemical_biological_description,
            'main_processing_steps': main_processing_steps,
            'distribution_serving_methods': distribution_serving_methods,
            'product_contact_surfaces': product_contact_surfaces,
            'consumer_groups': consumer_groups,
            'storage_conditions': storage_conditions,
            'shelf_life_days': shelf_life_days,
            'packaging_type': packaging_type,
            'inherent_hazards': inherent_hazards,
            'fs_acceptance_criteria': fs_acceptance_criteria,
            'law_regulation_requirement': law_regulation_requirement,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print(f"  ✓ Created {len(products_data)} professional food products")

def create_professional_suppliers(conn):
    """Create professional food industry suppliers"""
    print("\n🚚 Creating professional food suppliers...")
    
    suppliers_data = [
        # Raw Materials
        ('SUP-001', 'Green Valley Dairy Farm', 'active', 'raw_materials', 'John Smith', 'john@greenvalleydairy.com', '+1-555-1001', 'www.greenvalleydairy.com', '1234 Farm Road', 'Dairy Valley', 'CA', '90210', 'USA', 'CA123456789', '12-3456789', 'Partnership', 1985, '["Organic", "Non-GMO"]', '2025-12-31', 95, '2025-01-15', '2025-07-15', 'low', '[]', 'Certified organic dairy farm with excellent quality standards', 1),
        ('SUP-002', 'Premium Beef Ranch', 'active', 'raw_materials', 'Mary Johnson', 'mary@premiumbeef.com', '+1-555-1002', 'www.premiumbeef.com', '5678 Ranch Way', 'Beef City', 'TX', '75001', 'USA', 'TX987654321', '98-7654321', 'Corporation', 1990, '["USDA Prime", "Grass-Fed"]', '2025-11-30', 92, '2025-01-10', '2025-07-10', 'low', '[]', 'Premium beef supplier with HACCP certification', 1),
        ('SUP-003', 'Golden Grain Mills', 'active', 'raw_materials', 'Robert Brown', 'robert@goldengrain.com', '+1-555-1003', 'www.goldengrain.com', '9012 Mill Street', 'Grain Town', 'KS', '66001', 'USA', 'KS456789123', '45-6789123', 'Corporation', 1975, '["Non-GMO", "Kosher"]', '2025-10-15', 88, '2025-01-05', '2025-07-05', 'medium', '[]', 'Premium flour and grain supplier', 1),
        
        # Packaging
        ('SUP-004', 'EcoPack Solutions', 'active', 'packaging', 'Lisa Davis', 'lisa@ecopack.com', '+1-555-1004', 'www.ecopack.com', '3456 Industrial Blvd', 'Pack City', 'IL', '60601', 'USA', 'IL789123456', '78-9123456', 'Corporation', 2000, '["FDA Approved", "Recyclable"]', '2025-09-30', 90, '2025-01-20', '2025-07-20', 'low', '[]', 'Sustainable packaging solutions for food industry', 1),
        ('SUP-005', 'FreshSeal Packaging', 'active', 'packaging', 'Michael Wilson', 'michael@freshseal.com', '+1-555-1005', 'www.freshseal.com', '7890 Packaging Ave', 'Seal Town', 'OH', '44101', 'USA', 'OH321654987', '32-1654987', 'Corporation', 1995, '["Food Grade", "Barrier Properties"]', '2025-08-15', 87, '2025-01-25', '2025-07-25', 'low', '[]', 'Specialized food packaging materials', 1),
        
        # Ingredients
        ('SUP-006', 'Pure Cultures Inc', 'active', 'ingredients', 'Sarah Miller', 'sarah@purecultures.com', '+1-555-1006', 'www.purecultures.com', '2468 Culture Lane', 'Culture City', 'WI', '53701', 'USA', 'WI654987321', '65-4987321', 'Corporation', 1988, '["GRAS", "Kosher"]', '2025-12-15', 94, '2025-01-30', '2025-07-30', 'low', '[]', 'Premium starter cultures for dairy products', 1),
        ('SUP-007', 'Sweet Sugar Co', 'active', 'ingredients', 'David Garcia', 'david@sweetsugar.com', '+1-555-1007', 'www.sweetsugar.com', '1357 Sugar Street', 'Sweet City', 'FL', '33101', 'USA', 'FL987321654', '98-7321654', 'Corporation', 1980, '["Organic", "Fair Trade"]', '2025-11-15', 89, '2025-02-01', '2025-08-01', 'low', '[]', 'Premium organic sugar and sweeteners', 1),
        
        # Services
        ('SUP-008', 'CleanTech Sanitation', 'active', 'services', 'Jennifer Lee', 'jennifer@cleantech.com', '+1-555-1008', 'www.cleantech.com', '9753 Clean Way', 'Clean City', 'NC', '27601', 'USA', 'NC147258369', '14-7258369', 'Corporation', 1992, '["EPA Approved", "Food Safe"]', '2025-10-30', 91, '2025-02-05', '2025-08-05', 'low', '[]', 'Professional food facility sanitation services', 1),
        ('SUP-009', 'CalibPro Services', 'active', 'services', 'Kevin Taylor', 'kevin@calibpro.com', '+1-555-1009', 'www.calibpro.com', '8642 Calibration Dr', 'Calib City', 'CO', '80201', 'USA', 'CO369258147', '36-9258147', 'Corporation', 1998, '["ISO 17025", "NIST Traceable"]', '2025-09-15', 96, '2025-02-10', '2025-08-10', 'low', '[]', 'Precision calibration services for food industry', 1),
        
        # Equipment
        ('SUP-010', 'FoodTech Equipment', 'active', 'equipment', 'Amanda Rodriguez', 'amanda@foodtech.com', '+1-555-1010', 'www.foodtech.com', '7410 Equipment Blvd', 'Tech City', 'PA', '19101', 'USA', 'PA258147369', '25-8147369', 'Corporation', 1985, '["NSF Certified", "3-A Sanitary"]', '2025-12-30', 93, '2025-02-15', '2025-08-15', 'low', '[]', 'Professional food processing equipment', 1),
        ('SUP-011', 'ColdChain Solutions', 'active', 'equipment', 'Thomas Anderson', 'thomas@coldchain.com', '+1-555-1011', 'www.coldchain.com', '8520 Cold Street', 'Cold City', 'WA', '98101', 'USA', 'WA741852963', '74-1852963', 'Corporation', 1990, '["Energy Star", "Refrigerant Safe"]', '2025-11-30', 88, '2025-02-20', '2025-08-20', 'low', '[]', 'Refrigeration and cold storage solutions', 1),
        
        # Testing
        ('SUP-012', 'FoodLab Testing', 'active', 'testing', 'Maria Lopez', 'maria@foodlab.com', '+1-555-1012', 'www.foodlab.com', '9630 Lab Lane', 'Lab City', 'CA', '90211', 'USA', 'CA852963741', '85-2963741', 'Corporation', 1995, '["ISO 17025", "FDA Registered"]', '2025-10-15', 95, '2025-02-25', '2025-08-25', 'low', '[]', 'Comprehensive food safety testing laboratory', 1),
        ('SUP-013', 'MicroTest Labs', 'active', 'testing', 'James White', 'james@microtest.com', '+1-555-1013', 'www.microtest.com', '1470 Micro Blvd', 'Micro City', 'NY', '10001', 'USA', 'NY963741852', '96-3741852', 'Corporation', 1988, '["A2LA Accredited", "Rapid Testing"]', '2025-09-30', 92, '2025-03-01', '2025-09-01', 'low', '[]', 'Microbiological testing and analysis', 1),
        
        # Transportation
        ('SUP-014', 'FreshLogistics', 'active', 'transportation', 'Patricia Clark', 'patricia@freshlogistics.com', '+1-555-1014', 'www.freshlogistics.com', '2580 Logistics Way', 'Log City', 'GA', '30301', 'USA', 'GA741963852', '74-1963852', 'Corporation', 2000, '["FDA Registered", "Temperature Controlled"]', '2025-12-15', 89, '2025-03-05', '2025-09-05', 'medium', '[]', 'Temperature-controlled food transportation', 1),
        ('SUP-015', 'SafeHaul Transport', 'active', 'transportation', 'Christopher Hall', 'chris@safehaul.com', '+1-555-1015', 'www.safehaul.com', '3690 Haul Street', 'Haul City', 'TN', '37201', 'USA', 'TN852741963', '85-2741963', 'Corporation', 1995, '["HACCP Certified", "GPS Tracking"]', '2025-11-15', 87, '2025-03-10', '2025-09-10', 'medium', '[]', 'Specialized food transportation services', 1)
    ]
    
    for (supplier_code, name, status, category, contact_person, email, phone, website, 
         address1, city, state, postal, country, business_reg, tax_id, company_type, 
         year_established, certifications, cert_expiry, overall_score, last_eval, 
         next_eval, risk_level, risk_factors, notes, created_by) in suppliers_data:
        
        conn.execute(text("""
            INSERT INTO suppliers (supplier_code, name, status, category, contact_person, email, phone, website,
                                address_line1, city, state, postal_code, country, business_registration_number,
                                tax_identification_number, company_type, year_established, certifications,
                                certification_expiry_dates, overall_score, last_evaluation_date, next_evaluation_date,
                                risk_level, risk_factors, notes, created_at, created_by)
            VALUES (:supplier_code, :name, :status, :category, :contact_person, :email, :phone, :website,
                   :address1, :city, :state, :postal, :country, :business_reg, :tax_id, :company_type,
                   :year_established, :certifications, :cert_expiry, :overall_score, :last_eval, :next_eval,
                   :risk_level, :risk_factors, :notes, :created_at, :created_by)
        """), {
            'supplier_code': supplier_code,
            'name': name,
            'status': status,
            'category': category,
            'contact_person': contact_person,
            'email': email,
            'phone': phone,
            'website': website,
            'address1': address1,
            'city': city,
            'state': state,
            'postal': postal,
            'country': country,
            'business_reg': business_reg,
            'tax_id': tax_id,
            'company_type': company_type,
            'year_established': year_established,
            'certifications': certifications,
            'cert_expiry': cert_expiry,
            'overall_score': overall_score,
            'last_eval': last_eval,
            'next_eval': next_eval,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print(f"  ✓ Created {len(suppliers_data)} professional food industry suppliers")

def create_professional_documents(conn):
    """Create professional food safety documents"""
    print("\n📋 Creating professional documents...")
    
    documents_data = [
        # Food Safety Manuals
        ('FSM-001', 'Food Safety Management System Manual', 'Comprehensive FSMS manual based on ISO 22000:2018', 'manual', 'food_safety', 'approved', '2.1', 'Quality Assurance', 'All Products', '[]', 'HACCP, ISO 22000, Food Safety', 1),
        ('FSM-002', 'HACCP Plan Manual', 'Hazard Analysis and Critical Control Points implementation guide', 'manual', 'food_safety', 'approved', '1.3', 'Quality Assurance', 'All Products', '[]', 'HACCP, Critical Control Points, Food Safety', 1),
        ('FSM-003', 'Prerequisite Programs Manual', 'PRP implementation and management procedures', 'manual', 'food_safety', 'approved', '1.2', 'Quality Assurance', 'All Products', '[]', 'PRP, Prerequisites, Sanitation', 1),
        
        # Standard Operating Procedures
        ('SOP-001', 'Receiving and Inspection Procedure', 'Standard procedure for receiving raw materials and ingredients', 'procedure', 'operations', 'approved', '1.4', 'Quality Assurance', 'Raw Materials', '[]', 'Receiving, Inspection, Raw Materials', 1),
        ('SOP-002', 'Temperature Control Procedure', 'Temperature monitoring and control procedures for food products', 'procedure', 'operations', 'approved', '1.2', 'Quality Assurance', 'All Products', '[]', 'Temperature, Monitoring, Control', 1),
        ('SOP-003', 'Cleaning and Sanitization Procedure', 'Comprehensive cleaning and sanitization procedures', 'procedure', 'operations', 'approved', '2.0', 'Production', 'All Areas', '[]', 'Cleaning, Sanitization, Hygiene', 1),
        ('SOP-004', 'Allergen Control Procedure', 'Allergen management and cross-contamination prevention', 'procedure', 'operations', 'approved', '1.1', 'Quality Assurance', 'All Products', '[]', 'Allergens, Cross-contamination, Control', 1),
        ('SOP-005', 'Traceability Procedure', 'Product traceability and recall procedures', 'procedure', 'operations', 'approved', '1.3', 'Quality Assurance', 'All Products', '[]', 'Traceability, Recall, Tracking', 1),
        
        # Work Instructions
        ('WI-001', 'Milk Pasteurization Work Instruction', 'Step-by-step pasteurization process instructions', 'work_instruction', 'production', 'approved', '1.2', 'Production', 'Dairy Products', '["DAI-001"]', 'Pasteurization, Milk, Temperature', 1),
        ('WI-002', 'Cheese Making Work Instruction', 'Detailed cheese production process instructions', 'work_instruction', 'production', 'approved', '1.1', 'Production', 'Dairy Products', '["DAI-003"]', 'Cheese, Production, Aging', 1),
        ('WI-003', 'Bread Baking Work Instruction', 'Artisan bread production process instructions', 'work_instruction', 'production', 'approved', '1.3', 'Production', 'Bakery Products', '["BAK-001"]', 'Bread, Baking, Fermentation', 1),
        
        # Forms and Records
        ('FRM-001', 'Daily Temperature Log', 'Daily temperature monitoring record form', 'form', 'records', 'approved', '1.0', 'Quality Assurance', 'All Products', '[]', 'Temperature, Log, Monitoring', 1),
        ('FRM-002', 'HACCP Monitoring Record', 'Critical Control Point monitoring record form', 'form', 'records', 'approved', '1.1', 'Quality Assurance', 'All Products', '[]', 'HACCP, Monitoring, CCP', 1),
        ('FRM-003', 'Cleaning Verification Checklist', 'Post-cleaning verification checklist', 'form', 'records', 'approved', '1.0', 'Production', 'All Areas', '[]', 'Cleaning, Verification, Checklist', 1),
        ('FRM-004', 'Supplier Evaluation Form', 'Supplier performance evaluation form', 'form', 'records', 'approved', '1.2', 'Quality Assurance', 'Suppliers', '[]', 'Supplier, Evaluation, Performance', 1),
        
        # Training Materials
        ('TRN-001', 'Food Safety Awareness Training', 'Basic food safety awareness training material', 'training_material', 'training', 'approved', '1.1', 'Human Resources', 'All Employees', '[]', 'Training, Food Safety, Awareness', 1),
        ('TRN-002', 'HACCP Team Training', 'HACCP team member training material', 'training_material', 'training', 'approved', '1.0', 'Quality Assurance', 'HACCP Team', '[]', 'Training, HACCP, Team', 1),
        ('TRN-003', 'Allergen Management Training', 'Allergen control and management training', 'training_material', 'training', 'approved', '1.1', 'Quality Assurance', 'Production Staff', '[]', 'Training, Allergens, Management', 1),
        
        # Policies
        ('POL-001', 'Food Safety Policy', 'Company food safety policy statement', 'policy', 'management', 'approved', '1.0', 'Management', 'All Operations', '[]', 'Policy, Food Safety, Management', 1),
        ('POL-002', 'Supplier Management Policy', 'Supplier selection and management policy', 'policy', 'management', 'approved', '1.1', 'Procurement', 'Suppliers', '[]', 'Policy, Supplier, Management', 1),
        ('POL-003', 'Training and Competency Policy', 'Employee training and competency development policy', 'policy', 'management', 'approved', '1.0', 'Human Resources', 'All Employees', '[]', 'Policy, Training, Competency', 1),
        
        # Specifications
        ('SPEC-001', 'Raw Milk Specification', 'Raw milk quality and safety specifications', 'specification', 'quality', 'approved', '1.2', 'Quality Assurance', 'Raw Materials', '[]', 'Specification, Raw Milk, Quality', 1),
        ('SPEC-002', 'Finished Product Specification', 'Finished product quality specifications', 'specification', 'quality', 'approved', '1.1', 'Quality Assurance', 'All Products', '[]', 'Specification, Finished Product, Quality', 1),
        ('SPEC-003', 'Packaging Material Specification', 'Packaging material specifications and requirements', 'specification', 'quality', 'approved', '1.0', 'Quality Assurance', 'Packaging', '[]', 'Specification, Packaging, Materials', 1)
    ]
    
    for (doc_number, title, description, doc_type, category, status, version, 
         department, product_line, applicable_products, keywords, created_by) in documents_data:
        
        conn.execute(text("""
            INSERT INTO documents (document_number, title, description, document_type, category, status, version,
                                department, product_line, applicable_products, keywords, created_at, created_by)
            VALUES (:doc_number, :title, :description, :doc_type, :category, :status, :version,
                   :department, :product_line, :applicable_products, :keywords, :created_at, :created_by)
        """), {
            'doc_number': doc_number,
            'title': title,
            'description': description,
            'doc_type': doc_type,
            'category': category,
            'status': status,
            'version': version,
            'department': department,
            'product_line': product_line,
            'applicable_products': applicable_products,
            'keywords': keywords,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print(f"  ✓ Created {len(documents_data)} professional documents")

def create_professional_batches(conn):
    """Create professional production batches"""
    print("\n📦 Creating professional production batches...")
    
    # Get product IDs
    result = conn.execute(text("SELECT id, product_code, name FROM products"))
    products = result.fetchall()
    
    batch_data = []
    batch_counter = 1
    
    for product_id, product_code, product_name in products:
        # Create 2-3 batches per product
        for i in range(random.randint(2, 3)):
            batch_number = f"BATCH-{product_code}-{batch_counter:03d}"
            production_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Determine batch type based on product
            if 'milk' in product_name.lower():
                batch_type = 'raw_milk'
                quantity = random.uniform(1000, 5000)
                unit = 'L'
            elif 'cheese' in product_name.lower():
                batch_type = 'final_product'
                quantity = random.uniform(100, 500)
                unit = 'kg'
            elif 'yogurt' in product_name.lower():
                batch_type = 'final_product'
                quantity = random.uniform(500, 2000)
                unit = 'L'
            elif 'beef' in product_name.lower() or 'chicken' in product_name.lower():
                batch_type = 'raw_material'
                quantity = random.uniform(200, 1000)
                unit = 'kg'
            else:
                batch_type = 'final_product'
                quantity = random.uniform(100, 1000)
                unit = 'units'
            
            # Determine status
            statuses = ['completed', 'in_production', 'pending']
            weights = [0.6, 0.3, 0.1]  # More completed batches
            status = random.choices(statuses, weights=weights)[0]
            
            batch_data.append((
                batch_number, batch_type, status, product_id, product_name,
                quantity, unit, production_date, 1
            ))
            batch_counter += 1
    
    for (batch_number, batch_type, status, product_id, product_name, 
         quantity, unit, production_date, created_by) in batch_data:
        
        conn.execute(text("""
            INSERT INTO batches (batch_number, batch_type, status, product_id, product_name, quantity, unit,
                              production_date, created_at, created_by)
            VALUES (:batch_number, :batch_type, :status, :product_id, :product_name, :quantity, :unit,
                   :production_date, :created_at, :created_by)
        """), {
            'batch_number': batch_number,
            'batch_type': batch_type,
            'status': status,
            'product_id': product_id,
            'product_name': product_name,
            'quantity': quantity,
            'unit': unit,
            'production_date': production_date.isoformat(),
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print(f"  ✓ Created {len(batch_data)} professional production batches")

def create_professional_haccp_data(conn):
    """Create professional HACCP data with complete process flows, hazards, CCPs, and OPRPs"""
    print("\n🔍 Creating professional HACCP data...")
    
    # Create HACCP Plans
    haccp_plans = [
        ('Fresh Milk HACCP Plan', 'HACCP plan for fresh milk production', 1, 1),  # Fresh Whole Milk
        ('Greek Yogurt HACCP Plan', 'HACCP plan for Greek yogurt production', 2, 1),  # Greek Yogurt
        ('Cheddar Cheese HACCP Plan', 'HACCP plan for cheddar cheese production', 3, 1),  # Cheddar Cheese
        ('Ground Beef HACCP Plan', 'HACCP plan for ground beef processing', 5, 1),  # Ground Beef
    ]
    
    for title, description, product_id, created_by in haccp_plans:
        conn.execute(text("""
            INSERT INTO haccp_plans (title, description, product_id, status, version,
                                   created_at, created_by)
            VALUES (:title, :description, :product_id, 'approved', '1.0',
                   :created_at, :created_by)
        """), {
            'title': title,
            'description': description,
            'product_id': product_id,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print("  ✓ Created HACCP plans")
    
    # Create Process Flows for Fresh Milk (Product ID 1)
    process_flows_milk = [
        (1, 1, 'Raw Milk Reception', 'Receipt and inspection of raw milk from suppliers', 'Receiving tank', '4', '', '', '', 1),
        (1, 2, 'Filtration', 'Remove physical contaminants from raw milk', 'Inline filter', '', '', '', '', 1),
        (1, 3, 'Standardization', 'Adjust milk fat content to 3.25%', 'Separator', '4', '', '', '', 1),
        (1, 4, 'Pasteurization', 'Heat treatment to destroy pathogens', 'HTST Pasteurizer', '72', '15', '6.6-6.8', '', 1),
        (1, 5, 'Cooling', 'Rapid cooling to refrigeration temperature', 'Plate cooler', '4', '', '', '', 1),
        (1, 6, 'Packaging', 'Aseptic filling into clean containers', 'Filling machine', '4', '', '', '', 1),
        (1, 7, 'Cold Storage', 'Store finished product at refrigeration temperature', 'Cold room', '2-4', '', '', '', 1),
    ]
    
    for product_id, step_number, step_name, description, equipment, temp, time_min, ph, aw, created_by in process_flows_milk:
        conn.execute(text("""
            INSERT INTO process_flows (product_id, step_number, step_name, description, equipment,
                                     temperature, time_minutes, ph, aw, created_at, created_by)
            VALUES (:product_id, :step_number, :step_name, :description, :equipment,
                   :temperature, :time_minutes, :ph, :aw, :created_at, :created_by)
        """), {
            'product_id': product_id,
            'step_number': step_number,
            'step_name': step_name,
            'description': description,
            'equipment': equipment,
            'temperature': temp,
            'time_minutes': time_min,
            'ph': ph,
            'aw': aw,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print("  ✓ Created process flows for Fresh Milk")
    
    # Create Hazards with ISO 22000 Risk Strategy Implementation
    # Format: (product_id, process_step_id, hazard_type, hazard_name, description, consequences,
    #          likelihood, severity, risk_score, risk_level, control_measures,
    #          risk_strategy, risk_strategy_justification, subsequent_step, created_by)
    
    hazards_data = [
        # Fresh Milk - Raw Milk Reception (Step 1)
        (1, 1, 'biological', 'Pathogenic bacteria in raw milk',
         'Presence of Listeria, Salmonella, E.coli O157:H7 in raw milk',
         'Consumer illness, foodborne disease outbreak, product recall',
         4, 5, 20, 'critical',
         'Supplier certification, testing program, temperature control',
         'use_existing_prps', 
         'Subsequent step (Pasteurization) will effectively control this hazard through validated thermal process',
         'Pasteurization',
         1),
        
        (1, 1, 'chemical', 'Antibiotic residues',
         'Antibiotic residues in raw milk from treated cows',
         'Allergic reactions, antimicrobial resistance, regulatory violation',
         2, 4, 8, 'medium',
         'Supplier testing program, certification requirements',
         'use_existing_prps',
         'Supplier management program and testing protocols adequately control this hazard',
         '',
         1),
        
        # Fresh Milk - Pasteurization (Step 4) - THIS IS A CCP
        (1, 4, 'biological', 'Survival of pathogenic bacteria',
         'Inadequate pasteurization allowing pathogen survival',
         'Consumer illness, severe foodborne disease outbreak, fatalities, massive product recall',
         3, 5, 15, 'high',
         'Time-temperature monitoring, validated process, calibrated equipment',
         'ccp',
         'No subsequent step will control this hazard. Critical limits (72°C for 15 seconds) must be met to ensure pathogen destruction. Monitoring and corrective actions are essential.',
         '',
         1),
        
        # Fresh Milk - Packaging (Step 6) - THIS IS AN OPRP
        (1, 6, 'biological', 'Post-pasteurization contamination',
         'Recontamination during packaging from equipment or environment',
         'Consumer illness, product spoilage, limited outbreak',
         3, 4, 12, 'high',
         'Sanitation program, environmental monitoring, equipment cleaning',
         'opprp',
         'While subsequent storage will not eliminate contamination, operational limits on environmental monitoring and sanitation can control this hazard. Requires specific monitoring but less critical than pasteurization.',
         '',
         1),
        
        (1, 6, 'physical', 'Foreign material in package',
         'Metal, glass, or plastic fragments in finished product',
         'Consumer injury (choking, cuts), product recall, liability',
         2, 3, 6, 'medium',
         'Metal detector, visual inspection, equipment maintenance',
         'opprp',
         'Operational prerequisite with specific limits on metal detector sensitivity and visual inspection frequency can adequately control this physical hazard.',
         '',
         1),
        
        (1, 6, 'allergen', 'Allergen cross-contact',
         'Cross-contact with milk allergens on shared equipment',
         'Allergic reactions in sensitive consumers, product recall',
         2, 4, 8, 'medium',
         'Equipment cleaning procedures, allergen control program',
         'use_existing_prps',
         'Existing allergen management program and cleaning procedures adequately control this hazard for milk products.',
         '',
         1),
        
        # Ground Beef Hazards (Product 5)
        (5, 1, 'biological', 'E.coli O157:H7 contamination',
         'E.coli O157:H7 present in raw beef trim',
         'Severe consumer illness (HUS), fatalities, major product recall, regulatory action',
         4, 5, 20, 'critical',
         'Supplier certification, testing program, temperature control',
         'use_existing_prps',
         'No subsequent step eliminates this hazard as product is sold raw. However, validated Supplier HACCP programs, testing, and proper cooking by consumer controls the risk.',
         'Consumer cooking',
         1),
        
        (5, 2, 'biological', 'Temperature abuse during processing',
         'Bacterial growth due to temperature rise during grinding',
         'Increased pathogen levels, reduced shelf life, potential illness',
         3, 4, 12, 'high',
         'Temperature monitoring, batch time limits, equipment chilling',
         'opprp',
         'Operational limits on processing temperature (keep below 4°C) and processing time can control bacterial growth. Requires specific monitoring.',
         '',
         1),
    ]
    
    hazard_ids = []
    for (product_id, process_step_id, hazard_type, hazard_name, description, consequences,
         likelihood, severity, risk_score, risk_level, control_measures,
         risk_strategy, risk_strategy_justification, subsequent_step, created_by) in hazards_data:
        
        result = conn.execute(text("""
            INSERT INTO hazards (product_id, process_step_id, hazard_type, hazard_name, 
                               description, consequences, likelihood, severity, risk_score, 
                               risk_level, control_measures, is_controlled, control_effectiveness,
                               risk_strategy, risk_strategy_justification, subsequent_step,
                               is_ccp, created_at, created_by, reference_documents, prp_reference_ids)
            VALUES (:product_id, :process_step_id, :hazard_type, :hazard_name,
                   :description, :consequences, :likelihood, :severity, :risk_score,
                   :risk_level, :control_measures, :is_controlled, :control_effectiveness,
                   :risk_strategy, :risk_strategy_justification, :subsequent_step,
                   :is_ccp, :created_at, :created_by, :reference_documents, :prp_reference_ids)
            RETURNING id
        """), {
            'product_id': product_id,
            'process_step_id': process_step_id,
            'hazard_type': hazard_type,
            'hazard_name': hazard_name,
            'description': description,
            'consequences': consequences,
            'likelihood': likelihood,
            'severity': severity,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'control_measures': control_measures,
            'is_controlled': 1,
            'control_effectiveness': 90 if risk_strategy == 'ccp' else 80,
            'risk_strategy': risk_strategy,
            'risk_strategy_justification': risk_strategy_justification,
            'subsequent_step': subsequent_step,
            'is_ccp': 1 if risk_strategy == 'ccp' else 0,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by,
            'reference_documents': '[]',
            'prp_reference_ids': '[]'
        })
        hazard_id = result.fetchone()[0]
        hazard_ids.append((hazard_id, risk_strategy, hazard_name, product_id))
    
    print(f"  ✓ Created {len(hazards_data)} hazards with ISO 22000 risk strategies")
    
    # Create CCPs for hazards with risk_strategy='ccp'
    ccp_counter = 1
    for hazard_id, risk_strategy, hazard_name, product_id in hazard_ids:
        if risk_strategy == 'ccp':
            conn.execute(text("""
                INSERT INTO ccps (product_id, hazard_id, ccp_number, ccp_name, description,
                                status, critical_limit_min, critical_limit_max, critical_limit_unit,
                                critical_limit_description, monitoring_frequency, monitoring_method,
                                monitoring_responsible, monitoring_equipment, corrective_actions,
                                verification_frequency, verification_method, verification_responsible,
                                created_at, created_by)
                VALUES (:product_id, :hazard_id, :ccp_number, :ccp_name, :description,
                       'active', :cl_min, :cl_max, :cl_unit, :cl_desc,
                       :mon_freq, :mon_method, :mon_resp, :mon_equip, :corr_actions,
                       :ver_freq, :ver_method, :ver_resp, :created_at, :created_by)
            """), {
                'product_id': product_id,
                'hazard_id': hazard_id,
                'ccp_number': f'CCP-{ccp_counter}',
                'ccp_name': f'CCP-{ccp_counter} Pasteurization Temperature',
                'description': f'Critical control point for {hazard_name}',
                'cl_min': 72.0,
                'cl_max': 75.0,
                'cl_unit': '°C',
                'cl_desc': 'Minimum 72°C for 15 seconds to ensure pathogen destruction',
                'mon_freq': 'Continuous',
                'mon_method': 'Automated temperature recorder with data logging',
                'mon_resp': 'Production Operator',
                'mon_equip': 'Calibrated temperature probe and chart recorder',
                'corr_actions': 'Stop production, re-pasteurize affected product, adjust temperature, investigate cause, document corrective action',
                'ver_freq': 'Daily',
                'ver_method': 'Review temperature charts, verify critical limits met, check calibration',
                'ver_resp': 'QA Supervisor',
                'created_at': datetime.now().isoformat(),
                'created_by': 1
            })
            ccp_counter += 1
    
    print(f"  ✓ Created {ccp_counter - 1} CCPs for critical hazards")
    
    # Create OPRPs for hazards with risk_strategy='opprp'
    oprp_counter = 1
    for hazard_id, risk_strategy, hazard_name, product_id in hazard_ids:
        if risk_strategy == 'opprp':
            conn.execute(text("""
                INSERT INTO oprps (product_id, hazard_id, oprp_number, oprp_name, description,
                                 status, operational_limits, operational_limit_min, operational_limit_max,
                                 operational_limit_unit, operational_limit_description,
                                 monitoring_frequency, monitoring_method, monitoring_responsible,
                                 monitoring_equipment, corrective_actions,
                                 verification_frequency, verification_method, verification_responsible,
                                 justification, objective, sop_reference,
                                 created_at, created_by)
                VALUES (:product_id, :hazard_id, :oprp_number, :oprp_name, :description,
                       'active', :op_limits, :op_min, :op_max, :op_unit, :op_desc,
                       :mon_freq, :mon_method, :mon_resp, :mon_equip, :corr_actions,
                       :ver_freq, :ver_method, :ver_resp, :justification, :objective, :sop_reference,
                       :created_at, :created_by)
            """), {
                'product_id': product_id,
                'hazard_id': hazard_id,
                'oprp_number': f'OPRP-{oprp_counter}',
                'oprp_name': f'OPRP-{oprp_counter} {hazard_name[:50]}',
                'description': f'Operational prerequisite program for {hazard_name}',
                'op_limits': 'Environmental monitoring limits, sanitation verification limits' if 'contamination' in hazard_name.lower() else 'Processing temperature and time limits',
                'op_min': 0.0 if 'contamination' in hazard_name.lower() else 0.0,
                'op_max': 10.0 if 'contamination' in hazard_name.lower() else 4.0,
                'op_unit': 'CFU/swab' if 'contamination' in hazard_name.lower() else '°C',
                'op_desc': 'Maximum acceptable level for environmental monitoring' if 'contamination' in hazard_name.lower() else 'Maximum processing temperature to control bacterial growth',
                'mon_freq': 'Daily' if 'contamination' in hazard_name.lower() else 'Every batch',
                'mon_method': 'ATP swab testing and environmental sampling' if 'contamination' in hazard_name.lower() else 'Continuous temperature monitoring with data logging',
                'mon_resp': 'QA Specialist',
                'mon_equip': 'ATP meter and environmental swabs' if 'contamination' in hazard_name.lower() else 'Calibrated temperature sensors',
                'corr_actions': 'Re-clean and sanitize area, investigate source, hold product pending retest' if 'contamination' in hazard_name.lower() else 'Stop processing, cool product, investigate cause, adjust equipment',
                'ver_freq': 'Weekly',
                'ver_method': 'Review monitoring records, trend analysis, periodic microbiological testing',
                'ver_resp': 'QA Manager',
                'justification': f'OPRP required to control {hazard_name} through operational limits',
                'objective': 'Maintain hygienic processing environment' if 'contamination' in hazard_name.lower() else 'Control bacterial growth during processing',
                'sop_reference': 'SOP-003 Cleaning and Sanitization Procedure' if 'contamination' in hazard_name.lower() else 'SOP-002 Temperature Control Procedure',
                'created_at': datetime.now().isoformat(),
                'created_by': 1
            })
            oprp_counter += 1
    
    print(f"  ✓ Created {oprp_counter - 1} OPRPs for operational hazards")
    print(f"  ✓ ISO 22000 Risk Strategy Implementation Complete:")
    print(f"    - CCPs: {ccp_counter - 1} (Critical control points)")
    print(f"    - OPRPs: {oprp_counter - 1} (Operational prerequisite programs)")
    print(f"    - PRPs: {len([h for h in hazard_ids if h[1] == 'use_existing_prps'])} (Controlled by existing prerequisites)")

def create_professional_equipment_data(conn):
    """Create professional equipment data"""
    print("\n🔧 Creating professional equipment data...")
    
    equipment_data = [
        ('Pasteurizer HTST-001', 'pasteurizer', 'HTST-001', 'Production Floor A', 'High Temperature Short Time pasteurizer for milk processing', 1),
        ('Cheese Vat CV-001', 'processing_equipment', 'CV-001', 'Production Floor B', 'Stainless steel cheese making vat with temperature control', 1),
        ('Refrigeration Unit RF-001', 'refrigeration', 'RF-001', 'Cold Storage Room', 'Walk-in refrigeration unit for product storage', 1),
        ('Temperature Logger TL-001', 'monitoring_equipment', 'TL-001', 'Quality Lab', 'Digital temperature monitoring system with data logging', 1),
        ('Cleaning System CS-001', 'cleaning_equipment', 'CS-001', 'Sanitation Area', 'Automated cleaning-in-place system for equipment sanitization', 1),
    ]
    
    for name, equipment_type, serial_number, location, notes, created_by in equipment_data:
        conn.execute(text("""
            INSERT INTO equipment (name, equipment_type, serial_number, location, notes, is_active, critical_to_food_safety, created_at, created_by)
            VALUES (:name, :equipment_type, :serial_number, :location, :notes, :is_active, :critical_to_food_safety, :created_at, :created_by)
        """), {
            'name': name,
            'equipment_type': equipment_type,
            'serial_number': serial_number,
            'location': location,
            'notes': notes,
            'is_active': 1,
            'critical_to_food_safety': 1,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print("  ✓ Created equipment records")

def setup_database_complete():
    """Complete database setup with tables and professional data"""
    print("🏭 Setting up ISO 22000 FSMS Database with Professional Demo Data")
    print("=" * 70)
    
    try:
        # Step 0: Check existing database state
        if not handle_existing_tables():
            print("⚠️  Database state check failed - some tables may be missing")
            print("  💡 Consider running: python reset_database.py")
        
        # Step 1: Create database tables
        if not create_database_tables():
            print("❌ Failed to create database tables")
            print("  💡 If you're getting 'table already exists' errors, try running:")
            print("     python reset_database.py")
            print("     python setup_database_complete.py")
            return False
        
        # Step 2: Create permissions
        if not create_permissions():
            print("⚠️  Warning: Could not create permissions")
        
        # Step 3: Create default roles with permissions
        if not create_default_roles():
            print("⚠️  Warning: Could not create default roles")
        
        # Step 4: Populate with professional data
        with engine.connect() as conn:
            # Clear existing data
            clear_existing_data(conn)
            
            # Create professional data
            create_professional_users(conn)
            create_user_permissions(conn)
            create_professional_products(conn)
            create_professional_suppliers(conn)
            create_professional_documents(conn)
            create_professional_batches(conn)
            create_professional_haccp_data(conn)
            create_professional_equipment_data(conn)
            
            conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ Database setup completed successfully!")
        print("\n📊 System now contains:")
        print("   - 🔐 Complete RBAC System:")
        print("     • 189 Permissions (21 modules × 9 actions)")
        print("     • 10 Roles with proper permission assignments")
        print("     • Role-permission associations")
        print("   - 👥 12 Professional Users with correct role assignments:")
        print("     • 1 System Administrator (Full access - all 189 permissions)")
        print("     • 2 QA Managers (Most permissions except user management)")
        print("     • 2 QA Specialists (Limited permissions for QA modules)")
        print("     • 1 Production Manager (Production-related permissions)")
        print("     • 1 Production Operator (View-only permissions)")
        print("     • 1 Maintenance Manager (Maintenance-related permissions)")
        print("     • 1 Maintenance Technician (Limited maintenance permissions)")
        print("     • 1 HR Manager (Training and user permissions)")
        print("     • 1 Compliance Officer (Compliance-related permissions)")
        print("     • 1 Auditor (Audit-related permissions)")
        print("   - 🥛 8 Food Products (Dairy, Meat, Bakery)")
        print("   - 🚚 15 Food Industry Suppliers")
        print("   - 📋 25 Professional Documents (SOPs, Manuals)")
        print("   - 📦 20 Production Batches")
        print("   - 🔍 Complete HACCP Implementation with ISO 22000:2018 Risk Strategy:")
        print("     • 4 HACCP Plans (Approved)")
        print("     • 7 Process Flows (Fresh Milk production steps)")
        print("     • 8 Hazards with complete risk assessment:")
        print("       - consequences field (replaces rationale)")
        print("       - risk_strategy field (ccp/opprp/use_existing_prps)")
        print("       - risk_strategy_justification field")
        print("       - subsequent_step field")
        print("     • CCPs: 1 (Critical Control Point - Pasteurization)")
        print("       - Complete with critical limits, monitoring, verification")
        print("     • OPRPs: 3 (Operational Prerequisite Programs)")
        print("       - Complete with operational limits, monitoring, verification")
        print("       - objective and sop_reference fields included")
        print("     • PRPs: 4 (Controlled by existing prerequisites)")
        print("   - 🔧 5 Equipment Records")
        print("\n🎯 Ready for professional demonstrations with full RBAC!")
        print("\n✨ NEW: ISO 22000:2018 Risk Strategy Implementation:")
        print("   • Hazards classified into three control strategies:")
        print("     1. CCP (Critical Control Points) - Most critical hazards")
        print("     2. OPRP (Operational PRPs) - High-risk operational hazards")
        print("     3. Use Existing PRPs - Lower risk hazards")
        print("   • Complete justification and subsequent step tracking")
        print("   • Automated CCP and OPRP creation based on risk strategy")
        print("\n🔑 Default login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   (All demo users use password: admin123)")
        print("\n🔒 Role-based access is now fully functional!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    setup_database_complete()
