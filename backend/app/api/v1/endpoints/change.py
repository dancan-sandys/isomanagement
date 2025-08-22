from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission_dependency
from app.core.security import get_current_user
from app.services.change_service import ChangeService
from app.schemas.change import ChangeRequestCreate, ChangeApprovalStep, ChangeRequestResponse, ChangeAssessUpdate, ChangeDecisionRequest
from app.models.change import ApprovalDecision, ChangeRequest

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


@router.get("/", response_model=List[ChangeRequestResponse])
def list_changes(
	status: Optional[str] = Query(None),
	process_id: Optional[int] = Query(None),
	db: Session = Depends(get_db),
	current_user = Depends(require_permission_dependency("documents:view"))
):
	q = db.query(ChangeRequest)
	if status:
		from app.models.change import ChangeStatus
		try:
			q = q.filter(ChangeRequest.status == ChangeStatus(status))
		except Exception:
			pass
	if process_id:
		q = q.filter(ChangeRequest.process_id == process_id)
	rows = q.order_by(ChangeRequest.created_at.desc()).all()
	# Eagerly load approvals as dicts
	result = []
	for r in rows:
		item = ChangeRequestResponse.model_validate(r)
		item.approvals = [
			{
				"id": ap.id,
				"approver_id": ap.approver_id,
				"sequence": ap.sequence,
				"decision": ap.decision.value if hasattr(ap.decision, "value") else str(ap.decision),
				"comments": ap.comments,
				"decided_at": ap.decided_at,
			}
			for ap in r.approvals
		]
		result.append(item)
	return result


@router.get("/{change_id}", response_model=ChangeRequestResponse)
def get_change(change_id: int, db: Session = Depends(get_db), current_user = Depends(require_permission_dependency("documents:view"))):
	row = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
	if not row:
		raise HTTPException(status_code=404, detail="Not found")
	item = ChangeRequestResponse.model_validate(row)
	item.approvals = [
		{
			"id": ap.id,
			"approver_id": ap.approver_id,
			"sequence": ap.sequence,
			"decision": ap.decision.value if hasattr(ap.decision, "value") else str(ap.decision),
			"comments": ap.comments,
			"decided_at": ap.decided_at,
		}
		for ap in row.approvals
	]
	return item