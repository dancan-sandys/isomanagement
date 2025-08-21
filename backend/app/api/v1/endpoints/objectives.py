from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.services.objectives_service import ObjectivesService
from app.schemas.objectives import (
    ObjectiveCreate, ObjectiveUpdate, Objective,
    ObjectiveTargetCreate, ObjectiveTargetUpdate, ObjectiveTarget,
    ObjectiveProgressCreate, ObjectiveProgressUpdate, ObjectiveProgress
)

router = APIRouter()


@router.post("/", response_model=Objective)
def create_objective(payload: ObjectiveCreate, db: Session = Depends(get_db)):
    service = ObjectivesService(db)
    return service.create_objective(payload.model_dump())


@router.get("/", response_model=List[Objective])
def list_objectives(db: Session = Depends(get_db)):
    service = ObjectivesService(db)
    return service.list_objectives()


@router.get("/{objective_id}", response_model=Objective)
def get_objective(objective_id: int, db: Session = Depends(get_db)):
    service = ObjectivesService(db)
    obj = service.get_objective(objective_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Objective not found")
    return obj


@router.put("/{objective_id}", response_model=Objective)
def update_objective(objective_id: int, payload: ObjectiveUpdate, db: Session = Depends(get_db)):
    service = ObjectivesService(db)
    obj = service.update_objective(objective_id, {k: v for k, v in payload.model_dump().items() if v is not None})
    if not obj:
        raise HTTPException(status_code=404, detail="Objective not found")
    return obj


@router.post("/{objective_id}/targets", response_model=ObjectiveTarget)
def upsert_target(objective_id: int, payload: ObjectiveTargetCreate, db: Session = Depends(get_db)):
    if payload.objective_id != objective_id:
        raise HTTPException(status_code=400, detail="Objective ID mismatch")
    service = ObjectivesService(db)
    return service.upsert_target(payload.model_dump())


@router.get("/{objective_id}/targets", response_model=List[ObjectiveTarget])
def list_targets(objective_id: int, db: Session = Depends(get_db)):
    service = ObjectivesService(db)
    return service.list_targets(objective_id)


@router.post("/{objective_id}/progress", response_model=ObjectiveProgress)
def upsert_progress(objective_id: int, payload: ObjectiveProgressCreate, db: Session = Depends(get_db)):
    if payload.objective_id != objective_id:
        raise HTTPException(status_code=400, detail="Objective ID mismatch")
    service = ObjectivesService(db)
    return service.upsert_progress(payload.model_dump())


@router.get("/{objective_id}/progress", response_model=List[ObjectiveProgress])
def list_progress(objective_id: int, db: Session = Depends(get_db)):
    service = ObjectivesService(db)
    return service.list_progress(objective_id)


@router.get("/kpis", response_model=List[ObjectiveProgress])
def get_kpis(
    objective_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    service = ObjectivesService(db)
    # Reuse ObjectiveProgress schema for lean KPI payload
    results = service.get_kpis(objective_id, department_id, period_start, period_end)
    # Map to schema objects
    mapped: List[ObjectiveProgress] = []
    for r in results:
        mapped.append(ObjectiveProgress(
            id=0,
            objective_id=r["objective_id"],
            department_id=r.get("department_id"),
            period_start=r["period_start"],
            period_end=r["period_end"],
            actual_value=r.get("actual_value"),
            attainment_percent=r.get("attainment_percent"),
            status=r.get("status"),
            created_by=0
        ))
    return mapped

