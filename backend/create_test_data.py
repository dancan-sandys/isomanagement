#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create comprehensive test data for ISO 22000 FSMS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document
from app.models.haccp import Product
from app.models.prp import PRPProgram
from app.models.supplier import Supplier
from app.models.user import User, UserRole, UserStatus

def create_test_data():
    """Create comprehensive test data for the ISO 22000 FSMS"""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("Creating test data for ISO 22000 FSMS...")
            
            # 1. Create test users
            create_test_users(conn)
            
            # 2. Create test documents
            create_test_documents(conn)
            
            # 3. Create test HACCP products
            create_test_haccp_products(conn)
            
            # 4. Create test PRP programs
            create_test_prp_programs(conn)
            
            # 5. Create test suppliers
            create_test_suppliers(conn)
            
            print("✅ Test data created successfully!")
            print("\n📊 Dashboard will now show:")
            print("   - 8 Documents (Manuals, SOPs, Records)")
            print("   - 4 HACCP Plans (Milk, Yogurt, Cheese, Butter)")
            print("   - 6 PRP Programs (Sanitation, Pest Control, etc.)")
            print("   - 5 Suppliers (Milk, Packaging, Cultures)")
            print("   - 3 Users (Admin, QA Manager, Production Supervisor)")
            
    except Exception as e:
        print(f"❌ Error creating test data: {e}")

def create_test_users(conn):
    """Create test users"""
    print("Creating test users...")
    
    # Check if users already exist
    result = conn.execute(text("SELECT COUNT(*) FROM users"))
    if result.scalar() > 0:
        print("Users already exist, skipping...")
        return
    
    # Create test users
    users_data = [
        {
            "username": "admin",
            "email": "admin@iso22000.com",
            "full_name": "System Administrator",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO",  # admin123
            "role": "ADMIN",
            "status": "ACTIVE",
            "department": "Quality Assurance",
            "position": "System Administrator"
        },
        {
            "username": "qa_manager",
            "email": "qa@iso22000.com",
            "full_name": "QA Manager",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO",  # admin123
            "role": "QA_MANAGER",
            "status": "ACTIVE",
            "department": "Quality Assurance",
            "position": "QA Manager"
        },
        {
            "username": "production",
            "email": "production@iso22000.com",
            "full_name": "Production Supervisor",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO",  # admin123
            "role": "PRODUCTION_MANAGER",
            "status": "ACTIVE",
            "department": "Production",
            "position": "Production Supervisor"
        }
    ]
    
    for user_data in users_data:
        conn.execute(text("""
            INSERT INTO users (
                username, email, full_name, hashed_password, 
                role, status, department, position, 
                is_active, is_verified, created_at, updated_at
            ) VALUES (
                :username, :email, :full_name, :hashed_password,
                :role, :status, :department, :position,
                true, true, datetime('now'), datetime('now')
            )
        """), user_data)
    
    conn.commit()
    print("✅ Test users created")

def create_test_documents(conn):
    """Create test documents"""
    print("Creating test documents...")
    
    # Check if documents already exist
    result = conn.execute(text("SELECT COUNT(*) FROM documents"))
    if result.scalar() > 0:
        print("Documents already exist, skipping...")
        return
    
    documents_data = [
        {
            "document_number": "DOC-001",
            "title": "ISO 22000 Food Safety Manual",
            "description": "Main food safety management system manual",
            "document_type": "MANUAL",
            "category": "GENERAL",
            "version": "1.0",
            "status": "APPROVED",
            "created_by": 1
        },
        {
            "document_number": "DOC-002",
            "title": "HACCP Plan Development SOP",
            "description": "Standard operating procedure for HACCP plan development",
            "document_type": "PROCEDURE",
            "category": "HACCP",
            "version": "2.1",
            "status": "APPROVED",
            "created_by": 2
        },
        {
            "document_number": "DOC-003",
            "title": "Daily Sanitation Checklist",
            "description": "Daily cleaning and sanitation verification checklist",
            "document_type": "CHECKLIST",
            "category": "PRP",
            "version": "1.0",
            "status": "DRAFT",
            "created_by": 3
        },
        {
            "document_number": "DOC-004",
            "title": "Supplier Evaluation Procedure",
            "description": "Procedure for evaluating and approving suppliers",
            "document_type": "PROCEDURE",
            "category": "SUPPLIER",
            "version": "1.2",
            "status": "APPROVED",
            "created_by": 2
        },
        {
            "document_number": "DOC-005",
            "title": "Corrective Action Form",
            "description": "Form for documenting corrective actions",
            "document_type": "FORM",
            "category": "QUALITY",
            "version": "1.0",
            "status": "APPROVED",
            "created_by": 1
        },
        {
            "document_number": "DOC-006",
            "title": "Internal Audit Checklist",
            "description": "Checklist for conducting internal audits",
            "document_type": "CHECKLIST",
            "category": "AUDIT",
            "version": "1.1",
            "status": "DRAFT",
            "created_by": 2
        },
        {
            "document_number": "DOC-007",
            "title": "Training Record Template",
            "description": "Template for recording employee training",
            "document_type": "FORM",
            "category": "TRAINING",
            "version": "1.0",
            "status": "APPROVED",
            "created_by": 1
        },
        {
            "document_number": "DOC-008",
            "title": "Equipment Maintenance Log",
            "description": "Log for recording equipment maintenance activities",
            "document_type": "RECORD",
            "category": "MAINTENANCE",
            "version": "1.0",
            "status": "APPROVED",
            "created_by": 3
        }
    ]
    
    for doc_data in documents_data:
        conn.execute(text("""
            INSERT INTO documents (
                document_number, title, description, document_type, category, 
                version, status, created_by, created_at, updated_at
            ) VALUES (
                :document_number, :title, :description, :document_type, :category,
                :version, :status, :created_by, datetime('now'), datetime('now')
            )
        """), doc_data)
    
    conn.commit()
    print("✅ Test documents created")

def create_test_haccp_products(conn):
    """Create test HACCP products"""
    print("Creating test HACCP products...")
    
    # Check if products already exist
    result = conn.execute(text("SELECT COUNT(*) FROM products"))
    if result.scalar() > 0:
        print("HACCP products already exist, skipping...")
        return
    
    products_data = [
        {
            "product_code": "MILK-001",
            "name": "Pasteurized Milk",
            "description": "Pasteurized whole milk product",
            "category": "milk",
            "formulation": '{"ingredients": ["raw_milk"], "proportions": [100]}',
            "allergens": '["milk"]',
            "shelf_life_days": 7,
            "storage_conditions": "Refrigerated at 2-4°C",
            "packaging_type": "Plastic bottle",
            "haccp_plan_approved": True,
            "haccp_plan_version": "1.0",
            "created_by": 2
        },
        {
            "product_code": "YOG-001",
            "name": "Greek Yogurt",
            "description": "Greek-style yogurt with live cultures",
            "category": "yogurt",
            "formulation": '{"ingredients": ["milk", "cultures"], "proportions": [95, 5]}',
            "allergens": '["milk"]',
            "shelf_life_days": 21,
            "storage_conditions": "Refrigerated at 2-4°C",
            "packaging_type": "Plastic container",
            "haccp_plan_approved": True,
            "haccp_plan_version": "1.0",
            "created_by": 2
        },
        {
            "product_code": "CHE-001",
            "name": "Cheddar Cheese",
            "description": "Aged cheddar cheese product",
            "category": "cheese",
            "formulation": '{"ingredients": ["milk", "rennet", "salt"], "proportions": [85, 10, 5]}',
            "allergens": '["milk"]',
            "shelf_life_days": 180,
            "storage_conditions": "Refrigerated at 2-4°C",
            "packaging_type": "Vacuum sealed",
            "haccp_plan_approved": False,
            "haccp_plan_version": None,
            "created_by": 3
        },
        {
            "product_code": "BUT-001",
            "name": "Butter",
            "description": "Cultured butter product",
            "category": "butter",
            "formulation": '{"ingredients": ["cream", "salt"], "proportions": [95, 5]}',
            "allergens": '["milk"]',
            "shelf_life_days": 90,
            "storage_conditions": "Refrigerated at 2-4°C",
            "packaging_type": "Wax paper",
            "haccp_plan_approved": True,
            "haccp_plan_version": "1.0",
            "created_by": 2
        }
    ]
    
    for product_data in products_data:
        conn.execute(text("""
            INSERT INTO products (
                product_code, name, description, category, formulation,
                allergens, shelf_life_days, storage_conditions, packaging_type,
                haccp_plan_approved, haccp_plan_version, created_by,
                created_at, updated_at
            ) VALUES (
                :product_code, :name, :description, :category, :formulation,
                :allergens, :shelf_life_days, :storage_conditions, :packaging_type,
                :haccp_plan_approved, :haccp_plan_version, :created_by,
                datetime('now'), datetime('now')
            )
        """), product_data)
    
    conn.commit()
    print("✅ Test HACCP products created")

def create_test_prp_programs(conn):
    """Create test PRP programs"""
    print("Creating test PRP programs...")
    
    # Check if PRP programs already exist
    result = conn.execute(text("SELECT COUNT(*) FROM prp_programs"))
    if result.scalar() > 0:
        print("PRP programs already exist, skipping...")
        return
    
    prp_data = [
        {
            "program_code": "PRP-001",
            "name": "Cleaning and Sanitation Program",
            "description": "Daily cleaning and sanitation procedures",
            "category": "cleaning_sanitation",
            "status": "active",
            "objective": "Ensure proper cleaning and sanitation of all equipment and facilities",
            "scope": "All production areas, equipment, and storage facilities",
            "responsible_department": "Production",
            "responsible_person": 3,
            "frequency": "daily",
            "frequency_details": "Daily cleaning after each production shift",
            "sop_reference": "SOP-CLEAN-001",
            "forms_required": '["daily_cleaning_checklist", "sanitation_verification_form"]',
            "created_by": 3
        },
        {
            "program_code": "PRP-002",
            "name": "Pest Control Program",
            "description": "Integrated pest management program",
            "category": "pest_control",
            "status": "active",
            "objective": "Prevent pest infestation in production and storage areas",
            "scope": "All facility areas including production, storage, and office spaces",
            "responsible_department": "Quality Assurance",
            "responsible_person": 2,
            "frequency": "weekly",
            "frequency_details": "Weekly inspection and treatment as needed",
            "sop_reference": "SOP-PEST-001",
            "forms_required": '["pest_inspection_report", "treatment_record"]',
            "created_by": 2
        },
        {
            "program_code": "PRP-003",
            "name": "Personal Hygiene Program",
            "description": "Employee hygiene and health monitoring",
            "category": "staff_hygiene",
            "status": "active",
            "objective": "Ensure all personnel maintain proper hygiene standards",
            "scope": "All employees and visitors to production areas",
            "responsible_department": "Production",
            "responsible_person": 3,
            "frequency": "daily",
            "frequency_details": "Daily hygiene checks and training as needed",
            "sop_reference": "SOP-HYGIENE-001",
            "forms_required": '["hygiene_checklist", "training_record"]',
            "created_by": 3
        },
        {
            "program_code": "PRP-004",
            "name": "Waste Management Program",
            "description": "Waste handling and disposal procedures",
            "category": "waste_management",
            "status": "active",
            "objective": "Proper handling and disposal of all waste materials",
            "scope": "All waste generated in production and facility operations",
            "responsible_department": "Production",
            "responsible_person": 3,
            "frequency": "daily",
            "frequency_details": "Daily waste collection and disposal",
            "sop_reference": "SOP-WASTE-001",
            "forms_required": '["waste_disposal_record", "recycling_log"]',
            "created_by": 3
        },
        {
            "program_code": "PRP-005",
            "name": "Equipment Maintenance Program",
            "description": "Preventive maintenance schedule",
            "category": "maintenance",
            "status": "active",
            "objective": "Ensure all equipment is properly maintained and calibrated",
            "scope": "All production and testing equipment",
            "responsible_department": "Production",
            "responsible_person": 3,
            "frequency": "monthly",
            "frequency_details": "Monthly preventive maintenance and calibration checks",
            "sop_reference": "SOP-MAINT-001",
            "forms_required": '["maintenance_log", "calibration_record"]',
            "created_by": 3
        },
        {
            "program_code": "PRP-006",
            "name": "Water Quality Program",
            "description": "Water quality monitoring and testing",
            "category": "water_quality",
            "status": "active",
            "objective": "Ensure water quality meets food safety standards",
            "scope": "All water used in production and cleaning",
            "responsible_department": "Quality Assurance",
            "responsible_person": 2,
            "frequency": "weekly",
            "frequency_details": "Weekly water quality testing and monitoring",
            "sop_reference": "SOP-WATER-001",
            "forms_required": '["water_quality_report", "testing_log"]',
            "created_by": 2
        }
    ]
    
    for prp in prp_data:
        conn.execute(text("""
            INSERT INTO prp_programs (
                program_code, name, description, category, status, objective,
                scope, responsible_department, responsible_person, frequency,
                frequency_details, sop_reference, forms_required, created_by,
                created_at, updated_at
            ) VALUES (
                :program_code, :name, :description, :category, :status, :objective,
                :scope, :responsible_department, :responsible_person, :frequency,
                :frequency_details, :sop_reference, :forms_required, :created_by,
                datetime('now'), datetime('now')
            )
        """), prp)
    
    conn.commit()
    print("✅ Test PRP programs created")

def create_test_suppliers(conn):
    """Create test suppliers"""
    print("Creating test suppliers...")
    
    # Check if suppliers already exist
    result = conn.execute(text("SELECT COUNT(*) FROM suppliers"))
    if result.scalar() > 0:
        print("Suppliers already exist, skipping...")
        return
    
    suppliers_data = [
        {
            "supplier_code": "SUP-001",
            "name": "Fresh Milk Co.",
            "status": "active",
            "category": "raw_milk",
            "contact_person": "John Smith",
            "email": "john@freshmilk.com",
            "phone": "+1-555-0101",
            "website": "https://freshmilk.com",
            "address_line1": "123 Dairy Farm Rd",
            "city": "Farmville",
            "state": "CA",
            "postal_code": "90210",
            "country": "USA",
            "business_registration_number": "BR123456",
            "tax_identification_number": "TIN789012",
            "company_type": "Corporation",
            "year_established": 1995,
            "certifications": '["ISO_22000", "HACCP", "Organic"]',
            "certification_expiry_dates": '{"ISO_22000": "2025-12-31", "HACCP": "2025-06-30", "Organic": "2025-03-15"}',
            "overall_score": 4.5,
            "risk_level": "low",
            "risk_factors": '[]',
            "notes": "Reliable supplier with excellent quality record",
            "created_by": 2
        },
        {
            "supplier_code": "SUP-002",
            "name": "Packaging Solutions Inc.",
            "status": "active",
            "category": "packaging",
            "contact_person": "Sarah Johnson",
            "email": "sarah@packaging.com",
            "phone": "+1-555-0102",
            "website": "https://packaging.com",
            "address_line1": "456 Industrial Blvd",
            "city": "Factory City",
            "state": "CA",
            "postal_code": "90211",
            "country": "USA",
            "business_registration_number": "BR234567",
            "tax_identification_number": "TIN890123",
            "company_type": "Corporation",
            "year_established": 2000,
            "certifications": '["ISO_9001", "FDA_Approved"]',
            "certification_expiry_dates": '{"ISO_9001": "2025-09-30", "FDA_Approved": "2025-12-31"}',
            "overall_score": 4.2,
            "risk_level": "low",
            "risk_factors": '[]',
            "notes": "Quality packaging materials with good delivery record",
            "created_by": 2
        },
        {
            "supplier_code": "SUP-003",
            "name": "Culture Supply Ltd.",
            "status": "active",
            "category": "cultures",
            "contact_person": "Mike Wilson",
            "email": "mike@cultures.com",
            "phone": "+1-555-0103",
            "website": "https://cultures.com",
            "address_line1": "789 Science Park",
            "city": "Lab Town",
            "state": "CA",
            "postal_code": "90212",
            "country": "USA",
            "business_registration_number": "BR345678",
            "tax_identification_number": "TIN901234",
            "company_type": "Corporation",
            "year_established": 1998,
            "certifications": '["ISO_22000", "GMP"]',
            "certification_expiry_dates": '{"ISO_22000": "2025-08-15", "GMP": "2025-11-30"}',
            "overall_score": 4.8,
            "risk_level": "low",
            "risk_factors": '[]',
            "notes": "High-quality cultures with excellent technical support",
            "created_by": 2
        },
        {
            "supplier_code": "SUP-004",
            "name": "Equipment Parts Co.",
            "status": "pending_approval",
            "category": "equipment",
            "contact_person": "Lisa Brown",
            "email": "lisa@equipment.com",
            "phone": "+1-555-0104",
            "website": "https://equipment.com",
            "address_line1": "321 Machine St",
            "city": "Industrial City",
            "state": "CA",
            "postal_code": "90213",
            "country": "USA",
            "business_registration_number": "BR456789",
            "tax_identification_number": "TIN012345",
            "company_type": "Corporation",
            "year_established": 2005,
            "certifications": '["ISO_9001"]',
            "certification_expiry_dates": '{"ISO_9001": "2025-07-20"}',
            "overall_score": 3.5,
            "risk_level": "medium",
            "risk_factors": '["New supplier", "Limited history"]',
            "notes": "New supplier under evaluation",
            "created_by": 3
        },
        {
            "supplier_code": "SUP-005",
            "name": "Quality Testing Lab",
            "status": "active",
            "category": "services",
            "contact_person": "David Lee",
            "email": "david@lab.com",
            "phone": "+1-555-0105",
            "website": "https://lab.com",
            "address_line1": "654 Test Ave",
            "city": "Science City",
            "state": "CA",
            "postal_code": "90214",
            "country": "USA",
            "business_registration_number": "BR567890",
            "tax_identification_number": "TIN123456",
            "company_type": "Corporation",
            "year_established": 1990,
            "certifications": '["ISO_17025", "FDA_Approved"]',
            "certification_expiry_dates": '{"ISO_17025": "2025-10-31", "FDA_Approved": "2025-12-31"}',
            "overall_score": 4.7,
            "risk_level": "low",
            "risk_factors": '[]',
            "notes": "Accredited testing laboratory with fast turnaround times",
            "created_by": 2
        }
    ]
    
    for supplier_data in suppliers_data:
        conn.execute(text("""
            INSERT INTO suppliers (
                supplier_code, name, status, category, contact_person, email, phone, website,
                address_line1, city, state, postal_code, country, business_registration_number,
                tax_identification_number, company_type, year_established, certifications,
                certification_expiry_dates, overall_score, risk_level, risk_factors, notes, created_by,
                created_at, updated_at
            ) VALUES (
                :supplier_code, :name, :status, :category, :contact_person, :email, :phone, :website,
                :address_line1, :city, :state, :postal_code, :country, :business_registration_number,
                :tax_identification_number, :company_type, :year_established, :certifications,
                :certification_expiry_dates, :overall_score, :risk_level, :risk_factors, :notes, :created_by,
                datetime('now'), datetime('now')
            )
        """), supplier_data)
    
    conn.commit()
    print("✅ Test suppliers created")

if __name__ == "__main__":
    create_test_data() 