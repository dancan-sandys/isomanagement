"""
Presentation / demo data aligned with setup_database_complete.py (same payloads as iso22000_fsms.db seeds).

Run after initialize_database_complete.py (RBAC + admin). Does not wipe RBAC.

- Demo **users** (~12 including `admin`): created first, idempotent per username. Maps roles to the
  four roles from `initialize_database_complete` (QA Manager, Production Manager, Line Operator,
  System Administrator) because this project does not seed ten distinct roles like the old script.

- Suppliers, products, HACCP, batches, etc.: run only when `products` is empty (unless you reset DB).

Disable all demo with env: ISO_SEED_DEMO=0
"""

from __future__ import annotations

import os
import sys
from typing import Any

from sqlalchemy import text


def _want_demo() -> bool:
    return os.environ.get("ISO_SEED_DEMO", "1").strip().lower() not in ("0", "false", "no")


def _has_products(conn) -> bool:
    try:
        n = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        return bool(n and int(n) > 0)
    except Exception:
        return False


def seed_demo_personas(db) -> None:
    """
    Insert ~11 non-admin users (12 total with `admin`) matching setup_database_complete personas.
    Roles map onto the four seeded roles: QA Manager, Production Manager, Line Operator
    (System Administrator reserved for `admin`).

    Required for create_professional_haccp_data (line_operator, qa_supervisor, haccp_coordinator).
    Password for all demo accounts: admin123.
    """
    from app.models.user import User, UserStatus
    from app.models.rbac import Role
    from app.core.security import get_password_hash

    hp = get_password_hash("admin123")

    def rid(name: str) -> int | None:
        r = db.query(Role).filter(Role.name == name).first()
        return r.id if r else None

    r_sys = rid("System Administrator")
    r_qa = rid("QA Manager")
    r_pm = rid("Production Manager")
    r_lo = rid("Line Operator")
    if not r_sys:
        print("⚠️  seed_demo_personas: System Administrator role missing; skip personas")
        return

    # Same usernames / emails / jobs as setup_database_complete.create_professional_users; role = one of four roles we have.
    # Tuple: username, email, full_name, position, department_name, phone, employee_id, role_key in ("qa","pm","lo")
    specs: list[tuple[str, str, str, str, str, str, str, str]] = [
        ("fs_manager", "fs.manager@foodsafe.com", "Sarah Johnson", "Food Safety Manager", "Quality Assurance", "+1-555-0101", "FSM001", "qa"),
        ("qa_director", "qa.director@foodsafe.com", "Michael Chen", "QA Director", "Quality Assurance", "+1-555-0102", "QAD001", "qa"),
        ("qa_supervisor", "qa.supervisor@foodsafe.com", "Lisa Rodriguez", "QA Supervisor", "Quality Assurance", "+1-555-0104", "QAS001", "qa"),
        ("haccp_coordinator", "haccp.coordinator@foodsafe.com", "David Kim", "HACCP Coordinator", "Quality Assurance", "+1-555-0105", "HC001", "qa"),
        ("production_supervisor", "production.supervisor@foodsafe.com", "James Brown", "Production Supervisor", "Production", "+1-555-0107", "PS001", "pm"),
        ("line_operator", "line.operator@foodsafe.com", "Thomas Wilson", "Line Operator", "Production", "+1-555-0109", "LO001", "lo"),
        ("maintenance_manager", "maintenance.manager@foodsafe.com", "Kevin Davis", "Maintenance Manager", "Maintenance", "+1-555-0110", "MM001", "pm"),
        ("calibration_tech", "calibration.tech@foodsafe.com", "Amanda Taylor", "Calibration Technician", "Maintenance", "+1-555-0111", "CT001", "lo"),
        ("hr_manager", "hr.manager@foodsafe.com", "Patricia Smith", "HR Manager", "Human Resources", "+1-555-0112", "HRM001", "qa"),
        ("compliance_officer", "compliance.officer@foodsafe.com", "Robert Johnson", "Compliance Officer", "Compliance", "+1-555-0113", "CO001", "qa"),
        ("auditor", "auditor@foodsafe.com", "Maria Garcia", "Internal Auditor", "Quality Assurance", "+1-555-0114", "AUD001", "qa"),
    ]

    def role_id_for(key: str) -> int:
        if key == "pm":
            return r_pm or r_sys
        if key == "lo":
            return r_lo or r_pm or r_sys
        return r_qa or r_sys

    created = 0
    for username, email, full_name, position, dept, phone, emp_id, rk in specs:
        if db.query(User).filter(User.username == username).first():
            continue
        db.add(
            User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=hp,
                role_id=role_id_for(rk),
                status=UserStatus.ACTIVE,
                department_name=dept,
                position=position,
                phone=phone,
                employee_id=emp_id,
                is_active=True,
                is_verified=True,
            )
        )
        created += 1
    if created:
        db.commit()
        print(f"✅ Demo personas: created {created} users (password: admin123; total demo roster 12 with admin)")
    else:
        print("⏭️  Demo personas: all present, skipped")


def run_presentation_demo(engine: Any) -> bool:
    """
    Populate suppliers, materials, products, HACCP, batches, etc. using setup_database_complete
    functions (same as full setup, without clearing RBAC or re-seeding permissions).
    """
    if not _want_demo():
        print("⏭️  Presentation demo seed skipped (ISO_SEED_DEMO=0)")
        return True

    # Import lazily — pulls large module after app path is set
    import setup_database_complete as sdc

    from app.core.database import SessionLocal

    # Always add missing demo users first (even if products already exist — e.g. DB had data but few users).
    db = SessionLocal()
    try:
        seed_demo_personas(db)
    finally:
        db.close()

    with engine.connect() as conn:
        if _has_products(conn):
            print(
                "⏭️  Skipping suppliers/products/HACCP/equipment seed — products table already has data. "
                "(Demo users above were still added if missing.)"
            )
            return True

    print("\n🏭 Seeding presentation data (suppliers, products, HACCP, batches, equipment)…")
    try:
        with engine.begin() as conn:
            sdc.create_professional_suppliers(conn)
            sdc.create_professional_materials(conn)
            sdc.create_professional_contact_surfaces(conn)
            sdc.create_professional_products(conn)
            sdc.assign_contact_surfaces_to_products(conn)
            sdc.create_professional_documents(conn)
            sdc.create_professional_batches(conn)
            sdc.create_professional_haccp_data(conn)
            sdc.create_monitoring_and_verification_logs(conn)
            sdc.create_professional_equipment_data(conn)
        print("✅ Presentation demo data applied successfully")
        return True
    except Exception as e:
        print(f"❌ Presentation demo seed failed: {e}")
        raise


def main() -> None:
    _backend = os.path.dirname(os.path.abspath(__file__))
    if _backend not in sys.path:
        sys.path.insert(0, _backend)
    os.environ.setdefault("DATABASE_URL", "")
    from app.core.database import engine

    run_presentation_demo(engine)


if __name__ == "__main__":
    main()
