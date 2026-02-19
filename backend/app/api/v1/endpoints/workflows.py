from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission_dependency
from app.models.user import User
from app.services.workflow_engine import WorkflowEngine


router = APIRouter()


@router.get("/workflows/{product_type}")
def get_workflow(product_type: str, db: Session = Depends(get_db), current_user: User = Depends(require_permission_dependency("traceability:view"))) -> Dict[str, Any]:
    try:
        engine = WorkflowEngine(db)
        return engine.load_workflow(product_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows/instantiate/{product_type}")
def instantiate_workflow(product_type: str, payload: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(require_permission_dependency("production:create"))) -> Dict[str, Any]:
    try:
        engine = WorkflowEngine(db)
        batch_id = int(payload.get("batch_id"))
        operator_id = payload.get("operator_id")
        fields = payload.get("fields") or {}
        return engine.instantiate_process_from_workflow(batch_id, product_type, operator_id, fields)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows/validate")
def validate_workflow(payload: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(require_permission_dependency("production:read"))) -> Dict[str, Any]:
    try:
        process_id = int(payload.get("process_id"))
        engine = WorkflowEngine(db)
        return engine.validate_against_workflow(process_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

