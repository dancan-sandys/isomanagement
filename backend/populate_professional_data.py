#!/usr/bin/env python3
"""
Professional Data Population Script for ISO 22000 FSMS
Creates realistic, professional demo data for a food safety management system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.core.config import settings
import random

def populate_professional_data():
    """Populate database with professional food safety management data"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("🏭 Creating professional ISO 22000 FSMS demo data...")
            print("=" * 60)
            
            # Clear existing unprofessional data
            clear_existing_data(conn)
            
            # Create professional data
            create_professional_users(conn)
            create_professional_products(conn)
            create_professional_suppliers(conn)
            create_professional_documents(conn)
            create_professional_batches(conn)
            create_professional_haccp_data(conn)
            create_professional_ccp_monitoring_logs(conn)
            # create_professional_prp_data(conn)  # Skip for now due to complex schema
            create_professional_training_data(conn)
            create_professional_equipment_data(conn)
            
            print("\n" + "=" * 60)
            print("✅ Professional demo data created successfully!")
            print("\n📊 System now contains:")
            print("   - 12 Professional Users (Food Safety roles)")
            print("   - 8 Food Products (Dairy, Meat, Bakery)")
            print("   - 15 Food Industry Suppliers")
            print("   - 25 Professional Documents (SOPs, Manuals)")
            print("   - 20 Production Batches")
            print("   - Complete HACCP Plans")
            print("   - 8 Critical Control Points (CCPs)")
            print("   - 30+ CCP Monitoring Logs")
            print("   - Training Programs")
            print("   - Equipment Records")
            print("\n🎯 Ready for professional demonstrations!")
            
    except Exception as e:
        print(f"❌ Error creating professional data: {e}")
        raise

def clear_existing_data(conn):
    """Clear existing unprofessional data"""
    print("🧹 Clearing existing unprofessional data...")
    
    # Tables to clear (in dependency order)
    tables_to_clear = [
        'batches', 'ccp_monitoring_logs', 'ccp_verification_logs', 'ccps',
        'hazards', 'process_flows', 'haccp_plans', 'products',
        'supplier_evaluations', 'supplier_documents', 'suppliers',
        'document_approvals', 'document_versions', 'documents',
        'training_attendance', 'training_sessions', 'training_programs',
        'maintenance_work_orders', 'calibration_records', 'equipment',
        'prp_checklist_items', 'prp_checklists', 'prp_programs',
        'users'
    ]
    
    for table in tables_to_clear:
        try:
            conn.execute(text(f"DELETE FROM {table}"))
            print(f"  ✓ Cleared {table}")
        except Exception as e:
            print(f"  ⚠️  Could not clear {table}: {e}")

def create_professional_users(conn):
    """Create professional food safety users"""
    print("\n👥 Creating professional users...")
    
    users_data = [
        # Management
        ('fs_manager', 'fs.manager@foodsafe.com', 'Sarah Johnson', 'Food Safety Manager', 'Quality Assurance', '+1-555-0101', 'FSM001'),
        ('qa_director', 'qa.director@foodsafe.com', 'Michael Chen', 'QA Director', 'Quality Assurance', '+1-555-0102', 'QAD001'),
        ('plant_manager', 'plant.manager@foodsafe.com', 'Robert Williams', 'Plant Manager', 'Operations', '+1-555-0103', 'PM001'),
        
        # Quality Assurance
        ('qa_supervisor', 'qa.supervisor@foodsafe.com', 'Lisa Rodriguez', 'QA Supervisor', 'Quality Assurance', '+1-555-0104', 'QAS001'),
        ('haccp_coordinator', 'haccp.coordinator@foodsafe.com', 'David Kim', 'HACCP Coordinator', 'Quality Assurance', '+1-555-0105', 'HC001'),
        ('microbiologist', 'microbiologist@foodsafe.com', 'Jennifer Lee', 'Microbiologist', 'Quality Assurance', '+1-555-0106', 'MB001'),
        
        # Production
        ('production_supervisor', 'production.supervisor@foodsafe.com', 'James Brown', 'Production Supervisor', 'Production', '+1-555-0107', 'PS001'),
        ('sanitation_lead', 'sanitation.lead@foodsafe.com', 'Maria Garcia', 'Sanitation Lead', 'Production', '+1-555-0108', 'SL001'),
        ('line_operator', 'line.operator@foodsafe.com', 'Thomas Wilson', 'Line Operator', 'Production', '+1-555-0109', 'LO001'),
        
        # Maintenance
        ('maintenance_manager', 'maintenance.manager@foodsafe.com', 'Kevin Davis', 'Maintenance Manager', 'Maintenance', '+1-555-0110', 'MM001'),
        ('calibration_tech', 'calibration.tech@foodsafe.com', 'Amanda Taylor', 'Calibration Technician', 'Maintenance', '+1-555-0111', 'CT001'),
        
        # Admin
        ('admin', 'admin@foodsafe.com', 'System Administrator', 'System Administrator', 'IT', '+1-555-0000', 'ADM001')
    ]
    
    # Hash for 'admin123' - Default password for all demo users
    # Using simple SHA256 hash for compatibility (fallback method from auth system)
    # To change password, use: python -c "import hashlib; print(hashlib.sha256('your_new_password'.encode()).hexdigest())"
    hashed_password = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'
    
    for username, email, full_name, position, department, phone, employee_id in users_data:
        conn.execute(text("""
            INSERT INTO users (username, email, full_name, hashed_password, role_id, status, 
                             department_name, position, phone, employee_id, is_active, is_verified, 
                             failed_login_attempts, locked_until, created_at, created_by)
            VALUES (:username, :email, :full_name, :hashed_password, 1, 'active', 
                   :department, :position, :phone, :employee_id, 1, 1, 
                   0, NULL, :created_at, 1)
        """), {
            'username': username,
            'email': email,
            'full_name': full_name,
            'hashed_password': hashed_password,
            'department': department,
            'position': position,
            'phone': phone,
            'employee_id': employee_id,
            'created_at': datetime.now().isoformat()
        })
    
    print(f"  ✓ Created {len(users_data)} professional users")

def create_professional_products(conn):
    """Create professional food products"""
    print("\n🥛 Creating professional food products...")
    
    products_data = [
        # Dairy Products
        ('DAI-001', 'Fresh Whole Milk', 'Pasteurized whole milk, 3.25% fat', 'dairy', '{"milk": "100%", "vitamin_d": "400 IU/L"}', '["milk"]', 14, 'Refrigerated 2-4°C', 'HDPE Bottle', 1),
        ('DAI-002', 'Greek Yogurt', 'Creamy Greek yogurt, 2% fat', 'dairy', '{"milk": "95%", "live_cultures": "5 strains"}', '["milk"]', 21, 'Refrigerated 2-4°C', 'Plastic Cup', 1),
        ('DAI-003', 'Cheddar Cheese', 'Aged cheddar cheese, 6 months', 'dairy', '{"milk": "100%", "salt": "1.5%", "enzymes": "rennet"}', '["milk"]', 90, 'Refrigerated 2-4°C', 'Vacuum Pack', 1),
        ('DAI-004', 'Butter', 'Sweet cream butter, 80% fat', 'dairy', '{"cream": "100%", "salt": "1.5%"}', '["milk"]', 60, 'Refrigerated 2-4°C', 'Wax Paper', 1),
        
        # Meat Products
        ('MEA-001', 'Ground Beef', 'Fresh ground beef, 80/20 lean', 'meat', '{"beef": "100%"}', '[]', 3, 'Refrigerated 0-2°C', 'Vacuum Pack', 1),
        ('MEA-002', 'Chicken Breast', 'Boneless skinless chicken breast', 'meat', '{"chicken": "100%"}', '[]', 5, 'Refrigerated 0-2°C', 'Vacuum Pack', 1),
        
        # Bakery Products
        ('BAK-001', 'Whole Wheat Bread', 'Artisan whole wheat bread', 'bakery', '{"flour": "60%", "water": "35%", "yeast": "2%", "salt": "1%"}', '["wheat", "gluten"]', 7, 'Room temperature', 'Paper Bag', 1),
        ('BAK-002', 'Chocolate Chip Cookies', 'Soft chocolate chip cookies', 'bakery', '{"flour": "45%", "sugar": "25%", "butter": "20%", "chocolate": "10%"}', '["wheat", "gluten", "milk", "eggs"]', 14, 'Room temperature', 'Plastic Bag', 1)
    ]
    
    for product_code, name, description, category, formulation, allergens, shelf_life, storage, packaging, created_by in products_data:
        conn.execute(text("""
            INSERT INTO products (product_code, name, description, category, formulation, allergens,
                                shelf_life_days, storage_conditions, packaging_type, haccp_plan_approved,
                                created_at, created_by, risk_assessment_required)
            VALUES (:product_code, :name, :description, :category, :formulation, :allergens,
                   :shelf_life, :storage, :packaging, 1, :created_at, :created_by, 1)
        """), {
            'product_code': product_code,
            'name': name,
            'description': description,
            'category': category,
            'formulation': formulation,
            'allergens': allergens,
            'shelf_life': shelf_life,
            'storage': storage,
            'packaging': packaging,
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
        ('FSM-001', 'Food Safety Management System Manual', 'Comprehensive FSMS manual based on ISO 22000:2018', 'manual', 'food_safety', 'APPROVED', '2.1', 'Quality Assurance', 'All Products', '[]', 'HACCP, ISO 22000, Food Safety', 1),
        ('FSM-002', 'HACCP Plan Manual', 'Hazard Analysis and Critical Control Points implementation guide', 'manual', 'food_safety', 'APPROVED', '1.3', 'Quality Assurance', 'All Products', '[]', 'HACCP, Critical Control Points, Food Safety', 1),
        ('FSM-003', 'Prerequisite Programs Manual', 'PRP implementation and management procedures', 'manual', 'food_safety', 'APPROVED', '1.2', 'Quality Assurance', 'All Products', '[]', 'PRP, Prerequisites, Sanitation', 1),
        
        # Standard Operating Procedures
        ('SOP-001', 'Receiving and Inspection Procedure', 'Standard procedure for receiving raw materials and ingredients', 'procedure', 'operations', 'APPROVED', '1.4', 'Quality Assurance', 'Raw Materials', '[]', 'Receiving, Inspection, Raw Materials', 1),
        ('SOP-002', 'Temperature Control Procedure', 'Temperature monitoring and control procedures for food products', 'procedure', 'operations', 'APPROVED', '1.2', 'Quality Assurance', 'All Products', '[]', 'Temperature, Monitoring, Control', 1),
        ('SOP-003', 'Cleaning and Sanitization Procedure', 'Comprehensive cleaning and sanitization procedures', 'procedure', 'operations', 'APPROVED', '2.0', 'Production', 'All Areas', '[]', 'Cleaning, Sanitization, Hygiene', 1),
        ('SOP-004', 'Allergen Control Procedure', 'Allergen management and cross-contamination prevention', 'procedure', 'operations', 'APPROVED', '1.1', 'Quality Assurance', 'All Products', '[]', 'Allergens, Cross-contamination, Control', 1),
        ('SOP-005', 'Traceability Procedure', 'Product traceability and recall procedures', 'procedure', 'operations', 'APPROVED', '1.3', 'Quality Assurance', 'All Products', '[]', 'Traceability, Recall, Tracking', 1),
        
        # Work Instructions
        ('WI-001', 'Milk Pasteurization Work Instruction', 'Step-by-step pasteurization process instructions', 'work_instruction', 'production', 'APPROVED', '1.2', 'Production', 'Dairy Products', '["DAI-001"]', 'Pasteurization, Milk, Temperature', 1),
        ('WI-002', 'Cheese Making Work Instruction', 'Detailed cheese production process instructions', 'work_instruction', 'production', 'APPROVED', '1.1', 'Production', 'Dairy Products', '["DAI-003"]', 'Cheese, Production, Aging', 1),
        ('WI-003', 'Bread Baking Work Instruction', 'Artisan bread production process instructions', 'work_instruction', 'production', 'APPROVED', '1.3', 'Production', 'Bakery Products', '["BAK-001"]', 'Bread, Baking, Fermentation', 1),
        
        # Forms and Records
        ('FRM-001', 'Daily Temperature Log', 'Daily temperature monitoring record form', 'form', 'records', 'APPROVED', '1.0', 'Quality Assurance', 'All Products', '[]', 'Temperature, Log, Monitoring', 1),
        ('FRM-002', 'HACCP Monitoring Record', 'Critical Control Point monitoring record form', 'form', 'records', 'APPROVED', '1.1', 'Quality Assurance', 'All Products', '[]', 'HACCP, Monitoring, CCP', 1),
        ('FRM-003', 'Cleaning Verification Checklist', 'Post-cleaning verification checklist', 'form', 'records', 'APPROVED', '1.0', 'Production', 'All Areas', '[]', 'Cleaning, Verification, Checklist', 1),
        ('FRM-004', 'Supplier Evaluation Form', 'Supplier performance evaluation form', 'form', 'records', 'APPROVED', '1.2', 'Quality Assurance', 'Suppliers', '[]', 'Supplier, Evaluation, Performance', 1),
        
        # Training Materials
        ('TRN-001', 'Food Safety Awareness Training', 'Basic food safety awareness training material', 'training_material', 'training', 'APPROVED', '1.1', 'Human Resources', 'All Employees', '[]', 'Training, Food Safety, Awareness', 1),
        ('TRN-002', 'HACCP Team Training', 'HACCP team member training material', 'training_material', 'training', 'APPROVED', '1.0', 'Quality Assurance', 'HACCP Team', '[]', 'Training, HACCP, Team', 1),
        ('TRN-003', 'Allergen Management Training', 'Allergen control and management training', 'training_material', 'training', 'APPROVED', '1.1', 'Quality Assurance', 'Production Staff', '[]', 'Training, Allergens, Management', 1),
        
        # Policies
        ('POL-001', 'Food Safety Policy', 'Company food safety policy statement', 'policy', 'management', 'APPROVED', '1.0', 'Management', 'All Operations', '[]', 'Policy, Food Safety, Management', 1),
        ('POL-002', 'Supplier Management Policy', 'Supplier selection and management policy', 'policy', 'management', 'APPROVED', '1.1', 'Procurement', 'Suppliers', '[]', 'Policy, Supplier, Management', 1),
        ('POL-003', 'Training and Competency Policy', 'Employee training and competency development policy', 'policy', 'management', 'APPROVED', '1.0', 'Human Resources', 'All Employees', '[]', 'Policy, Training, Competency', 1),
        
        # Specifications
        ('SPEC-001', 'Raw Milk Specification', 'Raw milk quality and safety specifications', 'specification', 'quality', 'APPROVED', '1.2', 'Quality Assurance', 'Raw Materials', '[]', 'Specification, Raw Milk, Quality', 1),
        ('SPEC-002', 'Finished Product Specification', 'Finished product quality specifications', 'specification', 'quality', 'APPROVED', '1.1', 'Quality Assurance', 'All Products', '[]', 'Specification, Finished Product, Quality', 1),
        ('SPEC-003', 'Packaging Material Specification', 'Packaging material specifications and requirements', 'specification', 'quality', 'APPROVED', '1.0', 'Quality Assurance', 'Packaging', '[]', 'Specification, Packaging, Materials', 1)
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
    """Create professional HACCP data"""
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

def create_professional_ccp_monitoring_logs(conn):
    """Create professional CCP monitoring logs with all required columns"""
    print("\n📊 Creating professional CCP monitoring logs...")
    
    # First, create hazards for the CCPs
    hazards_data = [
        ('Biological Hazard - Pathogenic Bacteria', 'Contamination by pathogenic bacteria such as Salmonella, E. coli, Listeria', 'biological', 4, 5, 20, 'high', 'Proper temperature control and pasteurization', True, 4, True, 'Temperature control is critical for pathogen destruction', 1),
        ('Biological Hazard - Spoilage Microorganisms', 'Growth of spoilage microorganisms affecting product quality', 'biological', 3, 3, 9, 'medium', 'Temperature control and proper storage', True, 3, False, 'Controlled by temperature and storage conditions', 1),
        ('Physical Hazard - Foreign Objects', 'Presence of foreign objects in food products', 'physical', 2, 4, 8, 'medium', 'Visual inspection and metal detection', True, 4, False, 'Controlled by inspection and detection equipment', 1),
        ('Chemical Hazard - Allergens', 'Presence of undeclared allergens in products', 'chemical', 3, 5, 15, 'high', 'Allergen control and proper labeling', True, 4, True, 'Allergen control is critical for consumer safety', 1),
        ('Chemical Hazard - Chemical Contamination', 'Contamination by cleaning chemicals or other chemicals', 'chemical', 2, 3, 6, 'low', 'Proper cleaning procedures and chemical control', True, 3, False, 'Controlled by proper procedures and training', 1)
    ]
    
    for hazard_name, description, hazard_type, likelihood, severity, risk_score, risk_level, control_measures, is_controlled, control_effectiveness, is_ccp, rationale, created_by in hazards_data:
        conn.execute(text("""
            INSERT INTO hazards (hazard_name, description, hazard_type, likelihood, severity, risk_score, 
                               risk_level, control_measures, is_controlled, control_effectiveness, is_ccp, 
                               rationale, created_at, created_by, product_id, process_step_id)
            VALUES (:hazard_name, :description, :hazard_type, :likelihood, :severity, :risk_score, 
                   :risk_level, :control_measures, :is_controlled, :control_effectiveness, :is_ccp, 
                   :rationale, :created_at, :created_by, :product_id, :process_step_id)
        """), {
            'hazard_name': hazard_name,
            'description': description,
            'hazard_type': hazard_type,
            'likelihood': likelihood,
            'severity': severity,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'control_measures': control_measures,
            'is_controlled': is_controlled,
            'control_effectiveness': control_effectiveness,
            'is_ccp': is_ccp,
            'rationale': rationale,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by,
            'product_id': 1,  # Use the first product (Fresh Milk)
            'process_step_id': 1  # Use the first process step
        })
    
    print("  ✓ Created hazards")
    
    # Get hazard IDs for CCP creation
    hazard_result = conn.execute(text("SELECT id, hazard_name FROM hazards"))
    hazards = {hazard_name: hazard_id for hazard_id, hazard_name in hazard_result.fetchall()}
    
    # Now create CCPs (Critical Control Points) for the products
    ccp_data = [
        # Fresh Milk CCPs
        (1, hazards['Biological Hazard - Pathogenic Bacteria'], 'CCP-001', 'Milk Pasteurization Temperature', 'Temperature monitoring during pasteurization', 'active', 72.0, 85.0, '°C', 'Temperature must be maintained between 72-85°C for 15 seconds', 'Temperature monitoring every 30 minutes', 'Digital thermometer', 'QA Technician', 'Daily calibration check', 'QA Supervisor', 'Weekly verification', 'QA Manager', 1),
        (1, hazards['Biological Hazard - Spoilage Microorganisms'], 'CCP-002', 'Milk Cooling Temperature', 'Rapid cooling after pasteurization', 'active', 0.0, 4.0, '°C', 'Milk must be cooled to 4°C within 2 hours', 'Temperature monitoring every 15 minutes', 'Digital thermometer', 'Production Operator', 'Daily calibration check', 'QA Technician', 'Daily verification', 'QA Supervisor', 1),
        
        # Greek Yogurt CCPs
        (2, hazards['Biological Hazard - Pathogenic Bacteria'], 'CCP-003', 'Yogurt Fermentation Temperature', 'Temperature control during fermentation', 'active', 40.0, 45.0, '°C', 'Fermentation temperature must be maintained at 42±2°C', 'Temperature monitoring every hour', 'Digital thermometer', 'Production Operator', 'Daily calibration check', 'QA Technician', 'Daily verification', 'QA Supervisor', 1),
        (2, hazards['Biological Hazard - Pathogenic Bacteria'], 'CCP-004', 'Yogurt pH Control', 'pH monitoring during fermentation', 'active', 4.0, 4.5, 'pH', 'Final pH must be between 4.0-4.5', 'pH monitoring every 2 hours', 'pH meter', 'QA Technician', 'Weekly calibration check', 'QA Supervisor', 'Daily verification', 'QA Manager', 1),
        
        # Cheddar Cheese CCPs
        (3, hazards['Biological Hazard - Pathogenic Bacteria'], 'CCP-005', 'Cheese Cooking Temperature', 'Temperature during cheese cooking', 'active', 35.0, 40.0, '°C', 'Cooking temperature must be maintained at 38±2°C', 'Temperature monitoring every 30 minutes', 'Digital thermometer', 'Cheese Maker', 'Daily calibration check', 'QA Technician', 'Daily verification', 'QA Supervisor', 1),
        (3, hazards['Physical Hazard - Foreign Objects'], 'CCP-006', 'Cheese Pressing Pressure', 'Pressure during cheese pressing', 'active', 2.0, 3.0, 'bar', 'Pressing pressure must be maintained at 2.5±0.5 bar', 'Pressure monitoring every hour', 'Pressure gauge', 'Cheese Maker', 'Weekly calibration check', 'QA Technician', 'Daily verification', 'QA Supervisor', 1),
        
        # Ground Beef CCPs
        (5, hazards['Biological Hazard - Pathogenic Bacteria'], 'CCP-007', 'Beef Grinding Temperature', 'Temperature during grinding process', 'active', 0.0, 7.0, '°C', 'Grinding temperature must not exceed 7°C', 'Temperature monitoring every 15 minutes', 'Digital thermometer', 'Production Operator', 'Daily calibration check', 'QA Technician', 'Daily verification', 'QA Supervisor', 1),
        (5, hazards['Biological Hazard - Spoilage Microorganisms'], 'CCP-008', 'Beef Packaging Temperature', 'Temperature during packaging', 'active', 0.0, 4.0, '°C', 'Packaging temperature must be maintained at 2±2°C', 'Temperature monitoring every 30 minutes', 'Digital thermometer', 'Packaging Operator', 'Daily calibration check', 'QA Technician', 'Daily verification', 'QA Supervisor', 1)
    ]
    
    for (product_id, hazard_id, ccp_number, ccp_name, description, status, critical_limit_min, 
         critical_limit_max, critical_limit_unit, critical_limit_description, 
         monitoring_frequency, monitoring_method, monitoring_responsible, 
         verification_frequency, verification_method, verification_responsible, 
         verification_manager, created_by) in ccp_data:
        
        conn.execute(text("""
            INSERT INTO ccps (product_id, hazard_id, ccp_number, ccp_name, description, status, 
                            critical_limit_min, critical_limit_max, critical_limit_unit, 
                            critical_limit_description, monitoring_frequency, monitoring_method, 
                            monitoring_responsible, verification_frequency, verification_method, 
                            verification_responsible, created_at, created_by)
            VALUES (:product_id, :hazard_id, :ccp_number, :ccp_name, :description, :status, 
                   :critical_limit_min, :critical_limit_max, :critical_limit_unit, 
                   :critical_limit_description, :monitoring_frequency, :monitoring_method, 
                   :monitoring_responsible, :verification_frequency, :verification_method, 
                   :verification_responsible, :created_at, :created_by)
        """), {
            'product_id': product_id,
            'hazard_id': hazard_id,
            'ccp_number': ccp_number,
            'ccp_name': ccp_name,
            'description': description,
            'status': status,
            'critical_limit_min': critical_limit_min,
            'critical_limit_max': critical_limit_max,
            'critical_limit_unit': critical_limit_unit,
            'critical_limit_description': critical_limit_description,
            'monitoring_frequency': monitoring_frequency,
            'monitoring_method': monitoring_method,
            'monitoring_responsible': monitoring_responsible,
            'verification_frequency': verification_frequency,
            'verification_method': verification_method,
            'verification_responsible': verification_responsible,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print("  ✓ Created CCPs")
    
    # Get created CCPs and batches for monitoring logs
    ccp_result = conn.execute(text("SELECT id, ccp_number, ccp_name, critical_limit_min, critical_limit_max, critical_limit_unit FROM ccps"))
    ccps = ccp_result.fetchall()
    
    batch_result = conn.execute(text("SELECT id, batch_number, product_id FROM batches"))
    batches = batch_result.fetchall()
    
    # Create monitoring logs for each CCP
    monitoring_logs_created = 0
    
    for ccp_id, ccp_number, ccp_name, min_limit, max_limit, unit in ccps:
        # Find batches for this CCP's product
        product_batches = [b for b in batches if b[2] == next((c[0] for c in ccp_data if c[1] == ccp_number), None)]
        
        # Create 3-5 monitoring logs per CCP
        for i in range(random.randint(3, 5)):
            # Select a random batch or None
            batch_id = random.choice(product_batches)[0] if product_batches else None
            batch_number = random.choice(product_batches)[1] if product_batches else f"BATCH-{ccp_number}-{i+1:03d}"
            
            # Generate realistic monitoring data
            monitoring_time = datetime.now() - timedelta(hours=random.randint(1, 72))
            
            # Generate measured value within or slightly outside limits (90% within limits)
            if random.random() < 0.9:  # 90% within limits
                measured_value = random.uniform(min_limit, max_limit)
                is_within_limits = True
                corrective_action_taken = False
                corrective_action_description = None
                corrective_action_by = None
            else:  # 10% out of limits
                if random.random() < 0.5:
                    measured_value = random.uniform(min_limit - 2, min_limit)  # Below minimum
                else:
                    measured_value = random.uniform(max_limit, max_limit + 2)  # Above maximum
                is_within_limits = False
                corrective_action_taken = random.choice([True, False])
                if corrective_action_taken:
                    corrective_action_description = f"Corrective action taken: Adjusted {ccp_name.lower()} to bring within limits"
                    corrective_action_by = random.randint(1, 12)  # Random user ID
                else:
                    corrective_action_description = None
                    corrective_action_by = None
            
            # Generate additional parameters based on CCP type
            if 'temperature' in ccp_name.lower():
                additional_parameters = {
                    "ambient_temperature": round(random.uniform(18, 25), 1),
                    "equipment_status": random.choice(["normal", "normal", "normal", "maintenance_required"]),
                    "operator_id": f"OP-{random.randint(100, 999)}"
                }
            elif 'ph' in ccp_name.lower():
                additional_parameters = {
                    "calibration_date": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat(),
                    "buffer_solution_used": random.choice(["pH 4.0", "pH 7.0", "pH 10.0"]),
                    "temperature_compensation": round(random.uniform(20, 25), 1)
                }
            elif 'pressure' in ccp_name.lower():
                additional_parameters = {
                    "equipment_pressure": round(random.uniform(2.0, 3.0), 1),
                    "valve_position": random.choice(["open", "partially_open", "closed"]),
                    "system_status": "operational"
                }
            else:
                additional_parameters = {
                    "equipment_status": "normal",
                    "operator_notes": f"Standard monitoring for {ccp_name}"
                }
            
            # Generate observations
            observations = [
                f"Monitoring completed for {ccp_name}",
                f"Equipment functioning normally",
                f"Measured value: {measured_value} {unit}",
                f"Critical limits: {min_limit}-{max_limit} {unit}"
            ]
            
            if not is_within_limits:
                observations.append("⚠️ OUT OF SPECIFICATION - Requires immediate attention")
                if corrective_action_taken:
                    observations.append("✅ Corrective action implemented")
                else:
                    observations.append("❌ Corrective action pending")
            
            # Generate evidence files (simulated file references)
            evidence_files = []
            if random.random() < 0.7:  # 70% have evidence files
                evidence_files = [
                    f"monitoring_photo_{ccp_id}_{i+1}.jpg",
                    f"calibration_cert_{datetime.now().strftime('%Y%m%d')}.pdf"
                ]
            
            # Generate log metadata
            log_metadata = {
                "monitoring_device": f"Device-{ccp_id}-{random.randint(100, 999)}",
                "calibration_due": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
                "operator_signature": f"OP-{random.randint(100, 999)}",
                "supervisor_approval": random.choice([True, False]),
                "data_quality": random.choice(["excellent", "good", "acceptable"])
            }
            
            # Insert monitoring log with all required columns
            conn.execute(text("""
                INSERT INTO ccp_monitoring_logs (
                    ccp_id, batch_id, batch_number, monitoring_time, measured_value, unit, 
                    is_within_limits, additional_parameters, observations, evidence_files, 
                    corrective_action_taken, corrective_action_description, corrective_action_by, 
                    equipment_id, action_log_id, created_by, created_at, log_metadata
                ) VALUES (
                    :ccp_id, :batch_id, :batch_number, :monitoring_time, :measured_value, :unit, 
                    :is_within_limits, :additional_parameters, :observations, :evidence_files, 
                    :corrective_action_taken, :corrective_action_description, :corrective_action_by, 
                    :equipment_id, :action_log_id, :created_by, :created_at, :log_metadata
                )
            """), {
                'ccp_id': ccp_id,
                'batch_id': batch_id,
                'batch_number': batch_number,
                'monitoring_time': monitoring_time.isoformat(),
                'measured_value': measured_value,
                'unit': unit,
                'is_within_limits': is_within_limits,
                'additional_parameters': str(additional_parameters).replace("'", '"'),  # Convert to JSON string
                'observations': '; '.join(observations),
                'evidence_files': str(evidence_files).replace("'", '"'),  # Convert to JSON string
                'corrective_action_taken': corrective_action_taken,
                'corrective_action_description': corrective_action_description,
                'corrective_action_by': corrective_action_by,
                'equipment_id': random.randint(1, 5),  # Random equipment ID
                'action_log_id': None,  # No action log for demo data
                'created_by': random.randint(1, 12),  # Random user ID
                'created_at': monitoring_time.isoformat(),
                'log_metadata': str(log_metadata).replace("'", '"')  # Convert to JSON string
            })
            
            monitoring_logs_created += 1
    
    print(f"  ✓ Created {monitoring_logs_created} professional CCP monitoring logs")

def create_professional_prp_data(conn):
    """Create professional PRP data"""
    print("\n🛡️ Creating professional PRP data...")
    
    prp_programs = [
        ('PRP-001', 'Sanitation Program', 'Comprehensive sanitation and cleaning program', 'sanitation', 'active', 'Quality Assurance', 'Ensure all equipment and facilities are properly cleaned and sanitized to prevent contamination', 'All production areas, equipment, and facilities', 1),
        ('PRP-002', 'Pest Control Program', 'Integrated pest management program', 'pest_control', 'active', 'Quality Assurance', 'Prevent pest infestation and maintain pest-free environment in food processing areas', 'Entire facility including production, storage, and office areas', 1),
        ('PRP-003', 'Water Quality Program', 'Water quality monitoring and control program', 'water_quality', 'active', 'Quality Assurance', 'Ensure water used in food processing meets potable water standards', 'All water sources used in food processing and cleaning', 1),
        ('PRP-004', 'Employee Hygiene Program', 'Employee hygiene and health monitoring program', 'hygiene', 'active', 'Human Resources', 'Maintain high standards of personal hygiene and health among all employees', 'All employees and contractors working in food handling areas', 1),
        ('PRP-005', 'Supplier Management Program', 'Supplier approval and monitoring program', 'supplier_management', 'active', 'Procurement', 'Ensure all suppliers meet food safety requirements and maintain quality standards', 'All suppliers of raw materials, ingredients, and services', 1),
        ('PRP-006', 'Allergen Control Program', 'Allergen management and cross-contamination prevention', 'allergen_control', 'active', 'Quality Assurance', 'Prevent allergen cross-contamination and ensure proper allergen labeling', 'All products containing or potentially containing allergens', 1),
    ]
    
    for program_code, name, description, category, status, responsible_department, objective, scope, created_by in prp_programs:
        conn.execute(text("""
            INSERT INTO prp_programs (program_code, name, description, category, status, responsible_department, objective, scope, responsible_person, frequency,
                                    created_at, created_by)
            VALUES (:program_code, :name, :description, :category, :status, :responsible_department, :objective, :scope, :responsible_person, :frequency,
                   :created_at, :created_by)
        """), {
            'program_code': program_code,
            'name': name,
            'description': description,
            'category': category,
            'status': status,
            'responsible_department': responsible_department,
            'objective': objective,
            'scope': scope,
            'responsible_person': 1,  # Default to user ID 1 (admin)
            'frequency': 'daily',  # Default frequency
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print("  ✓ Created PRP programs")

def create_professional_training_data(conn):
    """Create professional training data"""
    print("\n🎓 Creating professional training data...")
    
    training_programs = [
        ('TRN-001', 'Food Safety Awareness', 'Basic food safety principles and practices', 'Quality Assurance', 1),
        ('TRN-002', 'HACCP Implementation', 'HACCP principles and implementation', 'Quality Assurance', 1),
        ('TRN-003', 'Allergen Management', 'Allergen control and cross-contamination prevention', 'Quality Assurance', 1),
        ('TRN-004', 'Sanitation Procedures', 'Proper cleaning and sanitization procedures', 'Production', 1),
        ('TRN-005', 'Temperature Control', 'Temperature monitoring and control procedures', 'Production', 1),
    ]
    
    for code, title, description, department, created_by in training_programs:
        conn.execute(text("""
            INSERT INTO training_programs (code, title, description, department, created_at, created_by)
            VALUES (:code, :title, :description, :department, :created_at, :created_by)
        """), {
            'code': code,
            'title': title,
            'description': description,
            'department': department,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        })
    
    print("  ✓ Created training programs")

def get_equipment_schema(conn):
    """Get the equipment table schema to determine what columns exist"""
    # Use SQLAlchemy text() for raw SQL queries
    result = conn.execute(text('PRAGMA table_info(equipment)'))
    columns = result.fetchall()
    
    schema_info = {
        'has_is_active': any(col[1] == 'is_active' for col in columns),
        'has_critical_to_food_safety': any(col[1] == 'critical_to_food_safety' for col in columns),
        'columns': [col[1] for col in columns]
    }
    
    return schema_info

def create_professional_equipment_data(conn):
    """Create professional equipment data with dynamic schema handling"""
    print("\n🔧 Creating professional equipment data...")
    
    # Get equipment table schema
    schema_info = get_equipment_schema(conn)
    print(f"  Equipment schema: is_active={schema_info['has_is_active']}, critical_to_food_safety={schema_info['has_critical_to_food_safety']}")
    
    equipment_data = [
        ('Pasteurizer HTST-001', 'pasteurizer', 'HTST-001', 'Production Floor A', 'High Temperature Short Time pasteurizer for milk processing', 1),
        ('Cheese Vat CV-001', 'processing_equipment', 'CV-001', 'Production Floor B', 'Stainless steel cheese making vat with temperature control', 1),
        ('Refrigeration Unit RF-001', 'refrigeration', 'RF-001', 'Cold Storage Room', 'Walk-in refrigeration unit for product storage', 1),
        ('Temperature Logger TL-001', 'monitoring_equipment', 'TL-001', 'Quality Lab', 'Digital temperature monitoring system with data logging', 1),
        ('Cleaning System CS-001', 'cleaning_equipment', 'CS-001', 'Sanitation Area', 'Automated cleaning-in-place system for equipment sanitization', 1),
    ]
    
    # Build dynamic INSERT statement based on schema
    base_columns = ['name', 'equipment_type', 'serial_number', 'location', 'notes', 'created_at', 'created_by']
    base_values = [':name', ':equipment_type', ':serial_number', ':location', ':notes', ':created_at', ':created_by']
    
    if schema_info['has_is_active']:
        base_columns.append('is_active')
        base_values.append(':is_active')
    
    if schema_info['has_critical_to_food_safety']:
        base_columns.append('critical_to_food_safety')
        base_values.append(':critical_to_food_safety')
    
    insert_sql = f"""
        INSERT INTO equipment ({', '.join(base_columns)})
        VALUES ({', '.join(base_values)})
    """
    
    for name, equipment_type, serial_number, location, notes, created_by in equipment_data:
        # Build parameters dynamically
        params = {
            'name': name,
            'equipment_type': equipment_type,
            'serial_number': serial_number,
            'location': location,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        }
        
        # Add optional columns if they exist
        if schema_info['has_is_active']:
            params['is_active'] = 1
        
        if schema_info['has_critical_to_food_safety']:
            params['critical_to_food_safety'] = 1
        
        conn.execute(text(insert_sql), params)
    
    print("  ✓ Created equipment records")

if __name__ == "__main__":
    populate_professional_data()
