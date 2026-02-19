from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.schemas.risk import (
    RiskItemCreate, RiskItemUpdate, RiskItemResponse, RiskFilter, RiskStats,
    RiskActionCreate, RiskActionResponse, RiskActionUpdate,
)
from app.services.risk_service import RiskService
from app.models.risk import RiskRegisterItem
from app.utils.audit import audit_event

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_risk_item(
    payload: RiskItemCreate,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        item = service.create_item(payload, 1)  # Use user ID 1 as default
        try:
            audit_event(db, 1, "risk_created", "risk", str(item.id), {"risk_number": item.risk_number})
        except Exception:
            pass
        return ResponseModel(success=True, message="Risk item created", data=RiskItemResponse.model_validate(item))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create risk item: {str(e)}")


@router.get("/", response_model=ResponseModel)
async def list_risk_items(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    item_type: Optional[str] = None,
    category: Optional[str] = None,
    status_f: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    likelihood: Optional[str] = None,
    classification: Optional[str] = None,
    detectability: Optional[str] = None,
    assigned_to: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    try:
        def nz(v: Optional[str]) -> Optional[str]:
            return None if v in ("", None) else v
        # Build filter model (enum values are validated inside schema)
        filters = RiskFilter(
            search=nz(search),
            item_type=nz(item_type),  # pydantic will coerce
            category=nz(category),
            status=nz(status_f),
            severity=nz(severity),
            likelihood=nz(likelihood),
            classification=nz(classification),
            detectability=nz(detectability),
            assigned_to=assigned_to,
            date_from=date_from,
            date_to=date_to,
        )
        service = RiskService(db)
        items, total = service.get_items(filters, page, size)
        return ResponseModel(
            success=True,
            message="Risk items retrieved",
            data={
                "items": [RiskItemResponse.model_validate(i) for i in items],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk items: {str(e)}")


@router.get("/{item_id}", response_model=ResponseModel)
async def get_risk_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.query(RiskRegisterItem).filter(RiskRegisterItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    return ResponseModel(success=True, message="Risk item retrieved", data=RiskItemResponse.model_validate(item))


@router.put("/{item_id}", response_model=ResponseModel)
async def update_risk_item(
    item_id: int,
    payload: RiskItemUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        item = service.update_item(item_id, payload)
        try:
            audit_event(db, 1, "risk_updated", "risk", str(item_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Risk item updated", data=RiskItemResponse.model_validate(item))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update risk item: {str(e)}")


@router.delete("/{item_id}", response_model=ResponseModel)
async def delete_risk_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    try:
        from app.models.risk import RiskRegisterItem

        item = db.query(RiskRegisterItem).filter(RiskRegisterItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Risk item not found")
        db.delete(item)
        db.commit()
        try:
            audit_event(db, 1, "risk_deleted", "risk", str(item_id))
        except Exception:
            pass
        return ResponseModel(success=True, message="Risk item deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete risk item: {str(e)}")


@router.get("/stats/overview", response_model=ResponseModel)
async def get_risk_stats(
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        stats = service.get_stats()
        return ResponseModel(success=True, message="Risk stats retrieved", data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk stats: {str(e)}")


@router.get("/{item_id}/progress", response_model=ResponseModel)
async def get_risk_progress(
    item_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        data = service.get_progress(item_id)
        return ResponseModel(success=True, message="Risk progress retrieved", data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress: {str(e)}")


@router.post("/{item_id}/actions", response_model=ResponseModel)
async def add_risk_action(
    item_id: int,
    payload: RiskActionCreate,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        action = service.add_action(
            item_id=item_id,
            title=payload.title,
            description=payload.description,
            assigned_to=payload.assigned_to,
            due_date=payload.due_date,
        )
        return ResponseModel(success=True, message="Action added", data=RiskActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add action: {str(e)}")


@router.post("/actions/{action_id}/complete", response_model=ResponseModel)
async def complete_risk_action(
    action_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        action = service.complete_action(action_id)
        return ResponseModel(success=True, message="Action completed", data=RiskActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete action: {str(e)}")


@router.get("/{item_id}/actions", response_model=ResponseModel)
async def list_risk_actions(
    item_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        actions = service.list_actions(item_id)
        return ResponseModel(success=True, message="Actions retrieved", data=[RiskActionResponse.model_validate(a) for a in actions])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve actions: {str(e)}")


@router.put("/actions/{action_id}", response_model=ResponseModel)
async def update_risk_action(
    action_id: int,
    payload: RiskActionUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        action = service.update_action(action_id, payload.model_dump(exclude_unset=True))
        return ResponseModel(success=True, message="Action updated", data=RiskActionResponse.model_validate(action))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update action: {str(e)}")


@router.delete("/actions/{action_id}", response_model=ResponseModel)
async def delete_risk_action(
    action_id: int,
    db: Session = Depends(get_db),
):
    try:
        service = RiskService(db)
        ok = service.delete_action(action_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Action not found")
        return ResponseModel(success=True, message="Action deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete action: {str(e)}")


