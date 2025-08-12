from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session

from app.services import log_audit_event


def audit_event(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
):
    """Convenience wrapper to log an audit event with request context."""
    ip = None
    ua = None
    try:
        if request is not None:
            ip = request.client.host if request.client else None
            ua = request.headers.get("user-agent")
    except Exception:
        pass
    try:
        log_audit_event(
            db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip,
            user_agent=ua,
        )
    except Exception:
        # Audit failures should never block business flow
        pass



