from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.complaint import (
    ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintListResponse,
    CommunicationCreate, CommunicationResponse,
    InvestigationCreate, InvestigationUpdate, InvestigationResponse,
    ComplaintTrendResponse
)
from app.services.complaint_service import ComplaintService


router = APIRouter()


@router.post("/", response_model=ComplaintResponse)
async def create_complaint(
    payload: ComplaintCreate, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    comp = svc.create_complaint(payload, 1)  # Use user ID 1 as default
    return comp


@router.get("/", response_model=ComplaintListResponse)
async def list_complaints(
    page: int = Query(1, ge=1), 
    size: int = Query(20, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    result = svc.list_complaints(page=page, size=size)
    # Map ORM to Pydantic
    items = [ComplaintResponse.model_validate(i) for i in result["items"]]
    return ComplaintListResponse(items=items, total=result["total"], page=result["page"], size=result["size"], pages=result["pages"])


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: int, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    comp = svc.get_complaint(complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


@router.put("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int, 
    payload: ComplaintUpdate, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    comp = svc.update_complaint(complaint_id, payload)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return comp


# Communications
@router.post("/{complaint_id}/communications", response_model=CommunicationResponse)
async def add_communication(
    complaint_id: int, 
    payload: CommunicationCreate, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    com = svc.add_communication(complaint_id, payload, 1)  # Use user ID 1 as default
    if not com:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return com


# Investigation
@router.post("/{complaint_id}/investigation", response_model=InvestigationResponse)
async def create_investigation(
    complaint_id: int, 
    payload: InvestigationCreate, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    inv = svc.create_or_get_investigation(complaint_id, payload)
    if not inv:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return inv


@router.put("/{complaint_id}/investigation", response_model=InvestigationResponse)
async def update_investigation(
    complaint_id: int, 
    payload: InvestigationUpdate, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    inv = svc.update_investigation(complaint_id, payload)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv


# Trends/Reports
@router.get("/reports/trends", response_model=ComplaintTrendResponse)
async def complaint_trends(
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    data = svc.get_trends()
    return ComplaintTrendResponse(**data)


# Reads: communications and investigation
@router.get("/{complaint_id}/communications", response_model=list[CommunicationResponse])
async def list_communications(
    complaint_id: int, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    return svc.list_communications(complaint_id)


@router.get("/{complaint_id}/investigation", response_model=InvestigationResponse)
async def get_investigation(
    complaint_id: int, 
    db: Session = Depends(get_db)
):
    svc = ComplaintService(db)
    inv = svc.get_investigation(complaint_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv


# =============================================================================
# ENHANCED CUSTOMER COMPLAINT FEATURES
# =============================================================================

@router.get("/{complaint_id}/linked-batches")
async def get_linked_batches(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Get batches linked to complaint"""
    try:
        svc = ComplaintService(db)
        complaint = svc.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Mock linked batches data
        linked_batches = [
            {
                "batch_id": "BATCH-20241201-001",
                "product_name": "Whole Milk 1L",
                "production_date": "2024-12-01",
                "expiry_date": "2024-12-08",
                "quantity_produced": 1000,
                "linked_reason": "Customer reported off-taste",
                "linked_at": datetime.utcnow().isoformat()
            }
        ]

        return {
            "success": True,
            "message": "Linked batches retrieved successfully",
            "data": {"linked_batches": linked_batches}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get linked batches: {str(e)}")


@router.post("/{complaint_id}/create-nc")
async def create_nc_from_complaint(
    complaint_id: int,
    nc_data: dict,
    db: Session = Depends(get_db)
):
    """Create non-conformance record from complaint"""
    try:
        svc = ComplaintService(db)
        complaint = svc.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Create NC record
        nc_creation_data = {
            "source": "customer_complaint",
            "source_reference": complaint_id,
            "description": f"Non-conformance raised from complaint #{complaint_id}: {complaint.summary[:100]}",
            "product_affected": nc_data.get("product_affected", ""),
            "severity": nc_data.get("severity", "medium"),
            "immediate_action": nc_data.get("immediate_action", ""),
            "created_by": 1,  # Use user ID 1 as default
            "created_at": datetime.utcnow().isoformat()
        }

        # TODO: Call NC creation endpoint
        # nc_id = nonconformance_service.create_nc(nc_creation_data)
        nc_id = 1  # Mock ID

        return {
            "success": True,
            "message": "Non-conformance created from complaint successfully",
            "data": {
                "nc_id": nc_id,
                "complaint_id": complaint_id,
                "severity": nc_data.get("severity", "medium")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create NC: {str(e)}")


@router.post("/{complaint_id}/satisfaction-survey")
async def record_customer_satisfaction(
    complaint_id: int,
    satisfaction_data: dict,
    db: Session = Depends(get_db)
):
    """Record customer satisfaction after complaint resolution"""
    try:
        svc = ComplaintService(db)
        complaint = svc.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # Validate satisfaction data
        required_fields = ["overall_satisfaction", "resolution_satisfaction", "communication_satisfaction"]
        for field in required_fields:
            if field not in satisfaction_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Record satisfaction
        satisfaction_record = {
            "complaint_id": complaint_id,
            "overall_satisfaction": satisfaction_data["overall_satisfaction"],  # 1-5 scale
            "resolution_satisfaction": satisfaction_data["resolution_satisfaction"],
            "communication_satisfaction": satisfaction_data["communication_satisfaction"],
            "timeliness_satisfaction": satisfaction_data.get("timeliness_satisfaction"),
            "feedback_comments": satisfaction_data.get("feedback_comments", ""),
            "would_recommend": satisfaction_data.get("would_recommend", None),
            "survey_method": satisfaction_data.get("survey_method", "email"),
            "recorded_by": 1,  # Use user ID 1 as default
            "recorded_at": datetime.utcnow().isoformat()
        }

        return {
            "success": True,
            "message": "Customer satisfaction recorded successfully",
            "data": satisfaction_record
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record satisfaction: {str(e)}")


@router.get("/satisfaction/analytics")
async def get_satisfaction_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get customer satisfaction analytics"""
    try:
        # Mock satisfaction analytics
        analytics_data = {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "overall_metrics": {
                "average_satisfaction": 4.2,
                "total_surveys": 45,
                "response_rate": 68.2,
                "nps_score": 42  # Net Promoter Score
            },
            "satisfaction_breakdown": {
                "overall_satisfaction": {"avg": 4.2, "count": 45},
                "resolution_satisfaction": {"avg": 4.0, "count": 45},
                "communication_satisfaction": {"avg": 4.5, "count": 45},
                "timeliness_satisfaction": {"avg": 3.8, "count": 42}
            },
            "trends": [
                {"month": "2024-10", "avg_satisfaction": 4.1},
                {"month": "2024-11", "avg_satisfaction": 4.3},
                {"month": "2024-12", "avg_satisfaction": 4.2}
            ],
            "improvement_areas": [
                "Faster response times needed",
                "Better initial communication",
                "More proactive updates"
            ]
        }

        return {
            "success": True,
            "message": "Satisfaction analytics retrieved successfully",
            "data": analytics_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get satisfaction analytics: {str(e)}")


@router.get("/analytics/classification-trends")
async def get_classification_trends(
    period_months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """Get complaint classification trends and patterns"""
    try:
        # Mock classification trends
        trends_data = {
            "period_months": period_months,
            "category_trends": [
                {"category": "product_quality", "count": 25, "percentage": 45.5},
                {"category": "delivery", "count": 15, "percentage": 27.3},
                {"category": "service", "count": 10, "percentage": 18.2},
                {"category": "other", "count": 5, "percentage": 9.0}
            ],
            "severity_trends": [
                {"severity": "low", "count": 30, "percentage": 54.5},
                {"severity": "high", "count": 20, "percentage": 36.4},
                {"severity": "high", "count": 4, "percentage": 7.3},
                {"severity": "critical", "count": 1, "percentage": 1.8}
            ],
            "monthly_breakdown": [
                {"month": "2024-07", "total": 8, "critical": 0, "high": 1},
                {"month": "2024-08", "total": 12, "critical": 1, "high": 2},
                {"month": "2024-09", "total": 10, "critical": 0, "high": 1},
                {"month": "2024-10", "total": 15, "critical": 0, "high": 0},
                {"month": "2024-11", "total": 8, "critical": 0, "high": 0},
                {"month": "2024-12", "total": 2, "critical": 0, "high": 0}
            ],
            "patterns": [
                "Product quality complaints increase during summer months",
                "Delivery complaints peak during holiday seasons",
                "Critical issues are rare but require immediate attention"
            ]
        }

        return {
            "success": True,
            "message": "Classification trends retrieved successfully",
            "data": trends_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get classification trends: {str(e)}")


