from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.actions_log import SWOTAnalysis, SWOTItem, PESTELAnalysis, PESTELItem
from app.schemas.actions_log import (
    SWOTAnalysisCreate, SWOTAnalysisUpdate, SWOTAnalysisResponse,
    SWOTItemCreate, SWOTItemUpdate, SWOTItemResponse,
    PESTELAnalysisCreate, PESTELAnalysisUpdate, PESTELAnalysisResponse,
    PESTELItemCreate, PESTELItemUpdate, PESTELItemResponse
)
from app.services.actions_log_service import ActionsLogService

router = APIRouter()

# SWOT Analysis Endpoints
@router.post("/swot-analyses/", response_model=SWOTAnalysisResponse)
def create_swot_analysis(
    analysis: SWOTAnalysisCreate,
    db: Session = Depends(get_db)
):
    """Create a new SWOT analysis"""
    service = ActionsLogService(db)
    return service.create_swot_analysis(analysis)

@router.get("/swot-analyses/", response_model=List[SWOTAnalysisResponse])
def list_swot_analyses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List SWOT analyses with optional filtering"""
    service = ActionsLogService(db)
    return service.get_swot_analyses(skip=skip, limit=limit, is_active=is_active)

@router.get("/swot-analyses/{analysis_id}", response_model=SWOTAnalysisResponse)
def get_swot_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific SWOT analysis by ID"""
    service = ActionsLogService(db)
    analysis = service.get_swot_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="SWOT analysis not found")
    return analysis

@router.put("/swot-analyses/{analysis_id}", response_model=SWOTAnalysisResponse)
def update_swot_analysis(
    analysis_id: int,
    analysis: SWOTAnalysisUpdate,
    db: Session = Depends(get_db)
):
    """Update a SWOT analysis"""
    service = ActionsLogService(db)
    updated_analysis = service.update_swot_analysis(analysis_id, analysis)
    if not updated_analysis:
        raise HTTPException(status_code=404, detail="SWOT analysis not found")
    return updated_analysis

@router.delete("/swot-analyses/{analysis_id}")
def delete_swot_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Delete a SWOT analysis"""
    service = ActionsLogService(db)
    success = service.delete_swot_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="SWOT analysis not found")
    return {"message": "SWOT analysis deleted successfully"}

# SWOT Items Endpoints
@router.post("/swot-analyses/{analysis_id}/items/", response_model=SWOTItemResponse)
def create_swot_item(
    analysis_id: int,
    item: SWOTItemCreate,
    db: Session = Depends(get_db)
):
    """Add an item to a SWOT analysis"""
    service = ActionsLogService(db)
    return service.create_swot_item(analysis_id, item)

@router.get("/swot-analyses/{analysis_id}/items/", response_model=List[SWOTItemResponse])
def list_swot_items(
    analysis_id: int,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List items in a SWOT analysis"""
    service = ActionsLogService(db)
    return service.get_swot_items(analysis_id, category=category)

@router.put("/swot-items/{item_id}", response_model=SWOTItemResponse)
def update_swot_item(
    item_id: int,
    item: SWOTItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a SWOT item"""
    service = ActionsLogService(db)
    updated_item = service.update_swot_item(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="SWOT item not found")
    return updated_item

@router.delete("/swot-items/{item_id}")
def delete_swot_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Delete a SWOT item"""
    service = ActionsLogService(db)
    success = service.delete_swot_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="SWOT item not found")
    return {"message": "SWOT item deleted successfully"}

# PESTEL Analysis Endpoints
@router.post("/pestel-analyses/", response_model=PESTELAnalysisResponse)
def create_pestel_analysis(
    analysis: PESTELAnalysisCreate,
    db: Session = Depends(get_db)
):
    """Create a new PESTEL analysis"""
    service = ActionsLogService(db)
    return service.create_pestel_analysis(analysis)

@router.get("/pestel-analyses/", response_model=List[PESTELAnalysisResponse])
def list_pestel_analyses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List PESTEL analyses with optional filtering"""
    service = ActionsLogService(db)
    return service.get_pestel_analyses(skip=skip, limit=limit, is_active=is_active)

@router.get("/pestel-analyses/{analysis_id}", response_model=PESTELAnalysisResponse)
def get_pestel_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific PESTEL analysis by ID"""
    service = ActionsLogService(db)
    analysis = service.get_pestel_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="PESTEL analysis not found")
    return analysis

@router.put("/pestel-analyses/{analysis_id}", response_model=PESTELAnalysisResponse)
def update_pestel_analysis(
    analysis_id: int,
    analysis: PESTELAnalysisUpdate,
    db: Session = Depends(get_db)
):
    """Update a PESTEL analysis"""
    service = ActionsLogService(db)
    updated_analysis = service.update_pestel_analysis(analysis_id, analysis)
    if not updated_analysis:
        raise HTTPException(status_code=404, detail="PESTEL analysis not found")
    return updated_analysis

@router.delete("/pestel-analyses/{analysis_id}")
def delete_pestel_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Delete a PESTEL analysis"""
    service = ActionsLogService(db)
    success = service.delete_pestel_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="PESTEL analysis not found")
    return {"message": "PESTEL analysis deleted successfully"}

# PESTEL Items Endpoints
@router.post("/pestel-analyses/{analysis_id}/items/", response_model=PESTELItemResponse)
def create_pestel_item(
    analysis_id: int,
    item: PESTELItemCreate,
    db: Session = Depends(get_db)
):
    """Add an item to a PESTEL analysis"""
    service = ActionsLogService(db)
    return service.create_pestel_item(analysis_id, item)

@router.get("/pestel-analyses/{analysis_id}/items/", response_model=List[PESTELItemResponse])
def list_pestel_items(
    analysis_id: int,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List items in a PESTEL analysis"""
    service = ActionsLogService(db)
    return service.get_pestel_items(analysis_id, category=category)

@router.put("/pestel-items/{item_id}", response_model=PESTELItemResponse)
def update_pestel_item(
    item_id: int,
    item: PESTELItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a PESTEL item"""
    service = ActionsLogService(db)
    updated_item = service.update_pestel_item(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="PESTEL item not found")
    return updated_item

@router.delete("/pestel-items/{item_id}")
def delete_pestel_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Delete a PESTEL item"""
    service = ActionsLogService(db)
    success = service.delete_pestel_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="PESTEL item not found")
    return {"message": "PESTEL item deleted successfully"}

# Analytics Endpoints
@router.get("/analytics/swot-summary")
def get_swot_analytics(db: Session = Depends(get_db)):
    """Get SWOT analysis summary and statistics"""
    service = ActionsLogService(db)
    return service.get_swot_analytics()

@router.get("/analytics/pestel-summary")
def get_pestel_analytics(db: Session = Depends(get_db)):
    """Get PESTEL analysis summary and statistics"""
    service = ActionsLogService(db)
    return service.get_pestel_analytics()
