from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission_dependency
from app.core.security import get_current_user
from app.services.change_service import ChangeService
from app.schemas.change import ChangeRequestCreate, ChangeApprovalStep, ChangeRequestResponse, ChangeAssessUpdate, ChangeDecisionRequest
from app.models.change import ApprovalDecision

router = APIRouter()


@router.post("/", response_model=ChangeRequestResponse)
def create_change_request(
	payload: ChangeRequestCreate,
	approvals: Optional[List[ChangeApprovalStep]] = None,
	db: Session = Depends(get_db),
	current_user = Depends(require_permission_dependency("documents:update"))
):
	service = ChangeService(db)
	try:
		data = payload.model_dump()
		ap = [a.model_dump() for a in (approvals or [])]
		cr = service.create_change(getattr(current_user, "id", None), data, ap)
		return cr
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.put("/{change_id}/assess", response_model=ChangeRequestResponse)
def assess_change(
	change_id: int,	payload: ChangeAssessUpdate,
	db: Session = Depends(get_db),
	current_user = Depends(require_permission_dependency("documents:update"))
):
	service = ChangeService(db)
	try:
		cr = service.update_assessment(change_id, payload.model_dump(exclude_unset=True))
		return cr
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{change_id}/approve", response_model=ChangeRequestResponse)
def approve_change(
	change_id: int,
	payload: ChangeDecisionRequest,
	sequence: Optional[int] = Query(None),
	db: Session = Depends(get_db),
	current_user = Depends(require_permission_dependency("documents:approve"))
):
	service = ChangeService(db)
	try:
		decision = ApprovalDecision(payload.decision)
		cr = service.approve_step(change_id, getattr(current_user, "id", None), sequence, decision, payload.comments)
		return cr
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{change_id}/implement", response_model=ChangeRequestResponse)
def implement_change(
	change_id: int,
	db: Session = Depends(get_db),
	current_user = Depends(require_permission_dependency("documents:update"))
):
	service = ChangeService(db)
	try:
		cr = service.implement(change_id)
		return cr
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{change_id}/verify-close", response_model=ChangeRequestResponse)
def verify_and_close_change(
	change_id: int,
	db: Session = Depends(get_db),
	current_user = Depends(require_permission_dependency("documents:update"))
):
	service = ChangeService(db)
	try:
		cr = service.verify_and_close(change_id)
		return cr
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))