from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.nonconformance_service import NonConformanceService
from app.schemas.nonconformance import (
    NonConformanceCreate, NonConformanceUpdate, NonConformanceResponse, NonConformanceListResponse,
    RootCauseAnalysisCreate, RootCauseAnalysisUpdate, RootCauseAnalysisResponse, RootCauseAnalysisListResponse,
    CAPAActionCreate, CAPAActionUpdate, CAPAActionResponse, CAPAListResponse,
    CAPAVerificationCreate, CAPAVerificationUpdate, CAPAVerificationResponse, VerificationListResponse,
    NonConformanceAttachmentCreate, NonConformanceAttachmentResponse, AttachmentListResponse,
    NonConformanceFilter, CAPAFilter, BulkNonConformanceAction, BulkCAPAAction,
    NonConformanceDashboardStats, FiveWhysAnalysis, IshikawaAnalysis, RootCauseAnalysisRequest, RootCauseMethod
)
from app.utils.audit import audit_event

router = APIRouter()


# Non-Conformance endpoints
@router.get("/", response_model=NonConformanceListResponse)
async def get_non_conformances(
    search: Optional[str] = Query(None, description="Search by title, description, or NC number"),
    source: Optional[str] = Query(None, description="Filter by source"),
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    impact_area: Optional[str] = Query(None, description="Filter by impact area"),
    reported_by: Optional[int] = Query(None, description="Filter by reported by"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned to"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get non-conformances with filtering and pagination"""
    filter_params = NonConformanceFilter(
        search=search,
        source=source,
        status=status,
        severity=severity,
        impact_area=impact_area,
        reported_by=reported_by,
        assigned_to=assigned_to,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size
    )
    
    service = NonConformanceService(db)
    result = service.get_non_conformances(filter_params)
    
    return NonConformanceListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/{nc_id}", response_model=NonConformanceResponse)
async def get_non_conformance(
    nc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get non-conformance by ID"""
    service = NonConformanceService(db)
    non_conformance = service.get_non_conformance(nc_id)
    
    if not non_conformance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    return non_conformance


@router.post("/", response_model=NonConformanceResponse)
async def create_non_conformance(
    nc_data: NonConformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new non-conformance"""
    service = NonConformanceService(db)
    non_conformance = service.create_non_conformance(nc_data, current_user.id)
    try:
        audit_event(db, current_user.id, "nc_created", "nc_capa", str(non_conformance.id), {"source": nc_data.source})
    except Exception:
        pass
    return non_conformance


@router.put("/{nc_id}", response_model=NonConformanceResponse)
async def update_non_conformance(
    nc_id: int,
    nc_data: NonConformanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update non-conformance"""
    service = NonConformanceService(db)
    try:
        non_conformance = service.update_non_conformance(nc_id, nc_data)
    except ValueError as ve:
        # Invalid transition or unmet verification preconditions
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    
    if not non_conformance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    try:
        audit_event(db, current_user.id, "nc_updated", "nc_capa", str(non_conformance.id))
    except Exception:
        pass
    return non_conformance


@router.delete("/{nc_id}")
async def delete_non_conformance(
    nc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete non-conformance"""
    service = NonConformanceService(db)
    success = service.delete_non_conformance(nc_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    try:
        audit_event(db, current_user.id, "nc_deleted", "nc_capa", str(nc_id))
    except Exception:
        pass
    return {"message": "Non-conformance deleted successfully"}


@router.post("/bulk/action")
async def bulk_update_non_conformances(
    action_data: BulkNonConformanceAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update non-conformances"""
    service = NonConformanceService(db)
    result = service.bulk_update_non_conformances(action_data)
    
    return {
        "message": f"Updated {result['updated_count']} out of {result['total_requested']} non-conformances",
        "updated_count": result["updated_count"],
        "total_requested": result["total_requested"]
    }


# Root Cause Analysis endpoints
@router.get("/{nc_id}/root-cause-analyses/", response_model=List[RootCauseAnalysisResponse])
async def get_root_cause_analyses(
    nc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get root cause analyses for a non-conformance"""
    service = NonConformanceService(db)
    analyses = service.get_root_cause_analyses(nc_id)
    return analyses


@router.get("/root-cause-analyses/{analysis_id}", response_model=RootCauseAnalysisResponse)
async def get_root_cause_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get root cause analysis by ID"""
    service = NonConformanceService(db)
    analysis = service.get_root_cause_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Root cause analysis not found"
        )
    
    return analysis


@router.post("/{nc_id}/root-cause-analyses/", response_model=RootCauseAnalysisResponse)
async def create_root_cause_analysis(
    nc_id: int,
    analysis_data: RootCauseAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new root cause analysis"""
    service = NonConformanceService(db)
    
    # Check if non-conformance exists
    non_conformance = service.get_non_conformance(nc_id)
    if not non_conformance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    analysis_data.non_conformance_id = nc_id
    analysis = service.create_root_cause_analysis(analysis_data, current_user.id)
    try:
        audit_event(db, current_user.id, "rca_created", "nc_capa", str(analysis.id), {"nc_id": nc_id})
    except Exception:
        pass
    return analysis


@router.put("/root-cause-analyses/{analysis_id}", response_model=RootCauseAnalysisResponse)
async def update_root_cause_analysis(
    analysis_id: int,
    analysis_data: RootCauseAnalysisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update root cause analysis"""
    service = NonConformanceService(db)
    analysis = service.update_root_cause_analysis(analysis_id, analysis_data)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Root cause analysis not found"
        )
    
    try:
        audit_event(db, current_user.id, "rca_updated", "nc_capa", str(analysis.id))
    except Exception:
        pass
    return analysis


@router.delete("/root-cause-analyses/{analysis_id}")
async def delete_root_cause_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete root cause analysis"""
    service = NonConformanceService(db)
    success = service.delete_root_cause_analysis(analysis_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Root cause analysis not found"
        )
    
    try:
        audit_event(db, current_user.id, "rca_deleted", "nc_capa", str(analysis_id))
    except Exception:
        pass
    return {"message": "Root cause analysis deleted successfully"}


# HACCP helpers
@router.get("/haccp/recent-nc")
async def get_recent_haccp_nc(
    ccp_id: int = Query(..., description="CCP id"),
    batch_number: Optional[str] = Query(None, description="Optional batch number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the most recent HACCP-origin NC for a given CCP and optional batch number."""
    service = NonConformanceService(db)
    nc = service.get_recent_nc_for_haccp(ccp_id=ccp_id, batch_number=batch_number)
    if not nc:
        return {"found": False}
    return {
        "found": True,
        "id": nc.id,
        "nc_number": nc.nc_number,
        "title": nc.title,
        "status": nc.status,
        "severity": nc.severity,
        "reported_date": nc.reported_date,
    }


# CAPA Action endpoints
@router.get("/capas/", response_model=CAPAListResponse)
async def get_capa_actions(
    non_conformance_id: Optional[int] = Query(None, description="Filter by non-conformance"),
    status: Optional[str] = Query(None, description="Filter by status"),
    responsible_person: Optional[int] = Query(None, description="Filter by responsible person"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CAPA actions with filtering and pagination"""
    filter_params = CAPAFilter(
        non_conformance_id=non_conformance_id,
        status=status,
        responsible_person=responsible_person,
        action_type=action_type,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size
    )
    
    service = NonConformanceService(db)
    result = service.get_capa_actions(filter_params)
    
    return CAPAListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/capas/{capa_id}", response_model=CAPAActionResponse)
async def get_capa_action(
    capa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CAPA action by ID"""
    service = NonConformanceService(db)
    capa_action = service.get_capa_action(capa_id)
    
    if not capa_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA action not found"
        )
    
    return capa_action


@router.post("/{nc_id}/capas/", response_model=CAPAActionResponse)
async def create_capa_action(
    nc_id: int,
    capa_data: CAPAActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new CAPA action"""
    service = NonConformanceService(db)
    
    # Check if non-conformance exists
    non_conformance = service.get_non_conformance(nc_id)
    if not non_conformance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    capa_data.non_conformance_id = nc_id
    capa_action = service.create_capa_action(capa_data, current_user.id)
    try:
        audit_event(db, current_user.id, "capa_created", "nc_capa", str(capa_action.id), {"nc_id": nc_id})
    except Exception:
        pass
    return capa_action


@router.put("/capas/{capa_id}", response_model=CAPAActionResponse)
async def update_capa_action(
    capa_id: int,
    capa_data: CAPAActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CAPA action"""
    service = NonConformanceService(db)
    capa_action = service.update_capa_action(capa_id, capa_data)
    
    if not capa_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA action not found"
        )
    
    try:
        audit_event(db, current_user.id, "capa_updated", "nc_capa", str(capa_action.id))
    except Exception:
        pass
    return capa_action


@router.delete("/capas/{capa_id}")
async def delete_capa_action(
    capa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete CAPA action"""
    service = NonConformanceService(db)
    success = service.delete_capa_action(capa_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA action not found"
        )
    
    try:
        audit_event(db, current_user.id, "capa_deleted", "nc_capa", str(capa_id))
    except Exception:
        pass
    return {"message": "CAPA action deleted successfully"}


@router.post("/capas/bulk/action")
async def bulk_update_capa_actions(
    action_data: BulkCAPAAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update CAPA actions"""
    service = NonConformanceService(db)
    result = service.bulk_update_capa_actions(action_data)
    
    return {
        "message": f"Updated {result['updated_count']} out of {result['total_requested']} CAPA actions",
        "updated_count": result["updated_count"],
        "total_requested": result["total_requested"]
    }


# CAPA Verification endpoints
@router.get("/{nc_id}/verifications/", response_model=List[CAPAVerificationResponse])
async def get_capa_verifications(
    nc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CAPA verifications for a non-conformance"""
    service = NonConformanceService(db)
    verifications = service.get_capa_verifications(nc_id)
    return verifications


@router.get("/verifications/{verification_id}", response_model=CAPAVerificationResponse)
async def get_capa_verification(
    verification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CAPA verification by ID"""
    service = NonConformanceService(db)
    verification = service.get_capa_verification(verification_id)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA verification not found"
        )
    
    return verification


@router.post("/{nc_id}/capas/{capa_id}/verifications/", response_model=CAPAVerificationResponse)
async def create_capa_verification(
    nc_id: int,
    capa_id: int,
    verification_data: CAPAVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new CAPA verification"""
    service = NonConformanceService(db)
    
    # Check if non-conformance and CAPA action exist
    non_conformance = service.get_non_conformance(nc_id)
    if not non_conformance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    capa_action = service.get_capa_action(capa_id)
    if not capa_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA action not found"
        )
    
    verification_data.non_conformance_id = nc_id
    verification_data.capa_action_id = capa_id
    verification = service.create_capa_verification(verification_data, current_user.id)
    try:
        audit_event(db, current_user.id, "capa_verification_created", "nc_capa", str(verification.id), {"nc_id": nc_id, "capa_id": capa_id})
    except Exception:
        pass
    return verification


@router.put("/verifications/{verification_id}", response_model=CAPAVerificationResponse)
async def update_capa_verification(
    verification_id: int,
    verification_data: CAPAVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CAPA verification"""
    service = NonConformanceService(db)
    verification = service.update_capa_verification(verification_id, verification_data)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA verification not found"
        )
    
    try:
        audit_event(db, current_user.id, "capa_verification_updated", "nc_capa", str(verification.id))
    except Exception:
        pass
    return verification


@router.delete("/verifications/{verification_id}")
async def delete_capa_verification(
    verification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete CAPA verification"""
    service = NonConformanceService(db)
    success = service.delete_capa_verification(verification_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPA verification not found"
        )
    
    try:
        audit_event(db, current_user.id, "capa_verification_deleted", "nc_capa", str(verification_id))
    except Exception:
        pass
    return {"message": "CAPA verification deleted successfully"}


# Attachment endpoints
@router.get("/{nc_id}/attachments/", response_model=List[NonConformanceAttachmentResponse])
async def get_attachments(
    nc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attachments for a non-conformance"""
    service = NonConformanceService(db)
    attachments = service.get_attachments(nc_id)
    return attachments


@router.post("/{nc_id}/attachments/", response_model=NonConformanceAttachmentResponse)
async def create_attachment(
    nc_id: int,
    attachment_type: str = Query(..., description="Type of attachment"),
    description: Optional[str] = Query(None, description="Attachment description"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload an attachment for a non-conformance"""
    service = NonConformanceService(db)
    
    # Check if non-conformance exists
    non_conformance = service.get_non_conformance(nc_id)
    if not non_conformance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-conformance not found"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/non_conformance_attachments"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = f"{upload_dir}/{nc_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    attachment_data = NonConformanceAttachmentCreate(
        non_conformance_id=nc_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file.size,
        file_type=file.content_type,
        original_filename=file.filename,
        attachment_type=attachment_type,
        description=description
    )
    
    attachment = service.create_attachment(attachment_data, current_user.id)
    try:
        audit_event(db, current_user.id, "nc_attachment_uploaded", "nc_capa", str(attachment.id), {"nc_id": nc_id})
    except Exception:
        pass
    return attachment


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete attachment"""
    service = NonConformanceService(db)
    success = service.delete_attachment(attachment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    try:
        audit_event(db, current_user.id, "nc_attachment_deleted", "nc_capa", str(attachment_id))
    except Exception:
        pass
    return {"message": "Attachment deleted successfully"}


# Dashboard endpoints
@router.get("/dashboard/stats", response_model=NonConformanceDashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get non-conformance dashboard statistics"""
    service = NonConformanceService(db)
    stats = service.get_dashboard_stats()
    return stats


@router.get("/alerts/overdue-capas")
async def get_overdue_capas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue CAPA actions"""
    service = NonConformanceService(db)
    overdue_capas = service.get_overdue_capas()
    return {"overdue_capas": overdue_capas}


@router.get("/source/{source}/non-conformances")
async def get_non_conformances_by_source(
    source: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get non-conformances by source"""
    service = NonConformanceService(db)
    ncs = service.get_non_conformances_by_source(source)
    return {"non_conformances": ncs}


# Root cause analysis tools
@router.post("/{nc_id}/tools/five-whys", response_model=RootCauseAnalysisResponse)
async def persist_five_whys(
    nc_id: int,
    analysis: FiveWhysAnalysis,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Persist a 5 Whys analysis as RootCauseAnalysis for an NC"""
    service = NonConformanceService(db)
    non_conformance = service.get_non_conformance(nc_id)
    if not non_conformance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-conformance not found")

    rca = service.create_root_cause_analysis(
        RootCauseAnalysisCreate(
            non_conformance_id=nc_id,
            method=RootCauseMethod.FIVE_WHYS,
            analysis_date=datetime.utcnow(),
            immediate_cause=analysis.why_1,
            underlying_cause=analysis.why_2,
            root_cause=analysis.root_cause,
            why_1=analysis.why_1,
            why_2=analysis.why_2,
            why_3=analysis.why_3,
            why_4=analysis.why_4,
            why_5=analysis.why_5,
            contributing_factors=[],
            system_failures=[],
            recommendations=[],
            preventive_measures=[],
        ),
        conducted_by=current_user.id,
    )
    try:
        audit_event(db, current_user.id, "rca_5whys_created", "nc_capa", str(rca.id), {"nc_id": nc_id})
    except Exception:
        pass
    # Refresh to ensure fully bound instance for response serialization
    return service.get_root_cause_analysis(rca.id)


@router.post("/{nc_id}/tools/ishikawa", response_model=RootCauseAnalysisResponse)
async def persist_ishikawa(
    nc_id: int,
    analysis: IshikawaAnalysis,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Persist an Ishikawa/Fishbone analysis as RootCauseAnalysis for an NC"""
    service = NonConformanceService(db)
    non_conformance = service.get_non_conformance(nc_id)
    if not non_conformance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-conformance not found")

    rca = service.create_root_cause_analysis(
        RootCauseAnalysisCreate(
            non_conformance_id=nc_id,
            method=RootCauseMethod.ISHIKAWA,
            analysis_date=datetime.utcnow(),
            fishbone_categories=analysis.categories,
            fishbone_diagram_data=analysis.diagram_data,
            recommendations=[],
            preventive_measures=[],
        ),
        conducted_by=current_user.id,
    )
    try:
        audit_event(db, current_user.id, "rca_ishikawa_created", "nc_capa", str(rca.id), {"nc_id": nc_id})
    except Exception:
        pass
    return service.get_root_cause_analysis(rca.id)