from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.production_service import ProductionService
from app.schemas.production import (
    ProcessCreate, ProcessLogCreate, YieldCreate, TransferCreate, AgingCreate
)
from app.models.production import ProductProcessType

router = APIRouter()


@router.get("/analytics")
def get_analytics(process_type: Optional[str] = Query(None), db: Session = Depends(get_db)):
    service = ProductionService(db)
    pt = ProductProcessType(process_type) if process_type else None
    return service.get_analytics(pt)


@router.post("/process")
def create_process(payload: ProcessCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    try:
        pt = ProductProcessType(payload.process_type)
        proc = service.create_process(payload.batch_id, pt, payload.operator_id, payload.spec)
        return proc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/log")
def add_log(process_id: int, payload: ProcessLogCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    try:
        log = service.add_log(process_id, payload.model_dump())
        return log
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/yield")
def record_yield(process_id: int, payload: YieldCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    try:
        yr = service.record_yield(process_id, payload.output_qty, payload.unit, payload.expected_qty)
        return yr
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/transfer")
def record_transfer(process_id: int, payload: TransferCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    try:
        tr = service.record_transfer(process_id, payload.quantity, payload.unit, payload.location, payload.lot_number, payload.verified_by)
        return tr
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{process_id}/aging")
def record_aging(process_id: int, payload: AgingCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    try:
        ar = service.record_aging(process_id, payload.model_dump())
        return ar
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{process_id}")
def get_process(process_id: int, db: Session = Depends(get_db)):
    service = ProductionService(db)
    proc = service.get_process(process_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Process not found")
    return proc

