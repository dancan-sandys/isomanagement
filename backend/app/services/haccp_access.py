from __future__ import annotations

from typing import Dict, Set

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.haccp import CCP


def get_user_haccp_assignments(db: Session, user_id: int) -> Dict[str, Set[int]]:
    """Return product and CCP assignments for a given user."""
    if not user_id:
        return {
            "product_ids": set(),
            "monitoring_ccp_ids": set(),
            "verification_ccp_ids": set(),
        }

    rows = (
        db.query(
            CCP.id,
            CCP.product_id,
            CCP.monitoring_responsible,
            CCP.verification_responsible,
        )
        .filter(
            or_(
                CCP.monitoring_responsible == user_id,
                CCP.verification_responsible == user_id,
            )
        )
        .all()
    )

    product_ids: Set[int] = set()
    monitoring_ccps: Set[int] = set()
    verification_ccps: Set[int] = set()

    for row in rows:
        if row.product_id:
            product_ids.add(row.product_id)
        if row.monitoring_responsible == user_id:
            monitoring_ccps.add(row.id)
        if row.verification_responsible == user_id:
            verification_ccps.add(row.id)

    return {
        "product_ids": product_ids,
        "monitoring_ccp_ids": monitoring_ccps,
        "verification_ccp_ids": verification_ccps,
    }


def has_haccp_assignment(db: Session, user_id: int) -> bool:
    """Return True if the user is assigned to any CCP as monitor or verifier."""
    assignments = get_user_haccp_assignments(db, user_id)
    return (
        bool(assignments["product_ids"])
        or bool(assignments["monitoring_ccp_ids"])
        or bool(assignments["verification_ccp_ids"])
    )


def is_ccp_monitoring_responsible(db: Session, user_id: int, ccp_id: int) -> bool:
    """Check if the user is the monitoring responsible for a CCP."""
    if not user_id or not ccp_id:
        return False
    return (
        db.query(CCP.id)
        .filter(CCP.id == ccp_id, CCP.monitoring_responsible == user_id)
        .first()
        is not None
    )


def is_ccp_verification_responsible(db: Session, user_id: int, ccp_id: int) -> bool:
    """Check if the user is the verification responsible for a CCP."""
    if not user_id or not ccp_id:
        return False
    return (
        db.query(CCP.id)
        .filter(CCP.id == ccp_id, CCP.verification_responsible == user_id)
        .first()
        is not None
    )

