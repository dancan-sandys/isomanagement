#!/usr/bin/env python3
"""
Dairy Farm Demo Data Creation
Populate the ISO 22000 FSMS platform with comprehensive dairy farm data
"""

import sqlite3
import sys
from datetime import datetime, timedelta

def create_dairy_farm_demo_data():
    """Create comprehensive dairy farm demo data"""
    print("🐄 Creating Dairy Farm Demo Data")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # 1. Create Users (Dairy Farm Staff)
        print("\n👥 Creating Dairy Farm Staff...")
        
        users_data = [
            ('john_mwangi', 'john.mwangi@greenvalleydairy.com', 'John Mwangi', 'manager', 'Management', 'Farm Manager', '0712345678', 'EMP001', True, True),
            ('sarah_odhiambo', 'sarah.odhiambo@greenvalleydairy.com', 'Sarah Odhiambo', 'manager', 'Management', 'Quality Manager', '0723456789', 'EMP002', True, True),
            ('peter_kamau', 'peter.kamau@greenvalleydairy.com', 'Peter Kamau', 'supervisor', 'Production', 'Production Supervisor', '0734567890', 'EMP003', True, True),
            ('mary_wambui', 'mary.wambui@greenvalleydairy.com', 'Mary Wambui', 'operator', 'Production', 'Milk Processing Operator', '0745678901', 'EMP004', True, True),
            ('james_kiptoo', 'james.kiptoo@greenvalleydairy.com', 'James Kiptoo', 'operator', 'Production', 'Pasteurization Operator', '0756789012', 'EMP005', True, True),
            ('grace_akinyi', 'grace.akinyi@greenvalleydairy.com', 'Grace Akinyi', 'operator', 'Production', 'Packaging Operator', '0767890123', 'EMP006', True, True),
            ('david_otieno', 'david.otieno@greenvalleydairy.com', 'David Otieno', 'supervisor', 'Quality', 'Quality Control Supervisor', '0778901234', 'EMP007', True, True),
            ('linda_chebet', 'linda.chebet@greenvalleydairy.com', 'Linda Chebet', 'operator', 'Quality', 'Lab Technician', '0789012345', 'EMP008', True, True),
            ('robert_ndungu', 'robert.ndungu@greenvalleydairy.com', 'Robert Ndungu', 'supervisor', 'Maintenance', 'Maintenance Supervisor', '0790123456', 'EMP009', True, True),
            ('ann_wangari', 'ann.wangari@greenvalleydairy.com', 'Ann Wangari', 'operator', 'Maintenance', 'Equipment Technician', '0701234567', 'EMP010', True, True)
        ]
        
        cursor.execute("DELETE FROM users WHERE id > 1")
        
        for username, email, full_name, role, department, position, phone, emp_id, is_active, is_verified in users_data:
            cursor.execute("""
                INSERT INTO users (username, email, full_name, hashed_password, role_id, status, department, position, phone, employee_id, is_active, is_verified, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (username, email, full_name, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Ge', 2, 'active', department, position, phone, emp_id, is_active, is_verified))
        
        print(f"✅ Created {len(users_data)} dairy farm staff members")
        
        # 2. Create Suppliers
        print("\n🏭 Creating Dairy Farm Suppliers...")
        
        suppliers_data = [
            ('SUP001', 'Kenya Feeds Ltd', 'active', 'supplier', 'John Kamau', 'kenya.feeds@email.com', '+254-20-123456', 'https://kenyafeeds.co.ke', 'P.O. Box 123', 'Industrial Area', 'Nairobi', 'Nairobi', '00100', 'Kenya', 'BR001', 'TIN001', 'Limited Company', 1995, 'ISO 9001, HACCP', '{"ISO 9001": "2025-12-31", "HACCP": "2025-12-31"}', 95.5, '2024-07-01', '2024-10-01', 'LOW', 'High quality dairy feeds supplier', 'Excellent supplier with consistent quality', 2),
            ('SUP002', 'Vet Supplies Kenya', 'active', 'supplier', 'Dr. Sarah Wambui', 'vet.supplies@email.com', '+254-51-234567', 'https://vetsupplies.co.ke', 'P.O. Box 456', 'Nakuru Town', 'Nakuru', 'Rift Valley', '20100', 'Kenya', 'BR002', 'TIN002', 'Limited Company', 2000, 'ISO 9001', '{"ISO 9001": "2025-06-30"}', 92.0, '2024-07-05', '2024-10-05', 'LOW', 'Veterinary medicines and supplies', 'Reliable supplier of veterinary products', 2),
            ('SUP003', 'Milking Equipment Co', 'active', 'supplier', 'Peter Kiprop', 'milking.equipment@email.com', '+254-53-345678', 'https://milkingequipment.co.ke', 'P.O. Box 789', 'Eldoret Town', 'Eldoret', 'Rift Valley', '30100', 'Kenya', 'BR003', 'TIN003', 'Limited Company', 1998, 'ISO 9001, CE Mark', '{"ISO 9001": "2025-03-15", "CE Mark": "2025-12-31"}', 88.5, '2024-07-10', '2024-10-10', 'LOW', 'Milking machines and equipment', 'Quality equipment supplier', 2),
            ('SUP004', 'Packaging Solutions', 'active', 'supplier', 'Mary Njeri', 'packaging.solutions@email.com', '+254-41-456789', 'https://packagingsolutions.co.ke', 'P.O. Box 321', 'Mombasa Port', 'Mombasa', 'Coast', '80100', 'Kenya', 'BR004', 'TIN004', 'Limited Company', 2005, 'ISO 9001', '{"ISO 9001": "2025-09-30"}', 85.0, '2024-07-15', '2024-10-15', 'MEDIUM', 'Milk packaging materials', 'Good packaging supplier', 2),
            ('SUP005', 'Transport Kenya Ltd', 'active', 'supplier', 'James Mwangi', 'transport.kenya@email.com', '+254-20-567890', 'https://transportkenya.co.ke', 'P.O. Box 654', 'Industrial Area', 'Nairobi', 'Nairobi', '00100', 'Kenya', 'BR005', 'TIN005', 'Limited Company', 2002, 'ISO 9001, ISO 14001', '{"ISO 9001": "2025-08-31", "ISO 14001": "2025-08-31"}', 82.5, '2024-07-20', '2024-10-20', 'MEDIUM', 'Milk transportation services', 'Reliable transport services', 2)
        ]
        
        cursor.execute("DELETE FROM suppliers")
        
        for supplier_code, name, status, category, contact_person, email, phone, website, address_line1, address_line2, city, state, postal_code, country, business_registration_number, tax_identification_number, company_type, year_established, certifications, certification_expiry_dates, overall_score, last_evaluation_date, next_evaluation_date, risk_level, risk_factors, notes, created_by in suppliers_data:
            cursor.execute("""
                INSERT INTO suppliers (supplier_code, name, status, category, contact_person, email, phone, website, address_line1, address_line2, city, state, postal_code, country, business_registration_number, tax_identification_number, company_type, year_established, certifications, certification_expiry_dates, overall_score, last_evaluation_date, next_evaluation_date, risk_level, risk_factors, notes, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (supplier_code, name, status, category, contact_person, email, phone, website, address_line1, address_line2, city, state, postal_code, country, business_registration_number, tax_identification_number, company_type, year_established, certifications, certification_expiry_dates, overall_score, last_evaluation_date, next_evaluation_date, risk_level, risk_factors, notes, created_by))
        
        print(f"✅ Created {len(suppliers_data)} dairy farm suppliers")
        
        # 3. Create Equipment
        print("\n🔧 Creating Dairy Farm Equipment...")
        
        equipment_data = [
            ('Pasteurizer HTST-1000', 'pasteurizer', 'HTST-1000-001', 'Production Area', 'High Temperature Short Time Pasteurizer for milk processing', True, True, 2),
            ('Milk Separator MS-500', 'separator', 'MS-500-002', 'Production Area', 'Cream separator for milk processing', True, True, 2),
            ('Packaging Machine PM-200', 'packaging', 'PM-200-003', 'Packaging Area', 'Automatic milk packaging machine', True, True, 2),
            ('Milking Machine MM-50', 'milking', 'MM-50-004', 'Farm Area', 'Automated milking system', True, True, 2),
            ('Milk Tank MT-5000', 'storage', 'MT-5000-005', 'Storage Area', 'Bulk milk storage tank with cooling system', True, True, 2),
            ('Lab Equipment LE-100', 'laboratory', 'LE-100-006', 'Quality Lab', 'Milk quality testing equipment including pH meter and refractometer', False, True, 2)
        ]
        
        cursor.execute("DELETE FROM equipment")
        
        for name, equipment_type, serial_number, location, notes, critical_to_food_safety, is_active, created_by in equipment_data:
            cursor.execute("""
                INSERT INTO equipment (name, equipment_type, serial_number, location, notes, critical_to_food_safety, is_active, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (name, equipment_type, serial_number, location, notes, critical_to_food_safety, is_active, created_by))
        
        print(f"✅ Created {len(equipment_data)} dairy farm equipment items")
        
        # 4. Create HACCP Hazards
        print("\n⚠️ Creating Dairy Farm HACCP Hazards...")
        
        hazards_data = [
            (1, 1, 'biological', 'Bacterial Contamination', 'Pathogenic bacteria in raw milk', 4, 5, 20, 'HIGH', 'Milk pasteurization and proper storage', True, 4, True, 'Critical control point for food safety', '{"step1": "Is control at this step necessary for safety?", "step2": "Is the step specifically designed to eliminate or reduce the likelihood of occurrence?", "step3": "Could contamination occur at this step?", "step4": "Will a subsequent step eliminate or reduce the hazard?"}', '2024-07-01', 2, 2, 'HACCP team decision based on risk assessment', '["PRP001", "PRP002"]', '["DOC001", "DOC002"]', 1, 'HACCP Risk Assessment', '2024-07-01', 2, 'Regular monitoring and verification', 'Daily', 'Monthly', 4, 15, 'MEDIUM', True, 'Risk is acceptable with current controls'),
            (1, 2, 'chemical', 'Chemical Residues', 'Antibiotic residues in milk', 3, 5, 15, 'HIGH', 'Milk testing and withdrawal periods', True, 4, True, 'Critical control point for chemical safety', '{"step1": "Is control at this step necessary for safety?", "step2": "Is the step specifically designed to eliminate or reduce the likelihood of occurrence?", "step3": "Could contamination occur at this step?", "step4": "Will a subsequent step eliminate or reduce the hazard?"}', '2024-07-01', 2, 2, 'HACCP team decision based on risk assessment', '["PRP003"]', '["DOC003"]', 2, 'HACCP Risk Assessment', '2024-07-01', 2, 'Regular testing and monitoring', 'Daily', 'Monthly', 4, 12, 'MEDIUM', True, 'Risk is acceptable with current controls'),
            (1, 3, 'physical', 'Physical Contamination', 'Foreign objects in milk', 2, 3, 6, 'MEDIUM', 'Filtration and visual inspection', True, 3, False, 'Controlled by PRP', '{"step1": "Is control at this step necessary for safety?", "step2": "Is the step specifically designed to eliminate or reduce the likelihood of occurrence?", "step3": "Could contamination occur at this step?", "step4": "Will a subsequent step eliminate or reduce the hazard?"}', '2024-07-01', 2, 2, 'Controlled by PRP programs', '["PRP004"]', '["DOC004"]', 3, 'HACCP Risk Assessment', '2024-07-01', 2, 'Regular inspection and maintenance', 'Weekly', 'Monthly', 3, 6, 'LOW', True, 'Risk is acceptable with current controls')
        ]
        
        cursor.execute("DELETE FROM hazards")
        
        for product_id, process_step_id, hazard_type, hazard_name, description, likelihood, severity, risk_score, risk_level, control_measures, is_controlled, control_effectiveness, is_ccp, ccp_justification, decision_tree_steps, decision_tree_run_at, decision_tree_by, created_by, rationale, prp_reference_ids, reference_documents, risk_register_item_id, risk_assessment_method, risk_assessment_date, risk_assessor_id, risk_treatment_plan, risk_monitoring_frequency, risk_review_frequency, risk_control_effectiveness, risk_residual_score, risk_residual_level, risk_acceptable, risk_justification in hazards_data:
            cursor.execute("""
                INSERT INTO hazards (product_id, process_step_id, hazard_type, hazard_name, description, likelihood, severity, risk_score, risk_level, control_measures, is_controlled, control_effectiveness, is_ccp, ccp_justification, decision_tree_steps, decision_tree_run_at, decision_tree_by, created_by, rationale, prp_reference_ids, reference_documents, risk_register_item_id, risk_assessment_method, risk_assessment_date, risk_assessor_id, risk_treatment_plan, risk_monitoring_frequency, risk_review_frequency, risk_control_effectiveness, risk_residual_score, risk_residual_level, risk_acceptable, risk_justification, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (product_id, process_step_id, hazard_type, hazard_name, description, likelihood, severity, risk_score, risk_level, control_measures, is_controlled, control_effectiveness, is_ccp, ccp_justification, decision_tree_steps, decision_tree_run_at, decision_tree_by, created_by, rationale, prp_reference_ids, reference_documents, risk_register_item_id, risk_assessment_method, risk_assessment_date, risk_assessor_id, risk_treatment_plan, risk_monitoring_frequency, risk_review_frequency, risk_control_effectiveness, risk_residual_score, risk_residual_level, risk_acceptable, risk_justification))
        
        print(f"✅ Created {len(hazards_data)} dairy farm hazards")
        
        # 5. Create PRP Programs
        print("\n📋 Creating Dairy Farm PRP Programs...")
        
        prp_programs_data = [
            ('Good Agricultural Practices (GAP)', 'farm', 'HIGH', 'Ensure safe milk production from farm', 'Farm operations', 'Daily', 'John Mwangi', True),
            ('Good Manufacturing Practices (GMP)', 'production', 'HIGH', 'Maintain hygienic processing conditions', 'Production facility', 'Daily', 'Sarah Odhiambo', True),
            ('Sanitation Standard Operating Procedures (SSOP)', 'sanitation', 'HIGH', 'Equipment and facility cleaning', 'All areas', 'Daily', 'David Otieno', True),
            ('Pest Control Program', 'pest_control', 'MEDIUM', 'Prevent pest infestation', 'All areas', 'Weekly', 'Robert Ndungu', True),
            ('Water Quality Management', 'water_quality', 'HIGH', 'Ensure safe water supply', 'Water systems', 'Monthly', 'Peter Kamau', True)
        ]
        
        cursor.execute("DELETE FROM prp_programs")
        
        for name, program_type, priority, description, scope, frequency, responsible_person, is_active in prp_programs_data:
            cursor.execute("""
                INSERT INTO prp_programs (name, program_type, priority, description, scope, frequency, responsible_person, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (name, program_type, priority, description, scope, frequency, responsible_person, is_active))
        
        print(f"✅ Created {len(prp_programs_data)} dairy farm PRP programs")
        
        # 6. Create Documents
        print("\n📄 Creating Dairy Farm Documents...")
        
        documents_data = [
            ('HACCP Plan', 'haccp_plan', 'approved', 'Complete HACCP plan for dairy operations', 'Sarah Odhiambo', '2024-01-15', '2025-01-15', True),
            ('Food Safety Manual', 'manual', 'approved', 'Comprehensive food safety procedures', 'Sarah Odhiambo', '2024-02-01', '2025-02-01', True),
            ('Standard Operating Procedures', 'sop', 'approved', 'Daily operational procedures', 'Peter Kamau', '2024-02-15', '2025-02-15', True),
            ('Equipment Maintenance Manual', 'manual', 'approved', 'Equipment maintenance procedures', 'Robert Ndungu', '2024-03-01', '2025-03-01', True),
            ('Quality Control Procedures', 'sop', 'approved', 'Quality testing and control procedures', 'David Otieno', '2024-03-15', '2025-03-15', True)
        ]
        
        cursor.execute("DELETE FROM documents")
        
        for title, document_type, status, description, created_by_name, effective_date, review_date, is_active in documents_data:
            cursor.execute("""
                INSERT INTO documents (title, document_type, status, description, created_by, effective_date, review_date, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (title, document_type, status, description, 2, effective_date, review_date, is_active))
        
        print(f"✅ Created {len(documents_data)} dairy farm documents")
        
        # 7. Create Non-Conformances
        print("\n❌ Creating Dairy Farm Non-Conformances...")
        
        non_conformances_data = [
            ('High Bacterial Count in Raw Milk', 'inspection', 'HIGH', 'Raw milk sample exceeded bacterial limits', '2024-07-15', 'OPEN', 'Mary Wambui', 'Samuel Muthee', '2024-07-20', 'Investigate source and implement corrective measures'),
            ('Equipment Calibration Overdue', 'maintenance', 'MEDIUM', 'Pasteurizer temperature sensor not calibrated', '2024-07-10', 'IN_PROGRESS', 'Robert Ndungu', 'Ann Wangari', '2024-07-25', 'Schedule calibration and update maintenance schedule'),
            ('Packaging Material Defect', 'production', 'MEDIUM', 'Milk bottles with manufacturing defects', '2024-07-12', 'OPEN', 'Grace Akinyi', 'Peter Kamau', '2024-07-18', 'Contact supplier and implement incoming inspection')
        ]
        
        cursor.execute("DELETE FROM non_conformances")
        
        for description, source_type, severity, details, reported_date, status, reported_by_name, assigned_to_name, due_date, corrective_action in non_conformances_data:
            cursor.execute("""
                INSERT INTO non_conformances (description, source_type, severity, details, reported_date, status, reported_by, assigned_to, due_date, corrective_action, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (description, source_type, severity, details, reported_date, status, 4, 2, due_date, corrective_action))
        
        print(f"✅ Created {len(non_conformances_data)} dairy farm non-conformances")
        
        # 8. Create Audits
        print("\n🔍 Creating Dairy Farm Audits...")
        
        audits_data = [
            ('Internal HACCP Audit', 'internal', 'HACCP System', '2024-07-01', '2024-07-02', 'completed', 'Sarah Odhiambo', 'John Mwangi', 'HACCP system audit completed successfully'),
            ('Supplier Audit - Kenya Feeds', 'external', 'Supplier Evaluation', '2024-06-15', '2024-06-16', 'completed', 'Peter Kamau', 'John Mwangi', 'Supplier audit completed with minor findings'),
            ('Equipment Maintenance Audit', 'internal', 'Equipment Management', '2024-06-01', '2024-06-02', 'completed', 'Robert Ndungu', 'John Mwangi', 'Equipment maintenance audit completed')
        ]
        
        cursor.execute("DELETE FROM audits")
        
        for title, audit_type, scope, start_date, end_date, status, auditor_name, auditee_name, findings in audits_data:
            cursor.execute("""
                INSERT INTO audits (title, audit_type, scope, start_date, end_date, status, auditor, auditee, findings, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (title, audit_type, scope, start_date, end_date, status, auditor_name, auditee_name, findings))
        
        print(f"✅ Created {len(audits_data)} dairy farm audits")
        
        # 9. Create Batches
        print("\n🥛 Creating Dairy Farm Production Batches...")
        
        batches_data = [
            ('Milk-Batch-2024-001', 'raw_milk', 'in_production', '2024-07-15 06:00:00', '2024-07-15 08:00:00', '5000', 'L', 'Samuel Muthee', 'Morning milk collection'),
            ('Milk-Batch-2024-002', 'raw_milk', 'completed', '2024-07-15 16:00:00', '2024-07-15 18:00:00', '4800', 'L', 'Samuel Muthee', 'Evening milk collection'),
            ('Pasteurized-Milk-2024-001', 'final_product', 'released', '2024-07-15 09:00:00', '2024-07-15 11:00:00', '4500', 'L', 'Mary Wambui', 'Pasteurized whole milk'),
            ('Cream-Batch-2024-001', 'intermediate', 'completed', '2024-07-15 10:00:00', '2024-07-15 12:00:00', '500', 'L', 'James Kiptoo', 'Separated cream')
        ]
        
        cursor.execute("DELETE FROM batches")
        
        for batch_code, batch_type, status, production_start, production_end, quantity, unit, produced_by, description in batches_data:
            cursor.execute("""
                INSERT INTO batches (batch_code, batch_type, status, production_start, production_end, quantity, unit, produced_by, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (batch_code, batch_type, status, production_start, production_end, quantity, unit, produced_by, description))
        
        print(f"✅ Created {len(batches_data)} dairy farm production batches")
        
        # 10. Create Management Reviews
        print("\n📊 Creating Dairy Farm Management Reviews...")
        
        management_reviews_data = [
            ('Q2 2024 Management Review', 'SCHEDULED', 'Quarterly review of food safety management system', '2024-07-01', 'PLANNED', 'John Mwangi', '2024-10-01', 'Quarterly'),
            ('Annual Management Review 2024', 'SCHEDULED', 'Annual comprehensive review of FSMS', '2024-12-15', 'PLANNED', 'John Mwangi', '2025-12-15', 'Annual')
        ]
        
        cursor.execute("DELETE FROM management_reviews")
        
        for title, review_type, review_scope, review_date, status, chairperson_name, next_review_date, review_frequency in management_reviews_data:
            cursor.execute("""
                INSERT INTO management_reviews (title, review_type, review_scope, review_date, status, chairperson_id, next_review_date, review_frequency, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (title, review_type, review_scope, review_date, status, 2, next_review_date, review_frequency, 2))
        
        print(f"✅ Created {len(management_reviews_data)} dairy farm management reviews")
        
        conn.commit()
        print("\n🎉 Dairy Farm Demo Data Creation Completed Successfully!")
        print(f"\n📊 Demo Data Summary:")
        print(f"   👥 Staff Members: {len(users_data)}")
        print(f"   🏭 Suppliers: {len(suppliers_data)}")
        print(f"   🔧 Equipment: {len(equipment_data)}")
        print(f"   ⚠️ Hazards: {len(hazards_data)}")
        print(f"   📋 PRP Programs: {len(prp_programs_data)}")
        print(f"   📄 Documents: {len(documents_data)}")
        print(f"   ❌ Non-Conformances: {len(non_conformances_data)}")
        print(f"   🔍 Audits: {len(audits_data)}")
        print(f"   🥛 Production Batches: {len(batches_data)}")
        print(f"   📊 Management Reviews: {len(management_reviews_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating dairy farm demo data: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = create_dairy_farm_demo_data()
    sys.exit(0 if success else 1)
