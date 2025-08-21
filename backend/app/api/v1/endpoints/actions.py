from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.actions_service import ActionsService

router = APIRouter()


@router.get("/actions-log")
def list_actions(
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = ActionsService(db)
    actions = service.list_actions({k: v for k, v in {"source": source, "status": status, "priority": priority}.items() if v})
    return actions


@router.put("/actions-log/{action_id}")
def update_action(action_id: int, payload: dict, db: Session = Depends(get_db)):
    service = ActionsService(db)
    a = service.update_action(action_id, payload)
    if not a:
        raise HTTPException(status_code=404, detail="Action not found")
    return a


@router.post("/interested-parties")
def create_interested_party(payload: dict, db: Session = Depends(get_db)):
    service = ActionsService(db)
    return service.create_interested_party(payload)


@router.post("/issues/swot")
def create_swot_issue(payload: dict, db: Session = Depends(get_db)):
    service = ActionsService(db)
    return service.create_swot_issue(payload)


@router.post("/issues/pestel")
def create_pestel_issue(payload: dict, db: Session = Depends(get_db)):
    service = ActionsService(db)
    return service.create_pestel_issue(payload)

