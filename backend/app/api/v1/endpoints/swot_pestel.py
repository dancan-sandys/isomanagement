from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.actions_log import SWOTAnalysis, SWOTItem, PESTELAnalysis, PESTELItem, SWOTAction, PESTELAction
from app.models.user import User
from sqlalchemy import func, and_
from app.schemas.swot_pestel import (
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new SWOT analysis"""
    service = ActionsLogService(db)
    # Set the created_by field to the current user's ID
    analysis_dict = analysis.dict()
    analysis_dict['created_by'] = current_user.id
    return service.create_swot_analysis(analysis_dict)

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new PESTEL analysis"""
    service = ActionsLogService(db)
    # Set the created_by field to the current user's ID
    analysis_dict = analysis.dict()
    analysis_dict['created_by'] = current_user.id
    return service.create_pestel_analysis(analysis_dict)

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

# ISO-Specific Endpoints
@router.get("/iso/compliance-metrics")
def get_iso_compliance_metrics(db: Session = Depends(get_db)):
    """Get ISO 9001:2015 compliance metrics for SWOT/PESTEL analyses"""
    service = ActionsLogService(db)
    return service.get_iso_compliance_metrics()

@router.get("/iso/dashboard-metrics")
def get_iso_dashboard_metrics(db: Session = Depends(get_db)):
    """Get comprehensive ISO dashboard metrics including compliance, insights, and improvements"""
    service = ActionsLogService(db)
    return service.get_iso_dashboard_metrics()

@router.get("/iso/clause-4-1-assessment")
def get_clause_4_1_assessment(db: Session = Depends(get_db)):
    """Get assessment of compliance with ISO 9001:2015 Clause 4.1 - Understanding the organization and its context"""
    service = ActionsLogService(db)
    
    # Get all analyses with their strategic context information
    swot_analyses = service.get_swot_analyses(limit=1000)
    pestel_analyses = service.get_pestel_analyses(limit=1000)
    
    # Assess compliance with Clause 4.1 requirements
    clause_4_1_assessment = {
        "total_analyses": len(swot_analyses) + len(pestel_analyses),
        "analyses_with_context": sum(1 for a in swot_analyses if a.strategic_context) + 
                                sum(1 for a in pestel_analyses if a.strategic_context),
        "analyses_with_scope_defined": sum(1 for a in swot_analyses if a.scope) + 
                                      sum(1 for a in pestel_analyses if a.scope),
        "analyses_with_review_schedule": sum(1 for a in swot_analyses if a.next_review_date) + 
                                        sum(1 for a in pestel_analyses if a.next_review_date),
        "swot_analyses": {
            "total": len(swot_analyses),
            "with_strategic_context": sum(1 for a in swot_analyses if a.strategic_context),
            "with_iso_references": sum(1 for a in swot_analyses if a.iso_clause_reference),
            "organization_wide_scope": sum(1 for a in swot_analyses if a.scope == "organization_wide")
        },
        "pestel_analyses": {
            "total": len(pestel_analyses),
            "with_strategic_context": sum(1 for a in pestel_analyses if a.strategic_context),
            "with_iso_references": sum(1 for a in pestel_analyses if a.iso_clause_reference),
            "organization_wide_scope": sum(1 for a in pestel_analyses if a.scope == "organization_wide")
        },
        "compliance_recommendations": [
            "Ensure all analyses include strategic context per Clause 4.1",
            "Define clear scope for each analysis",
            "Establish regular review schedules",
            "Document interested parties and their requirements",
            "Link analyses to risk management processes"
        ]
    }
    
    return clause_4_1_assessment

@router.post("/swot-analyses/{analysis_id}/iso-review")
def conduct_iso_review(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Conduct an ISO compliance review of a SWOT analysis"""
    service = ActionsLogService(db)
    analysis = service.get_swot_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="SWOT analysis not found")
    
    # Perform ISO compliance review
    review_results = {
        "analysis_id": analysis_id,
        "review_date": datetime.now(),
        "compliance_score": 0,
        "findings": [],
        "recommendations": []
    }
    
    # Check strategic context
    if not analysis.strategic_context:
        review_results["findings"].append("Missing strategic context (Clause 4.1)")
        review_results["recommendations"].append("Define organizational purpose and strategic direction")
    else:
        review_results["compliance_score"] += 20
    
    # Check scope definition
    if not analysis.scope:
        review_results["findings"].append("Analysis scope not defined")
        review_results["recommendations"].append("Define clear analysis scope")
    else:
        review_results["compliance_score"] += 15
    
    # Check review schedule
    if not analysis.next_review_date:
        review_results["findings"].append("No review schedule established")
        review_results["recommendations"].append("Establish regular review schedule")
    else:
        review_results["compliance_score"] += 15
    
    # Check items with evidence
    items_with_evidence = service.db.query(
        func.count(SWOTItem.id)
    ).filter(
        and_(
            SWOTItem.analysis_id == analysis_id,
            func.json_array_length(SWOTItem.evidence_sources) > 0
        )
    ).scalar() or 0
    
    total_items = service.db.query(
        func.count(SWOTItem.id)
    ).filter(SWOTItem.analysis_id == analysis_id).scalar() or 0
    
    if total_items > 0 and items_with_evidence / total_items >= 0.8:
        review_results["compliance_score"] += 25
    elif items_with_evidence > 0:
        review_results["compliance_score"] += 15
        review_results["recommendations"].append("Increase documentation of evidence sources")
    else:
        review_results["findings"].append("Insufficient evidence documentation")
        review_results["recommendations"].append("Document evidence sources for all items")
    
    # Check action integration
    actions_count = service.db.query(func.count(SWOTAction.id)).filter(
        SWOTAction.analysis_id == analysis_id
    ).scalar() or 0
    
    if actions_count > 0:
        review_results["compliance_score"] += 25
    else:
        review_results["findings"].append("No actions generated from analysis")
        review_results["recommendations"].append("Generate actionable items from analysis")
    
    # Determine compliance level
    if review_results["compliance_score"] >= 80:
        review_results["compliance_level"] = "Fully Compliant"
    elif review_results["compliance_score"] >= 60:
        review_results["compliance_level"] = "Mostly Compliant"
    elif review_results["compliance_score"] >= 40:
        review_results["compliance_level"] = "Partially Compliant"
    else:
        review_results["compliance_level"] = "Non-Compliant"
    
    return review_results

@router.post("/pestel-analyses/{analysis_id}/iso-review")
def conduct_pestel_iso_review(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Conduct an ISO compliance review of a PESTEL analysis"""
    service = ActionsLogService(db)
    analysis = service.get_pestel_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="PESTEL analysis not found")
    
    # Similar review logic as SWOT but focused on external factors
    review_results = {
        "analysis_id": analysis_id,
        "review_date": datetime.now(),
        "compliance_score": 0,
        "findings": [],
        "recommendations": []
    }
    
    # Check for external environment focus
    if analysis.strategic_context:
        review_results["compliance_score"] += 25
    else:
        review_results["findings"].append("Missing strategic context for external environment")
        review_results["recommendations"].append("Define external environment context")
    
    # Check for regulatory landscape assessment
    if analysis.regulatory_landscape:
        review_results["compliance_score"] += 20
    else:
        review_results["findings"].append("Missing regulatory landscape assessment")
        review_results["recommendations"].append("Assess regulatory environment impact")
    
    # Check stakeholder impact assessment
    if analysis.stakeholder_impact:
        review_results["compliance_score"] += 20
    else:
        review_results["findings"].append("Missing stakeholder impact assessment")
        review_results["recommendations"].append("Assess impact on interested parties")
    
    # Check for monitoring processes
    items_with_monitoring = service.db.query(
        func.count(PESTELItem.id)
    ).filter(
        and_(
            PESTELItem.analysis_id == analysis_id,
            func.json_array_length(PESTELItem.monitoring_indicators) > 0
        )
    ).scalar() or 0
    
    total_items = service.db.query(
        func.count(PESTELItem.id)
    ).filter(PESTELItem.analysis_id == analysis_id).scalar() or 0
    
    if total_items > 0 and items_with_monitoring / total_items >= 0.7:
        review_results["compliance_score"] += 35
    else:
        review_results["findings"].append("Insufficient monitoring indicators defined")
        review_results["recommendations"].append("Define monitoring indicators for external factors")
    
    # Determine compliance level
    if review_results["compliance_score"] >= 80:
        review_results["compliance_level"] = "Fully Compliant"
    elif review_results["compliance_score"] >= 60:
        review_results["compliance_level"] = "Mostly Compliant"
    elif review_results["compliance_score"] >= 40:
        review_results["compliance_level"] = "Partially Compliant"
    else:
        review_results["compliance_level"] = "Non-Compliant"
    
    return review_results
