#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed realistic demo data for an engineering firm: users/roles, equipment, maintenance & calibration,
suppliers, documents, and an example process (treated via existing HACCP models for demo purposes).
"""
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings


def upsert_roles_and_permissions():
    # Ensure RBAC roles/permissions exist
    try:
        from create_rbac_seed_data import create_permissions, create_default_roles
        create_permissions()
        create_default_roles()
    except Exception as e:
        print(f"⚠️  RBAC seeding encountered an issue (continuing): {e}")


def insert_users(conn):
    print("👤 Creating engineering demo users…")
    # Password hash of 'admin123' like other seeds
    default_pwd = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO"
    users = [
        ("eng_manager", "eng.manager@example.com", "Engineering Manager", default_pwd, "Engineering", "Engineering Manager"),
        ("quality_engineer", "quality.engineer@example.com", "Quality Engineer", default_pwd, "Quality", "Quality Engineer"),
        ("maintenance_engineer", "maintenance.engineer@example.com", "Maintenance Engineer", default_pwd, "Maintenance", "Maintenance Engineer"),
        ("project_manager", "pm@example.com", "Project Manager", default_pwd, "Projects", "Project Manager"),
        ("test_technician", "lab.tech@example.com", "Test Technician", default_pwd, "Lab", "Test Technician"),
        ("welder", "welder@example.com", "Certified Welder", default_pwd, "Production", "Welder"),
    ]

    for u in users:
        conn.execute(text(
            """
            INSERT INTO users (username, email, full_name, hashed_password, role_id, status, department, position,
                               is_active, is_verified, created_at)
            SELECT :username, :email, :full_name, :pwd, COALESCE((SELECT id FROM roles WHERE name = :role_name LIMIT 1), 1),
                   'ACTIVE', :dept, :pos, 1, 1, :now
            WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = :username)
            """
        ), {
            "username": u[0],
            "email": u[1],
            "full_name": u[2],
            "pwd": u[3],
            "dept": u[4],
            "pos": u[5],
            "role_name": "System Administrator" if u[0] == "eng_manager" else (
                "QA Manager" if u[0] == "quality_engineer" else (
                    "Maintenance Engineer" if u[0] == "maintenance_engineer" else (
                        "Production Manager" if u[0] == "project_manager" else "Line Operator"
                    )
                )
            ),
            "now": datetime.utcnow().isoformat()
        })
    print("✅ Users created")


def insert_documents(conn):
    print("📄 Creating engineering QMS documents…")
    docs = [
        ("QM-ENG-001", "Quality Management Manual", "ISO 9001-aligned quality manual for engineering operations", "manual", "quality", "1.0", "approved", 1),
        ("WPS-001", "Welding Procedure Specification (WPS) - Carbon Steel", "Qualified WPS for GTAW on A36", "specification", "quality", "1.2", "approved", 1),
        ("WI-ASM-010", "Work Instruction - Pressure Vessel Assembly", "Step-by-step assembly and torque sequence", "work_instruction", "quality", "2.0", "approved", 1),
        ("FRM-INS-020", "Inspection Report Template", "Template for in-process and final inspections", "form", "quality", "1.0", "approved", 1),
        ("PROC-NC-005", "Nonconformance and CAPA Procedure", "How to log, investigate, and resolve NCs", "procedure", "quality", "1.1", "approved", 1),
        # Add variety for dashboard charts and approvals pipeline
        ("POL-SEC-001", "Information Security Policy", "Policy for securing information assets", "policy", "quality", "1.0", "approved", 1),
        ("REC-TRN-015", "Training Attendance Record", "Record template for training sessions", "record", "training", "1.0", "approved", 1),
        ("CHK-MNT-030", "Preventive Maintenance Checklist", "Checklist for CNC preventive maintenance", "checklist", "maintenance", "1.0", "under_review", 1),
        ("PROC-SUP-011", "Supplier Evaluation Procedure", "Procedure for evaluating suppliers", "procedure", "supplier", "1.0", "draft", 1),
    ]
    for d in docs:
        conn.execute(text(
            """
            INSERT INTO documents (document_number, title, description, document_type, category, version, status, created_by, created_at)
            SELECT :num, :title, :desc, :dtype, :cat, :ver, :status, :uid, :now
            WHERE NOT EXISTS (SELECT 1 FROM documents WHERE document_number = :num)
            """
        ), {
            "num": d[0], "title": d[1], "desc": d[2], "dtype": d[3], "cat": d[4],
            "ver": d[5], "status": d[6].upper(), "uid": d[7], "now": datetime.utcnow().isoformat()
        })
    print("✅ Documents created")

    # Seed a couple of pending document approvals to light up dashboards
    conn.execute(text(
        """
        INSERT INTO document_approvals (document_id, approver_id, approval_order, status, created_at)
        SELECT (SELECT id FROM documents WHERE document_number='CHK-MNT-030'), 1, 1, 'pending', :now
        WHERE NOT EXISTS (
            SELECT 1 FROM document_approvals WHERE document_id=(SELECT id FROM documents WHERE document_number='CHK-MNT-030')
        )
        """
    ), {"now": datetime.utcnow().isoformat()})


def insert_suppliers(conn):
    print("🏭 Creating engineering suppliers…")
    suppliers = [
        ("MAT-STEEL", "Prime Steel Ltd.", "active", "materials", "Rolled steel plate supplier", "steel.sales@prime.example.com"),
        ("COAT-ZINC", "ZincCoat Services", "active", "coatings", "Hot-dip galvanizing services", "orders@zinccoat.example.com"),
        ("LAB-METRO", "Metrology Labs Inc.", "active", "services", "Accredited calibration laboratory (ISO 17025)", "support@metrolab.example.com"),
    ]
    for s in suppliers:
        conn.execute(text(
            """
            INSERT INTO suppliers (supplier_code, name, status, category, notes, email, created_by, created_at)
            SELECT :code, :name, :status, :cat, :notes, :email, :uid, :now
            WHERE NOT EXISTS (SELECT 1 FROM suppliers WHERE supplier_code = :code)
            """
        ), {"code": s[0], "name": s[1], "status": s[2], "cat": s[3], "notes": s[4], "email": s[5], "uid": 1, "now": datetime.utcnow().isoformat()})
    print("✅ Suppliers created")

    # Ensure materials exist for suppliers (used by deliveries)
    print("📦 Creating supplier materials…")
    materials = [
        ("MAT-STEEL-A36", "Steel Plate A36", "MAT-STEEL", "metal"),
        ("COAT-ZN-SVC", "Zinc Coating Service", "COAT-ZINC", "service"),
        ("LAB-CAL-SVC", "Calibration Service", "LAB-METRO", "service"),
    ]
    for mcode, name, scode, mcat in materials:
        conn.execute(text(
            """
            INSERT INTO materials (material_code, name, supplier_id, category, is_active, approval_status, created_by, created_at)
            SELECT :mcode, :name, (SELECT id FROM suppliers WHERE supplier_code=:scode), :mcat, 1, 'approved', 1, :now
            WHERE NOT EXISTS (SELECT 1 FROM materials WHERE material_code=:mcode)
            """
        ), {"mcode": mcode, "name": name, "scode": scode, "mcat": mcat, "now": datetime.utcnow().isoformat()})

    # Supplier evaluations to power supplier KPIs
    evaluation_rows = [
        ("MAT-STEEL", "Q2 2025", 4.6, 4.7, 4.2, 4.5, 4.0, 4.5),
        ("COAT-ZINC", "Q2 2025", 4.2, 4.4, 4.1, 4.3, 4.0, 4.2),
        ("LAB-METRO", "Q2 2025", 4.8, 4.9, 4.6, 4.7, 4.9, 4.8),
    ]
    for code, period, qs, ds, ps, cs, hs, overall in evaluation_rows:
        conn.execute(text(
            """
            INSERT INTO supplier_evaluations (
                supplier_id, evaluation_period, evaluation_date, status,
                quality_score, delivery_score, price_score, communication_score, hygiene_score, overall_score,
                issues_identified, improvement_actions, follow_up_required, evaluated_by
            )
            SELECT (SELECT id FROM suppliers WHERE supplier_code=:code), :period, :edate, 'completed',
                   :qs, :ds, :ps, :cs, :hs, :overall,
                   '[]', '[]', 0, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM supplier_evaluations WHERE supplier_id=(SELECT id FROM suppliers WHERE supplier_code=:code) AND evaluation_period=:period
            )
            """
        ), {"code": code, "period": period, "edate": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "qs": qs, "ds": ds, "ps": ps, "cs": cs, "hs": hs, "overall": overall})

    # Incoming deliveries with inspection statuses
    deliveries = [
        ("DEL-0001", "MAT-STEEL", "CMM-PR-0001", (datetime.utcnow() - timedelta(days=1)).isoformat(), 1500.0, "kg", "BATCH-STEEL-001", "passed"),
        ("DEL-0002", "COAT-ZINC", "WLD-PW-202", (datetime.utcnow() - timedelta(days=2)).isoformat(), 200.0, "pcs", "BATCH-ZN-042", "quarantined"),
        ("DEL-0003", "LAB-METRO", "UTM-5980-0007", (datetime.utcnow() - timedelta(days=7)).isoformat(), 1.0, "service", "BATCH-CAL-2025-07", "passed"),
    ]
    for dnum, scode, eq_sn, ddate, qty, unit, lot, istatus in deliveries:
        conn.execute(text(
            """
            INSERT INTO incoming_deliveries (
                delivery_number, supplier_id, material_id, delivery_date, quantity_received, unit, lot_number,
                inspection_status, inspected_by, created_by
            )
            SELECT :dnum, (SELECT id FROM suppliers WHERE supplier_code=:scode),
                   (SELECT id FROM materials WHERE supplier_id=(SELECT id FROM suppliers WHERE supplier_code=:scode) ORDER BY id LIMIT 1), :ddate, :qty, :unit, :lot,
                   :istatus, 1, 1
            WHERE NOT EXISTS (SELECT 1 FROM incoming_deliveries WHERE delivery_number=:dnum)
            """
        ), {"dnum": dnum, "scode": scode, "ddate": ddate, "qty": qty, "unit": unit, "lot": lot, "istatus": istatus})


def insert_equipment(conn):
    print("🛠️  Creating equipment, maintenance and calibration plans…")
    equipment = [
        ("Zeiss CMM PRISMO 7", "CMM", "CMM-PR-0001", "Metrology Lab"),
        ("Instron UTM 5980", "Universal Testing Machine", "UTM-5980-0007", "Lab"),
        ("Norbar Torque Wrench 1000", "Torque Tool", "TW-1000-042", "Assembly"),
        ("Lincoln Electric Power Wave", "Welding Machine", "WLD-PW-202", "Welding Bay"),
        ("Haas VF-4", "CNC Mill", "CNC-HV4-311", "Machine Shop"),
    ]
    for e in equipment:
        conn.execute(text(
            """
            INSERT INTO equipment (name, equipment_type, serial_number, location, created_by, created_at)
            SELECT :name, :etype, :sn, :loc, :uid, :now
            WHERE NOT EXISTS (SELECT 1 FROM equipment WHERE serial_number = :sn)
            """
        ), {"name": e[0], "etype": e[1], "sn": e[2], "loc": e[3], "uid": 1, "now": datetime.utcnow().isoformat()})

    # Maintenance plans
    conn.execute(text(
        """
        INSERT INTO maintenance_plans (equipment_id, frequency_days, maintenance_type, last_performed_at, next_due_at, active)
        SELECT (SELECT id FROM equipment WHERE serial_number='CNC-HV4-311'), 30, 'preventive', :last, :next, 1
        WHERE NOT EXISTS (SELECT 1 FROM maintenance_plans WHERE equipment_id=(SELECT id FROM equipment WHERE serial_number='CNC-HV4-311'))
        """
    ), {"last": (datetime.utcnow() - timedelta(days=25)).isoformat(), "next": (datetime.utcnow() + timedelta(days=5)).isoformat()})

    # Calibration plans
    conn.execute(text(
        """
        INSERT INTO calibration_plans (equipment_id, schedule_date, last_calibrated_at, next_due_at, active)
        SELECT (SELECT id FROM equipment WHERE serial_number='CMM-PR-0001'), :sched, :last, :due, 1
        WHERE NOT EXISTS (SELECT 1 FROM calibration_plans WHERE equipment_id=(SELECT id FROM equipment WHERE serial_number='CMM-PR-0001'))
        """
    ), {"sched": (datetime.utcnow() + timedelta(days=3)).isoformat(), "last": (datetime.utcnow() - timedelta(days=360)).isoformat(), "due": (datetime.utcnow() + timedelta(days=5)).isoformat()})

    conn.execute(text(
        """
        INSERT INTO calibration_plans (equipment_id, schedule_date, last_calibrated_at, next_due_at, active)
        SELECT (SELECT id FROM equipment WHERE serial_number='TW-1000-042'), :sched, :last, :due, 1
        WHERE NOT EXISTS (SELECT 1 FROM calibration_plans WHERE equipment_id=(SELECT id FROM equipment WHERE serial_number='TW-1000-042'))
        """
    ), {"sched": (datetime.utcnow() + timedelta(days=1)).isoformat(), "last": (datetime.utcnow() - timedelta(days=170)).isoformat(), "due": (datetime.utcnow() + timedelta(days=10)).isoformat()})

    print("✅ Equipment, maintenance & calibration configured")


def insert_demo_process(conn):
    print("🧩 Creating a demo product/process with control points…")
    # Use existing HACCP product table to model a controlled engineering process
    conn.execute(text(
        """
        INSERT INTO products (product_code, name, description, category, formulation, allergens, created_by, created_at)
        SELECT 'ASM-PRV-001', 'Pressure Vessel Assembly', 'Assembly of ASME VIII vessel', 'assembly', '{}', '[]', 1, :now
        WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_code='ASM-PRV-001')
        """
    ), {"now": datetime.utcnow().isoformat()})

    # Basic process flow steps
    steps = [
        (1, "Incoming Material Inspection"),
        (2, "Fit-up & Tack Welding"),
        (3, "Full Welding"),
        (4, "Heat Treatment"),
        (5, "Hydrostatic Test"),
        (6, "Final Inspection & Release"),
    ]
    for num, name in steps:
        conn.execute(text(
            """
            INSERT INTO process_flows (product_id, step_number, step_name, description, created_by, created_at)
            SELECT (SELECT id FROM products WHERE product_code='ASM-PRV-001'), :sn, :name, '', 1, :now
            WHERE NOT EXISTS (
                SELECT 1 FROM process_flows WHERE product_id=(SELECT id FROM products WHERE product_code='ASM-PRV-001') AND step_number=:sn
            )
            """
        ), {"sn": num, "name": name, "now": datetime.utcnow().isoformat()})

    # Example hazards as process risks (metallurgical defect, leakage)
    hazards = [
        (2, 'physical', 'Crack initiation during tack', 3, 3, True, 3, False, None),
        (3, 'physical', 'Incomplete fusion / porosity', 4, 4, True, 4, True, 'Critical weld integrity'),
        (5, 'physical', 'Leak during hydrotest', 2, 5, True, 4, True, 'Pressure boundary failure risk'),
    ]
    for h in hazards:
        conn.execute(text(
            """
            INSERT INTO hazards (product_id, process_step_id, hazard_type, hazard_name, description, likelihood, severity, risk_score, risk_level,
                                 control_measures, is_controlled, control_effectiveness, is_ccp, ccp_justification, created_by, created_at)
            SELECT (SELECT id FROM products WHERE product_code='ASM-PRV-001'),
                   (SELECT id FROM process_flows WHERE product_id=(SELECT id FROM products WHERE product_code='ASM-PRV-001') AND step_number=:sn),
                   :htype, :hname, '', :like, :sev, (:like * :sev), CASE WHEN (:like * :sev) >= 15 THEN 'critical' WHEN (:like * :sev) >= 8 THEN 'high' WHEN (:like * :sev) >= 4 THEN 'medium' ELSE 'low' END,
                   'Qualified WPS, NDE (VT/PT/RT as applicable), welder qualification, procedure qualification records',
                   :ctrl, :eff, :is_ccp, :justif, 1, :now
            WHERE NOT EXISTS (SELECT 1 FROM hazards WHERE hazard_name=:hname)
            """
        ), {"sn": h[0], "htype": h[1], "hname": h[2], "like": h[3], "sev": h[4], "ctrl": h[5], "eff": h[6], "is_ccp": h[7], "justif": h[8], "now": datetime.utcnow().isoformat()})
    print("✅ Demo process created")


def insert_haccp_like_plan(conn):
    print("🗂️  Creating a versioned process control plan (using HACCP plan tables)…")
    # Minimal plan content
    content = {
        "scope": "Pressure Vessel Assembly",
        "controls": [
            {"step": "Welding", "control": "WPS WPS-001, PQR verified, welder qualified"},
            {"step": "Hydrostatic Test", "control": "1.5x design pressure for 30 minutes, no leakage"},
        ],
    }
    import json
    conn.execute(text(
        """
        INSERT INTO haccp_plans (product_id, title, description, status, version, current_content, effective_date, review_date, created_by, created_at)
        SELECT (SELECT id FROM products WHERE product_code='ASM-PRV-001'),
               'Process Control Plan - Pressure Vessel', 'Control measures for critical steps', 'draft', '1.0', :content,
               :eff, :rev, 1, :now
        WHERE NOT EXISTS (SELECT 1 FROM haccp_plans WHERE product_id=(SELECT id FROM products WHERE product_code='ASM-PRV-001'))
        """
    ), {"content": json.dumps(content), "eff": (datetime.utcnow() + timedelta(days=1)).isoformat(), "rev": (datetime.utcnow() + timedelta(days=365)).isoformat(), "now": datetime.utcnow().isoformat()})

    conn.execute(text(
        """
        INSERT INTO haccp_plan_versions (plan_id, version_number, content, change_description, created_by, created_at)
        SELECT p.id, '1.0', :content, 'Initial plan', 1, :now
        FROM haccp_plans p
        WHERE p.product_id=(SELECT id FROM products WHERE product_code='ASM-PRV-001')
          AND NOT EXISTS (
            SELECT 1 FROM haccp_plan_versions v WHERE v.plan_id=p.id AND v.version_number='1.0'
          )
        """
    ), {"content": json.dumps(content), "now": datetime.utcnow().isoformat()})
    print("✅ Control plan created with initial version")


def insert_prp(conn):
    print("🧼 Seeding PRP programs & checklists…")
    programs = [
        ("PRP-CLEAN-001", "Cleaning & Sanitation", "Plant-wide sanitation program", "cleaning_sanitation", "monthly"),
        ("PRP-PEST-001", "Pest Control Program", "Integrated pest management", "pest_control", "monthly"),
        ("PRP-MAINT-001", "Equipment Maintenance", "Preventive maintenance for critical assets", "maintenance", "monthly"),
    ]
    for code, name, desc, cat, freq in programs:
        conn.execute(text(
            """
            INSERT INTO prp_programs (program_code, name, description, category, status, objective, scope, responsible_department, frequency, next_due_date, created_by, created_at)
            SELECT :code, :name, :desc, :cat, 'active', 'Maintain hygiene and control risks', 'All operations', 'Quality', :freq, :next_due, 1, :now
            WHERE NOT EXISTS (SELECT 1 FROM prp_programs WHERE program_code=:code)
            """
        ), {"code": code, "name": name, "desc": desc, "cat": cat, "freq": freq, "next_due": (datetime.utcnow() + timedelta(days=7)).isoformat(), "now": datetime.utcnow().isoformat()})

    # Checklists (one completed, one pending, one in progress)
    checklists = [
        ("PRP-CLEAN-D-202508", "Daily Cleaning Checklist", "PRP-CLEAN-001", "completed", -2, -1, 98.0),
        ("PRP-PEST-M-202508", "Monthly Pest Control Checklist", "PRP-PEST-001", "pending", 7, 8, 0.0),
        ("PRP-MAINT-W-202508", "Weekly Maintenance Checklist", "PRP-MAINT-001", "in_progress", -1, 0, 40.0),
    ]
    for code, name, prog_code, status, start_offset, due_offset, comp_pct in checklists:
        conn.execute(text(
            """
            INSERT INTO prp_checklists (
                program_id, checklist_code, name, description, status, scheduled_date, due_date, completed_date,
                assigned_to, total_items, passed_items, failed_items, compliance_percentage, created_by, created_at
            )
            SELECT (SELECT id FROM prp_programs WHERE program_code=:pcode), :code, :name, '', :status,
                   :sched, :due, CASE WHEN :status='completed' THEN :completed ELSE NULL END,
                   1, 20, CASE WHEN :status='completed' THEN 19 ELSE 8 END, CASE WHEN :status='completed' THEN 1 ELSE 2 END, :comp,
                   1, :now
            WHERE NOT EXISTS (SELECT 1 FROM prp_checklists WHERE checklist_code=:code)
            """
        ), {
            "pcode": prog_code, "code": code, "name": name, "status": status,
            "sched": (datetime.utcnow() + timedelta(days=start_offset)).isoformat(),
            "due": (datetime.utcnow() + timedelta(days=due_offset)).isoformat(),
            "completed": (datetime.utcnow() + timedelta(days=due_offset)).isoformat(),
            "comp": comp_pct, "now": datetime.utcnow().isoformat()
        })
    print("✅ PRP seeded")


def insert_training(conn):
    print("🎓 Seeding training programs & sessions…")
    conn.execute(text(
        """
        INSERT INTO training_programs (code, title, description, department, created_by, created_at)
        SELECT 'TRN-WELD-001', 'Welding Safety & Quality', 'Training on WPS, PQR, and visual inspection', 'Production', 1, :now
        WHERE NOT EXISTS (SELECT 1 FROM training_programs WHERE code='TRN-WELD-001')
        """
    ), {"now": datetime.utcnow().isoformat()})

    conn.execute(text(
        """
        INSERT INTO training_sessions (program_id, session_date, location, trainer, notes, created_by, created_at)
        SELECT (SELECT id FROM training_programs WHERE code='TRN-WELD-001'), :date1, 'Training Room A', 'QA Manager', 'Intro to welding quality', 1, :now
        WHERE NOT EXISTS (SELECT 1 FROM training_sessions WHERE program_id=(SELECT id FROM training_programs WHERE code='TRN-WELD-001'))
        """
    ), {"date1": (datetime.utcnow() - timedelta(days=5)).isoformat(), "now": datetime.utcnow().isoformat()})

    # Attendance: mark most users attended
    for username in ["welder", "test_technician", "maintenance_engineer"]:
        conn.execute(text(
            """
            INSERT INTO training_attendance (session_id, user_id, attended, created_at)
            SELECT (SELECT id FROM training_sessions WHERE program_id=(SELECT id FROM training_programs WHERE code='TRN-WELD-001')),
                   (SELECT id FROM users WHERE username=:uname), 1, :now
            WHERE NOT EXISTS (
                SELECT 1 FROM training_attendance WHERE session_id=(SELECT id FROM training_sessions WHERE program_id=(SELECT id FROM training_programs WHERE code='TRN-WELD-001')) AND user_id=(SELECT id FROM users WHERE username=:uname)
            )
            """
        ), {"uname": username, "now": datetime.utcnow().isoformat()})
    print("✅ Training seeded")


def insert_nc_and_capa(conn):
    print("⚠️  Seeding Non-Conformances & CAPAs…")
    ncs = [
        ("NC-2025-001", "Porosity detected in weld", "welding defects found during VT", "audit", "high", -7, 14),
        ("NC-2025-002", "Hydrotest leakage at nozzle", "minor leak observed, rework required", "haccp", "critical", -2, 10),
    ]
    for nc_num, title, desc, src, sev, reported_offset, target_offset in ncs:
        conn.execute(text(
            """
            INSERT INTO non_conformances (
                nc_number, title, description, source, severity, status, reported_date, target_resolution_date, reported_by, created_at
            )
            SELECT :nc, :title, :desc, :src, :sev, 'open', :rep, :target, 1, :now
            WHERE NOT EXISTS (SELECT 1 FROM non_conformances WHERE nc_number=:nc)
            """
        ), {"nc": nc_num, "title": title, "desc": desc, "src": src, "sev": sev,
            "rep": (datetime.utcnow() + timedelta(days=reported_offset)).isoformat(),
            "target": (datetime.utcnow() + timedelta(days=target_offset)).isoformat(),
            "now": datetime.utcnow().isoformat()})

    # CAPA for first NC
    conn.execute(text(
        """
        INSERT INTO capa_actions (
            capa_number, non_conformance_id, title, description, action_type, responsible_person,
            assigned_date, target_completion_date, status, progress_percentage, created_by, created_at
        )
        SELECT 'CAPA-2025-1001', (SELECT id FROM non_conformances WHERE nc_number='NC-2025-001'), 'Repair weld and re-inspect',
               'Grind and re-weld porosity area, RT after repair', 'corrective', 1,
               :adate, :tdate, 'in_progress', 60.0, 1, :now
        WHERE NOT EXISTS (SELECT 1 FROM capa_actions WHERE capa_number='CAPA-2025-1001')
        """
    ), {"adate": (datetime.utcnow() - timedelta(days=2)).isoformat(), "tdate": (datetime.utcnow() + timedelta(days=5)).isoformat(), "now": datetime.utcnow().isoformat()})
    print("✅ NC & CAPA seeded")


def insert_traceability(conn):
    print("🔗 Seeding traceability batches & recall…")
    # Batches
    batches = [
        ("BATCH-STEEL-001", "raw_milk", "completed", (datetime.utcnow() - timedelta(days=10)).isoformat()),
        ("BATCH-ASM-001", "final_product", "in_production", (datetime.utcnow() - timedelta(days=1)).isoformat()),
        ("BATCH-ZN-042", "additive", "completed", (datetime.utcnow() - timedelta(days=6)).isoformat()),
    ]
    for bnum, btype, status, pdate in batches:
        conn.execute(text(
            """
            INSERT INTO batches (batch_number, batch_type, status, production_date, created_by, created_at)
            SELECT :bnum, :btype, :status, :pdate, 1, :now
            WHERE NOT EXISTS (SELECT 1 FROM batches WHERE batch_number=:bnum)
            """
        ), {"bnum": bnum, "btype": btype, "status": status, "pdate": pdate, "now": datetime.utcnow().isoformat()})

    # Links (ingredient to product)
    conn.execute(text(
        """
        INSERT INTO traceability_links (batch_id, linked_batch_id, relationship_type, usage_date, process_step, created_by, created_at)
        SELECT (SELECT id FROM batches WHERE batch_number='BATCH-ASM-001'), (SELECT id FROM batches WHERE batch_number='BATCH-STEEL-001'), 'ingredient', :udate, 'Assembly', 1, :now
        WHERE NOT EXISTS (
            SELECT 1 FROM traceability_links WHERE batch_id=(SELECT id FROM batches WHERE batch_number='BATCH-ASM-001') AND linked_batch_id=(SELECT id FROM batches WHERE batch_number='BATCH-STEEL-001')
        )
        """
    ), {"udate": (datetime.utcnow() - timedelta(days=1)).isoformat(), "now": datetime.utcnow().isoformat()})

    # Recall draft
    conn.execute(text(
        """
        INSERT INTO recalls (recall_number, recall_type, status, title, description, reason, issue_discovered_date, assigned_to, created_by, created_at)
        SELECT 'RECALL-2025-001', 'class_ii', 'draft', 'Potential material mix-up', 'Traceability check indicates potential mix-up', 'Supplier batch mismatch', :idate, 1, 1, :now
        WHERE NOT EXISTS (SELECT 1 FROM recalls WHERE recall_number='RECALL-2025-001')
        """
    ), {"idate": (datetime.utcnow() - timedelta(days=3)).isoformat(), "now": datetime.utcnow().isoformat()})
    print("✅ Traceability seeded")


def main():
    print("🚀 Seeding engineering demo data…")
    upsert_roles_and_permissions()

    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        insert_users(conn)
        insert_documents(conn)
        insert_suppliers(conn)
        insert_equipment(conn)
        insert_demo_process(conn)
        insert_haccp_like_plan(conn)
        insert_prp(conn)
        insert_training(conn)
        insert_nc_and_capa(conn)
        insert_traceability(conn)

    print("🎉 Engineering demo data ready.")


if __name__ == "__main__":
    main()



