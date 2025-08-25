#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Objectives API Endpoints for Phase 1 Implementation
Supports corporate and departmental objectives with advanced tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import require_permission, get_current_active_user
from app.services.objectives_service_enhanced import ObjectivesServiceEnhanced
from app.schemas.objectives_enhanced import (
    ObjectiveCreate, ObjectiveUpdate, Objective,
    ObjectiveTargetCreate, ObjectiveTargetUpdate, ObjectiveTarget,
    ObjectiveProgressCreate, ObjectiveProgressUpdate, ObjectiveProgress,
    DepartmentCreate, DepartmentUpdate, Department,
    DashboardKPIs, PerformanceMetrics, TrendAnalysis, PerformanceAlert,
    ObjectivesListResponse, ObjectivesDashboardResponse, ObjectiveDetailResponse,
    ObjectiveHierarchy, BulkProgressCreate, BulkTargetCreate, ObjectiveLinks, ObjectiveLinksUpdate,
    ObjectiveType, HierarchyLevel, PerformanceColor, TrendDirection, ObjectiveEvidence, ObjectiveEvidenceList
)
from app.models.rbac import Module
from app.models.food_safety_objectives import FoodSafetyObjective
from fastapi import UploadFile, File, Form
from app.services.storage_service import StorageService
from app.models.audit import AuditLog

router = APIRouter()


# ============================================================================
# OBJECTIVES MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=Objective, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "CREATE")))])
def create_objective(
    objective: ObjectiveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Create a new objective"""
    service = ObjectivesServiceEnhanced(db)
    
    try:
        payload = objective.model_dump()
        if not payload.get("created_by"):
            payload["created_by"] = current_user.id
        result = service.create_objective(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create objective: {str(e)}"
        )





@router.get("/", response_model=ObjectivesListResponse, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def list_objectives_root(
    objective_type: Optional[ObjectiveType] = Query(None, description="Filter by objective type"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    hierarchy_level: Optional[HierarchyLevel] = Query(None, description="Filter by hierarchy level"),
    status: Optional[str] = Query(None, description="Filter by status"),
    performance_color: Optional[PerformanceColor] = Query(None, description="Filter by performance color"),
    trend_direction: Optional[TrendDirection] = Query(None, description="Filter by trend direction"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """List objectives with filtering and pagination (root endpoint)"""
    service = ObjectivesServiceEnhanced(db)
    
    # Calculate offset
    offset = (page - 1) * size
    
    # Get objectives
    objectives = service.list_objectives(
        objective_type=objective_type,
        department_id=department_id,
        hierarchy_level=hierarchy_level,
        status=status,
        limit=size,
        offset=offset
    )
    
    # Get total count for pagination
    total_query = service.db.query(service.db.query(FoodSafetyObjective).filter(
        FoodSafetyObjective.status == 'active'
    ).subquery())
    total = total_query.count()
    
    return ObjectivesListResponse(
        objectives=objectives,
        total=total,
        page=page,
        size=size,
        has_next=offset + size < total,
        has_prev=page > 1
    )


# ============================================================================
# CORPORATE AND DEPARTMENTAL OBJECTIVES ENDPOINTS
# ============================================================================

@router.get("/corporate", response_model=List[Objective], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_corporate_objectives(
    db: Session = Depends(get_db)
):
    """Get all corporate objectives"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_corporate_objectives()


@router.get("/departmental/{department_id}", response_model=List[Objective], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_departmental_objectives(
    department_id: int = Path(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """Get objectives for a specific department"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_departmental_objectives(department_id)


@router.get("/hierarchy", response_model=ObjectiveHierarchy, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_hierarchical_objectives(
    db: Session = Depends(get_db)
):
    """Get objectives in hierarchical structure"""
    service = ObjectivesServiceEnhanced(db)
    hierarchy = service.get_hierarchical_objectives()
    return ObjectiveHierarchy(objectives=hierarchy)


@router.get("/export", response_model=Dict[str, Any], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "EXPORT")))])
def export_objectives(
    format: str = Query("json", description="Export format (json, csv, pdf)"),
    objective_type: Optional[ObjectiveType] = Query(None, description="Filter by objective type"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """Export objectives data"""
    service = ObjectivesServiceEnhanced(db)
    
    # Get objectives based on filters
    objectives = service.list_objectives(
        objective_type=objective_type,
        department_id=department_id
    )
    
    # Assemble related data
    all_targets = []
    all_progress = []
    for obj in objectives:
        all_targets.extend(service.get_targets(obj.id))
        all_progress.extend(service.get_progress(obj.id, limit=100))

    # Convert SQLAlchemy objects to dictionaries
    objectives_dict = []
    for obj in objectives:
        obj_dict = {
            "id": obj.id,
            "objective_code": obj.objective_code,
            "title": obj.title,
            "description": obj.description,
            "category": obj.category,
            "objective_type": obj.objective_type.value if hasattr(obj.objective_type, 'value') else str(obj.objective_type),
            "hierarchy_level": obj.hierarchy_level.value if hasattr(obj.hierarchy_level, 'value') else str(obj.hierarchy_level),
            "status": obj.status,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        objectives_dict.append(obj_dict)
    
    targets_dict = []
    for target in all_targets:
        target_dict = {
            "id": target.id,
            "objective_id": target.objective_id,
            "period_start": target.period_start,
            "period_end": target.period_end,
            "target_value": target.target_value,
            "created_at": target.created_at
        }
        targets_dict.append(target_dict)
    
    progress_dict = []
    for prog in all_progress:
        prog_dict = {
            "id": prog.id,
            "objective_id": prog.objective_id,
            "period_start": prog.period_start,
            "period_end": prog.period_end,
            "actual_value": prog.actual_value,
            "attainment_percent": prog.attainment_percent,
            "status": prog.status,
            "created_at": prog.created_at
        }
        progress_dict.append(prog_dict)

    export_payload = {
        "export_date": datetime.utcnow(),
        "export_format": format,
        "objectives": objectives_dict,
        "targets": targets_dict,
        "progress": progress_dict,
    }

    return export_payload


@router.get("/{objective_id}", response_model=ObjectiveDetailResponse, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_objective(
    objective_id: int = Path(..., description="Objective ID"),
    db: Session = Depends(get_db)
):
    """Get objective details with related data"""
    service = ObjectivesServiceEnhanced(db)
    
    objective = service.get_objective(objective_id)
    if not objective:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found"
        )
    
    # Get related data
    targets = service.get_targets(objective_id)
    progress = service.get_progress(objective_id)
    trend_analysis = service.get_trend_analysis(objective_id)
    # Get child objectives by filtering for parent_objective_id
    child_objectives = service.db.query(FoodSafetyObjective).filter(
        FoodSafetyObjective.parent_objective_id == objective_id
    ).all()
    
    return ObjectiveDetailResponse(
        objective=objective,
        targets=targets,
        progress=progress,
        trend_analysis=trend_analysis,
        child_objectives=child_objectives
    )


@router.put("/{objective_id}", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def update_objective(
    objective_id: int = Path(..., description="Objective ID"),
    objective_update: ObjectiveUpdate = None,
    db: Session = Depends(get_db)
):
    """Update an objective"""
    service = ObjectivesServiceEnhanced(db)
    
    result = service.update_objective(objective_id, objective_update.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found"
        )
    
    return result


@router.delete("/{objective_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "DELETE")))])
def delete_objective(
    objective_id: int = Path(..., description="Objective ID"),
    db: Session = Depends(get_db)
):
    """Delete an objective (soft delete)"""
    service = ObjectivesServiceEnhanced(db)
    
    success = service.delete_objective(objective_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found"
        )


# ============================================================================
# PROGRESS TRACKING ENDPOINTS
# ============================================================================

@router.post("/{objective_id}/progress", response_model=ObjectiveProgress, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def create_progress(
    objective_id: int = Path(..., description="Objective ID"),
    progress: ObjectiveProgressCreate = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Record progress for an objective"""
    service = ObjectivesServiceEnhanced(db)
    
    # Ensure objective_id matches
    if progress.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objective ID mismatch"
        )
    
    try:
        payload = progress.model_dump()
        if not payload.get("created_by"):
            payload["created_by"] = current_user.id
        result = service.create_progress(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create progress: {str(e)}"
        )


@router.get("/{objective_id}/progress", response_model=List[ObjectiveProgress], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_progress(
    objective_id: int = Path(..., description="Objective ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    db: Session = Depends(get_db)
):
    """Get progress history for an objective"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_progress(objective_id, limit)


@router.get("/{objective_id}/progress/trend", response_model=TrendAnalysis, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_trend_analysis(
    objective_id: int = Path(..., description="Objective ID"),
    periods: int = Query(6, ge=2, le=12, description="Number of periods to analyze"),
    db: Session = Depends(get_db)
):
    """Get trend analysis for an objective"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_trend_analysis(objective_id, periods)


@router.post("/{objective_id}/progress/bulk", response_model=List[ObjectiveProgress], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def create_bulk_progress(
    objective_id: int = Path(..., description="Objective ID"),
    bulk_progress: BulkProgressCreate = None,
    db: Session = Depends(get_db)
):
    """Create multiple progress entries for an objective"""
    service = ObjectivesServiceEnhanced(db)
    
    if bulk_progress.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objective ID mismatch"
        )
    
    results = []
    for progress_data in bulk_progress.progress_entries:
        progress_data.objective_id = objective_id
        result = service.create_progress(progress_data.model_dump())
        results.append(result)
    
    return results


# ============================================================================
# TARGET MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{objective_id}/targets", response_model=ObjectiveTarget, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def create_target(
    objective_id: int = Path(..., description="Objective ID"),
    target: ObjectiveTargetCreate = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Create a target for an objective"""
    service = ObjectivesServiceEnhanced(db)
    
    if target.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objective ID mismatch"
        )
    
    try:
        payload = target.model_dump()
        if not payload.get("created_by"):
            payload["created_by"] = current_user.id
        result = service.create_target(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create target: {str(e)}"
        )


@router.get("/{objective_id}/targets", response_model=List[ObjectiveTarget], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_targets(
    objective_id: int = Path(..., description="Objective ID"),
    db: Session = Depends(get_db)
):
    """Get targets for an objective"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_targets(objective_id)


@router.post("/{objective_id}/targets/bulk", response_model=List[ObjectiveTarget], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def create_bulk_targets(
    objective_id: int = Path(..., description="Objective ID"),
    bulk_targets: BulkTargetCreate = None,
    db: Session = Depends(get_db)
):
    """Create multiple targets for an objective"""
    service = ObjectivesServiceEnhanced(db)
    
    if bulk_targets.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objective ID mismatch"
        )
    
    results = []
    for target_data in bulk_targets.targets:
        target_data.objective_id = objective_id
        result = service.create_target(target_data.model_dump())
        results.append(result)
    
    return results


# ============================================================================
# DASHBOARD INTEGRATION ENDPOINTS
# ============================================================================

@router.get("/dashboard/kpis", response_model=DashboardKPIs, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_dashboard_kpis(
    db: Session = Depends(get_db)
):
    """Get KPI summary for dashboard"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_dashboard_kpis()


@router.get("/dashboard/performance", response_model=PerformanceMetrics, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_performance_metrics(
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """Get performance metrics for objectives"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_performance_metrics(department_id)


@router.get("/dashboard/trends", response_model=List[TrendAnalysis], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_dashboard_trends(
    objective_ids: List[int] = Query(..., description="List of objective IDs to analyze"),
    periods: int = Query(6, ge=2, le=12, description="Number of periods to analyze"),
    db: Session = Depends(get_db)
):
    """Get trend analysis for multiple objectives"""
    service = ObjectivesServiceEnhanced(db)
    
    trends = []
    for objective_id in objective_ids:
        trend = service.get_trend_analysis(objective_id, periods)
        trends.append(trend)
    
    return trends


@router.get("/dashboard/alerts", response_model=List[PerformanceAlert], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_dashboard_alerts(
    db: Session = Depends(get_db)
):
    """Get performance alerts for dashboard"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_alerts()


@router.get("/dashboard/summary", response_model=Dict[str, Any], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """Get aggregated dashboard data"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_dashboard_summary()


@router.get("/dashboard/comparison", response_model=Dict[str, Any], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_performance_comparison(
    period_start: datetime = Query(..., description="Comparison period start"),
    period_end: datetime = Query(..., description="Comparison period end"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """Get performance comparison between periods"""
    service = ObjectivesServiceEnhanced(db)
    
    # This would be implemented in the service
    # For now, return a placeholder
    return {
        "current_period": {
            "average_attainment": 85.5,
            "objectives_count": 12,
            "on_track_percentage": 75.0
        },
        "previous_period": {
            "average_attainment": 82.3,
            "objectives_count": 12,
            "on_track_percentage": 70.0
        },
        "improvement": {
            "attainment_change": 3.2,
            "on_track_change": 5.0
        }
    }


# =========================================================================
# DEPARTMENT MANAGEMENT ENDPOINTS
# =========================================================================

@router.post("/departments", response_model=Department, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new department"""
    service = ObjectivesServiceEnhanced(db)
    
    try:
        created = service.create_department(department.model_dump())
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create department: {str(e)}"
        )


@router.get("/departments", response_model=List[Department], dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def list_departments(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """List departments"""
    service = ObjectivesServiceEnhanced(db)
    return service.list_departments(status=status)


@router.get("/departments/{department_id}", response_model=Department, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_department(
    department_id: int = Path(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """Get a specific department"""
    service = ObjectivesServiceEnhanced(db)
    dept = service.get_department(department_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return dept


@router.put("/departments/{department_id}", response_model=Department, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def update_department(
    department_id: int = Path(..., description="Department ID"),
    payload: DepartmentUpdate = None,
    db: Session = Depends(get_db)
):
    """Update a department"""
    service = ObjectivesServiceEnhanced(db)
    updated = service.update_department(department_id, (payload.model_dump(exclude_unset=True) if payload else {}))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return updated


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "DELETE")))])
def delete_department(
    department_id: int = Path(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """Delete (soft) a department"""
    service = ObjectivesServiceEnhanced(db)
    ok = service.delete_department(department_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return None


# =========================================================================
# UTILITY ENDPOINTS
# =========================================================================

@router.get("/progress/summary", response_model=Dict[str, Any])
def get_progress_summary(
    objective_id: Optional[int] = Query(None, description="Filter by objective ID"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    period_start: Optional[datetime] = Query(None, description="Period start"),
    period_end: Optional[datetime] = Query(None, description="Period end"),
    db: Session = Depends(get_db)
):
    """Get progress summary for dashboard"""
    service = ObjectivesServiceEnhanced(db)
    
    # This would be implemented in the service
    # For now, return a placeholder
    return {
        "total_progress_entries": 45,
        "average_attainment": 87.3,
        "on_track_count": 32,
        "at_risk_count": 8,
        "off_track_count": 5,
        "recent_entries": 12
    }





# =========================================================================
# LINKAGES ENDPOINTS
# =========================================================================

@router.get("/{objective_id}/links", response_model=ObjectiveLinks, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def get_objective_links(
    objective_id: int = Path(..., description="Objective ID"),
    db: Session = Depends(get_db)
):
    service = ObjectivesServiceEnhanced(db)
    links = service.get_objective_links(objective_id)
    if not links:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    return links


@router.put("/{objective_id}/links", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def update_objective_links(
    objective_id: int = Path(..., description="Objective ID"),
    payload: ObjectiveLinksUpdate = None,
    db: Session = Depends(get_db)
):
    service = ObjectivesServiceEnhanced(db)
    updated = service.update_objective_links(objective_id, payload.model_dump(exclude_unset=True) if payload else {})
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    return updated
 
 
# =========================================================================
# EVIDENCE ENDPOINTS
# =========================================================================

@router.post("/{objective_id}/evidence", response_model=ObjectiveEvidence, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def upload_evidence(
    objective_id: int = Path(..., description="Objective ID"),
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    progress_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # Validate objective
    service = ObjectivesServiceEnhanced(db)
    obj = service.get_objective(objective_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")

    storage = StorageService(base_upload_dir="uploads/objectives")
    file_path, file_size, content_type, original_filename, checksum = storage.save_upload(file, subdir=str(objective_id))

    from app.models.food_safety_objectives import ObjectiveEvidence as EvidenceModel
    evidence = EvidenceModel(
        objective_id=objective_id,
        progress_id=progress_id,
        file_path=file_path,
        original_filename=original_filename,
        content_type=content_type,
        file_size=file_size,
        checksum=checksum,
        notes=notes,
        uploaded_by=current_user.id,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # Audit log
    db.add(AuditLog(user_id=current_user.id, action="objective_evidence_upload", resource_type="objective", resource_id=str(objective_id), details={"evidence_id": evidence.id, "filename": original_filename}))
    db.commit()

    return evidence


@router.get("/{objective_id}/evidence", response_model=ObjectiveEvidenceList, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "VIEW")))])
def list_evidence(
    objective_id: int = Path(..., description="Objective ID"),
    db: Session = Depends(get_db)
):
    from app.models.food_safety_objectives import ObjectiveEvidence as EvidenceModel
    items = db.query(EvidenceModel).filter(EvidenceModel.objective_id == objective_id).order_by(EvidenceModel.uploaded_at.desc()).all()
    return {"data": items}


@router.delete("/{objective_id}/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "DELETE")))])
def delete_evidence(
    objective_id: int,
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    from app.models.food_safety_objectives import ObjectiveEvidence as EvidenceModel
    ev = db.query(EvidenceModel).filter(EvidenceModel.id == evidence_id, EvidenceModel.objective_id == objective_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    # Delete file
    storage = StorageService(base_upload_dir="uploads/objectives")
    storage.delete_file(ev.file_path)
    db.delete(ev)
    db.add(AuditLog(user_id=current_user.id, action="objective_evidence_delete", resource_type="objective", resource_id=str(objective_id), details={"evidence_id": evidence_id}))
    db.commit()
    return None


@router.post("/{objective_id}/evidence/{evidence_id}/verify", response_model=ObjectiveEvidence, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "APPROVE")))])
def verify_evidence(
    objective_id: int,
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    from app.models.food_safety_objectives import ObjectiveEvidence as EvidenceModel
    ev = db.query(EvidenceModel).filter(EvidenceModel.id == evidence_id, EvidenceModel.objective_id == objective_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    ev.is_verified = True
    ev.verified_by = current_user.id
    ev.verified_at = datetime.utcnow()
    db.add(AuditLog(user_id=current_user.id, action="objective_evidence_verify", resource_type="objective", resource_id=str(objective_id), details={"evidence_id": evidence_id}))
    db.commit(); db.refresh(ev)
    return ev

# =========================================================================
# WORKFLOW ENDPOINTS
# =========================================================================

@router.post("/{objective_id}/assign", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "ASSIGN")))])
def assign_owner(
    objective_id: int = Path(..., description="Objective ID"),
    owner_user_id: int = Query(..., description="New owner user ID"),
    db: Session = Depends(get_db)
):
    service = ObjectivesServiceEnhanced(db)
    updated = service.assign_owner(objective_id, owner_user_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    db.add(AuditLog(user_id=owner_user_id, action="objective_assign_owner", resource_type="objective", resource_id=str(objective_id), details={"owner_user_id": owner_user_id}))
    db.commit()
    return updated


@router.post("/{objective_id}/submit", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def submit_for_approval(
    objective_id: int = Path(..., description="Objective ID"),
    notes: Optional[str] = Query(None, description="Submission notes"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    service = ObjectivesServiceEnhanced(db)
    updated = service.submit_for_approval(objective_id, current_user.id, notes)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    db.add(AuditLog(user_id=current_user.id, action="objective_submit", resource_type="objective", resource_id=str(objective_id), details={"notes": notes}))
    db.commit()
    return updated


@router.post("/{objective_id}/approve", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "APPROVE")))])
def approve_objective(
    objective_id: int = Path(..., description="Objective ID"),
    notes: Optional[str] = Query(None, description="Approval notes"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    service = ObjectivesServiceEnhanced(db)
    updated = service.approve(objective_id, current_user.id, notes)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    db.add(AuditLog(user_id=current_user.id, action="objective_approve", resource_type="objective", resource_id=str(objective_id), details={"notes": notes}))
    db.commit()
    return updated


@router.post("/{objective_id}/reject", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "APPROVE")))])
def reject_objective(
    objective_id: int = Path(..., description="Objective ID"),
    notes: Optional[str] = Query(None, description="Rejection notes"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    service = ObjectivesServiceEnhanced(db)
    updated = service.reject(objective_id, current_user.id, notes)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    db.add(AuditLog(user_id=current_user.id, action="objective_reject", resource_type="objective", resource_id=str(objective_id), details={"notes": notes}))
    db.commit()
    return updated


@router.post("/{objective_id}/close", response_model=Objective, dependencies=[Depends(require_permission((Module.OBJECTIVES.value, "UPDATE")))])
def close_objective(
    objective_id: int = Path(..., description="Objective ID"),
    reason: Optional[str] = Query(None, description="Closure reason"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    service = ObjectivesServiceEnhanced(db)
    updated = service.close(objective_id, current_user.id, reason)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    db.add(AuditLog(user_id=current_user.id, action="objective_close", resource_type="objective", resource_id=str(objective_id), details={"reason": reason}))
    db.commit()
    return updated

# =========================================================================
# UTILITY ENDPOINTS
# =========================================================================
