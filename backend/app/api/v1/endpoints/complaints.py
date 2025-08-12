from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.complaint import (
    ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintListResponse,
    CommunicationCreate, CommunicationResponse,
    InvestigationCreate, InvestigationUpdate, InvestigationResponse,
    ComplaintTrendResponse
)
from app.services.complaint_service import ComplaintService


router = APIRouter()


@router.post("/", response_model=ComplaintResponse)
async def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    comp = svc.create_complaint(payload, current_user.id)
    return comp


@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    result = svc.list_complaints(page=page, size=size)
    # Map ORM to Pydantic
    items = [ComplaintResponse.model_validate(i) for i in result["items"]]
    return ComplaintListResponse(items=items, total=result["total"], page=result["page"], size=result["size"], pages=result["pages"])


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    comp = svc.get_complaint(complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(complaint_id: int, payload: ComplaintUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    comp = svc.update_complaint(complaint_id, payload)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


# Communications
@router.post("/{complaint_id}/communications", response_model=CommunicationResponse)
async def add_communication(complaint_id: int, payload: CommunicationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    com = svc.add_communication(complaint_id, payload, current_user.id)
    if not com:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return com


# Investigation
@router.post("/{complaint_id}/investigation", response_model=InvestigationResponse)
async def create_investigation(complaint_id: int, payload: InvestigationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    inv = svc.create_or_get_investigation(complaint_id, payload)
    if not inv:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return inv


@router.put("/{complaint_id}/investigation", response_model=InvestigationResponse)
async def update_investigation(complaint_id: int, payload: InvestigationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    inv = svc.update_investigation(complaint_id, payload)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv


# Trends/Reports
@router.get("/reports/trends", response_model=ComplaintTrendResponse)
async def complaint_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    data = svc.get_trends()
    return ComplaintTrendResponse(**data)


# Reads: communications and investigation
@router.get("/{complaint_id}/communications", response_model=list[CommunicationResponse])
async def list_communications(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    return svc.list_communications(complaint_id)


@router.get("/{complaint_id}/investigation", response_model=InvestigationResponse)
async def get_investigation(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    svc = ComplaintService(db)
    inv = svc.get_investigation(complaint_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv


