#!/usr/bin/env python3
"""
Schema alignment helper to reconcile models with existing SQLite tables.
Adds missing columns used by endpoints for HACCP, PRP, Risk, NC/CAPA, Equipment, and logs.
"""

import sqlite3
from typing import Iterable


DB_PATH = "iso22000_fsms.db"


def get_existing_columns(cur: sqlite3.Cursor, table: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def add_column(cur: sqlite3.Cursor, table: str, column: str, ddl: str) -> None:
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
    print(f"✅ {table}.{column} added")


def ensure_columns(cur: sqlite3.Cursor, table: str, definitions: dict[str, str]) -> None:
    existing = get_existing_columns(cur, table)
    for col, ddl in definitions.items():
        if col not in existing:
            add_column(cur, table, col, ddl)


def table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def ensure_products(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "products"):
        return
    ensure_columns(
        cur,
        "products",
        {
            "risk_assessment_required": "BOOLEAN DEFAULT 1",
            "risk_assessment_frequency": "VARCHAR(100)",
            "risk_review_frequency": "VARCHAR(100)",
            "last_risk_assessment_date": "DATETIME",
            "next_risk_assessment_date": "DATETIME",
        },
    )


def ensure_ccp_monitoring_logs(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "ccp_monitoring_logs"):
        return
    ensure_columns(
        cur,
        "ccp_monitoring_logs",
        {
            "log_metadata": "TEXT",
            "action_log_id": "INTEGER",
        },
    )


def ensure_prp_programs(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "prp_programs"):
        return
    ensure_columns(
        cur,
        "prp_programs",
        {
            "risk_assessment_required": "BOOLEAN DEFAULT 1",
            "risk_assessment_date": "DATETIME",
            "risk_assessment_review_date": "DATETIME",
            "risk_level": "VARCHAR(50)",
            "risk_register_item_id": "INTEGER",
            "risk_assessment_frequency": "VARCHAR(100)",
            "risk_monitoring_plan": "TEXT",
            "risk_review_plan": "TEXT",
            "risk_improvement_plan": "TEXT",
            "risk_control_effectiveness": "INTEGER",
            "risk_residual_score": "INTEGER",
            "risk_residual_level": "VARCHAR(50)",
            # Ensure documentation fields present for dashboard queries
            "records_required": "TEXT",
            "training_requirements": "TEXT",
            "monitoring_frequency": "VARCHAR(100)",
            "verification_frequency": "VARCHAR(100)",
            "acceptance_criteria": "TEXT",
            "trend_analysis_required": "BOOLEAN",
            "corrective_action_procedure": "TEXT",
            "escalation_procedure": "TEXT",
            "preventive_action_procedure": "TEXT",
            "last_review_date": "DATETIME",
            "next_review_date": "DATETIME",
            "reviewed_by": "INTEGER",
            "approved_by": "INTEGER",
            "approved_at": "DATETIME",
        },
    )


def ensure_risk_register(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "risk_register"):
        return
    ensure_columns(
        cur,
        "risk_register",
        {
            "risk_context_id": "INTEGER",
            "risk_criteria_id": "INTEGER",
            "risk_assessment_method": "VARCHAR(100)",
            "risk_assessment_date": "DATETIME",
            "risk_assessor_id": "INTEGER",
            "risk_assessment_reviewed": "BOOLEAN",
            "risk_assessment_reviewer_id": "INTEGER",
            "risk_assessment_review_date": "DATETIME",
            "risk_treatment_strategy": "VARCHAR(100)",
            "risk_treatment_plan": "TEXT",
            "risk_treatment_cost": "FLOAT",
            "risk_treatment_benefit": "FLOAT",
            "risk_treatment_timeline": "VARCHAR(100)",
            "risk_treatment_approved": "BOOLEAN",
            "risk_treatment_approver_id": "INTEGER",
            "risk_treatment_approval_date": "DATETIME",
            "residual_risk_score": "INTEGER",
            "residual_risk_level": "VARCHAR(50)",
            "residual_risk_acceptable": "BOOLEAN",
            "residual_risk_justification": "TEXT",
            "monitoring_frequency": "VARCHAR(100)",
            "next_monitoring_date": "DATETIME",
            "monitoring_method": "VARCHAR(100)",
            "monitoring_responsible": "INTEGER",
            "review_frequency": "VARCHAR(100)",
            "review_responsible": "INTEGER",
            "last_review_date": "DATETIME",
            "review_outcome": "TEXT",
            "strategic_impact": "TEXT",
            "business_unit": "VARCHAR(100)",
            "project_association": "VARCHAR(100)",
            "stakeholder_impact": "TEXT",
            "market_impact": "TEXT",
            "competitive_impact": "TEXT",
            "regulatory_impact": "TEXT",
            "financial_impact": "TEXT",
            "operational_impact": "TEXT",
            "reputational_impact": "TEXT",
            "risk_velocity": "VARCHAR(50)",
            "risk_persistence": "VARCHAR(50)",
            "risk_contagion": "BOOLEAN",
            "risk_cascade": "BOOLEAN",
            "risk_amplification": "BOOLEAN",
        },
    )


def ensure_ccps(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "ccps"):
        return
    ensure_columns(
        cur,
        "ccps",
        {
            "risk_register_item_id": "INTEGER",
            "risk_assessment_method": "VARCHAR(100)",
            "risk_assessment_date": "DATETIME",
            "risk_assessor_id": "INTEGER",
            "risk_treatment_plan": "TEXT",
            "risk_monitoring_frequency": "VARCHAR(100)",
            "risk_review_frequency": "VARCHAR(100)",
            "risk_control_effectiveness": "INTEGER",
            "risk_residual_score": "INTEGER",
            "risk_residual_level": "VARCHAR(50)",
        },
    )


def ensure_non_conformances(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "non_conformances"):
        return
    ensure_columns(
        cur,
        "non_conformances",
        {
            "requires_immediate_action": "BOOLEAN",
            "risk_level": "VARCHAR(20)",
            "escalation_status": "VARCHAR(20)",
        },
    )


def ensure_equipment(cur: sqlite3.Cursor) -> None:
    if not table_exists(cur, "equipment"):
        return
    ensure_columns(
        cur,
        "equipment",
        {
            "is_active": "BOOLEAN DEFAULT 1",
            "critical_to_food_safety": "BOOLEAN",
        },
    )


def ensure_prp_capa_enums(cur: sqlite3.Cursor) -> None:
    # Ensure CorrectiveActionStatus text values exist via no-op; schema uses TEXT but service expects COMPLETED
    # No ALTER needed; but if legacy rows use lowercase, we won't modify rows here.
    pass


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print("🔧 Aligning database schema with models (SQLite)…")
    try:
        ensure_products(cur)
        ensure_ccp_monitoring_logs(cur)
        ensure_prp_programs(cur)
        ensure_ccps(cur)
        ensure_risk_register(cur)
        ensure_non_conformances(cur)
        ensure_equipment(cur)
        # Equipment analytics columns that services expect
        # maintenance_plans.prp_document_id
        if table_exists(cur, "maintenance_plans"):
            ensure_columns(cur, "maintenance_plans", {"prp_document_id": "INTEGER"})
        # calibration_plans.frequency_days
        if table_exists(cur, "calibration_plans"):
            ensure_columns(cur, "calibration_plans", {"frequency_days": "INTEGER DEFAULT 365"})
        # HACCP missing columns referenced in GETs
        # process_flows.risk_assessment_required, risk_assessment_frequency, risk_review_frequency, last_risk_assessment_date, next_risk_assessment_date
        if table_exists(cur, "process_flows"):
            ensure_columns(cur, "process_flows", {
                "risk_assessment_required": "BOOLEAN DEFAULT 1",
                "risk_assessment_frequency": "VARCHAR(100)",
                "risk_review_frequency": "VARCHAR(100)",
                "last_risk_assessment_date": "DATETIME",
                "next_risk_assessment_date": "DATETIME",
            })
        # hazards.reference_documents
        if table_exists(cur, "hazards"):
            ensure_columns(cur, "hazards", {
                "reference_documents": "TEXT",
            })
        conn.commit()
        print("🎉 Schema alignment complete")
    except Exception as exc:
        conn.rollback()
        print(f"❌ Schema alignment failed: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()


