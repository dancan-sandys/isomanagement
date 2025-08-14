#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed realistic demo data for an engineering firm: users/roles, equipment, maintenance & calibration,
suppliers, documents, and an example process (treated via existing HACCP models for demo purposes).
"""
import sys
import os
from datetime import datetime, timedelta

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

    print("🎉 Engineering demo data ready.")


if __name__ == "__main__":
    main()



