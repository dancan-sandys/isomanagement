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
from app.services.objectives_service_enhanced import ObjectivesServiceEnhanced
from app.schemas.objectives_enhanced import (
    ObjectiveCreate, ObjectiveUpdate, Objective,
    ObjectiveTargetCreate, ObjectiveTargetUpdate, ObjectiveTarget,
    ObjectiveProgressCreate, ObjectiveProgressUpdate, ObjectiveProgress,
    DepartmentCreate, DepartmentUpdate, Department,
    DashboardKPIs, PerformanceMetrics, TrendAnalysis, PerformanceAlert,
    ObjectivesListResponse, ObjectivesDashboardResponse, ObjectiveDetailResponse,
    ObjectiveHierarchy, BulkProgressCreate, BulkTargetCreate,
    ObjectiveType, HierarchyLevel, PerformanceColor, TrendDirection
)
from app.models.food_safety_objectives import FoodSafetyObjective

router = APIRouter()


# ============================================================================
# OBJECTIVES MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=Objective, status_code=status.HTTP_201_CREATED)
def create_objective(
    objective: ObjectiveCreate,
    db: Session = Depends(get_db)
):
    """Create a new objective"""
    service = ObjectivesServiceEnhanced(db)
    
    try:
        result = service.create_objective(objective.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create objective: {str(e)}"
        )





@router.get("/", response_model=ObjectivesListResponse)
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


@router.get("/{objective_id}", response_model=ObjectiveDetailResponse)
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
    child_objectives = service.list_objectives(parent_objective_id=objective_id)
    
    return ObjectiveDetailResponse(
        objective=objective,
        targets=targets,
        progress=progress,
        trend_analysis=trend_analysis,
        child_objectives=child_objectives
    )


@router.put("/{objective_id}", response_model=Objective)
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


@router.delete("/{objective_id}", status_code=status.HTTP_204_NO_CONTENT)
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
# CORPORATE AND DEPARTMENTAL OBJECTIVES ENDPOINTS
# ============================================================================

@router.get("/corporate", response_model=List[Objective])
def get_corporate_objectives(
    db: Session = Depends(get_db)
):
    """Get all corporate objectives"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_corporate_objectives()


@router.get("/departmental/{department_id}", response_model=List[Objective])
def get_departmental_objectives(
    department_id: int = Path(..., description="Department ID"),
    db: Session = Depends(get_db)
):
    """Get objectives for a specific department"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_departmental_objectives(department_id)


@router.get("/hierarchy", response_model=ObjectiveHierarchy)
def get_hierarchical_objectives(
    db: Session = Depends(get_db)
):
    """Get objectives in hierarchical structure"""
    service = ObjectivesServiceEnhanced(db)
    hierarchy = service.get_hierarchical_objectives()
    return ObjectiveHierarchy(objectives=hierarchy)


# ============================================================================
# PROGRESS TRACKING ENDPOINTS
# ============================================================================

@router.post("/{objective_id}/progress", response_model=ObjectiveProgress, status_code=status.HTTP_201_CREATED)
def create_progress(
    objective_id: int = Path(..., description="Objective ID"),
    progress: ObjectiveProgressCreate = None,
    db: Session = Depends(get_db)
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
        result = service.create_progress(progress.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create progress: {str(e)}"
        )


@router.get("/{objective_id}/progress", response_model=List[ObjectiveProgress])
def get_progress(
    objective_id: int = Path(..., description="Objective ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    db: Session = Depends(get_db)
):
    """Get progress history for an objective"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_progress(objective_id, limit)


@router.get("/{objective_id}/progress/trend", response_model=TrendAnalysis)
def get_trend_analysis(
    objective_id: int = Path(..., description="Objective ID"),
    periods: int = Query(6, ge=2, le=12, description="Number of periods to analyze"),
    db: Session = Depends(get_db)
):
    """Get trend analysis for an objective"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_trend_analysis(objective_id, periods)


@router.post("/{objective_id}/progress/bulk", response_model=List[ObjectiveProgress], status_code=status.HTTP_201_CREATED)
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

@router.post("/{objective_id}/targets", response_model=ObjectiveTarget, status_code=status.HTTP_201_CREATED)
def create_target(
    objective_id: int = Path(..., description="Objective ID"),
    target: ObjectiveTargetCreate = None,
    db: Session = Depends(get_db)
):
    """Create a target for an objective"""
    service = ObjectivesServiceEnhanced(db)
    
    if target.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objective ID mismatch"
        )
    
    try:
        result = service.create_target(target.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create target: {str(e)}"
        )


@router.get("/{objective_id}/targets", response_model=List[ObjectiveTarget])
def get_targets(
    objective_id: int = Path(..., description="Objective ID"),
    db: Session = Depends(get_db)
):
    """Get targets for an objective"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_targets(objective_id)


@router.post("/{objective_id}/targets/bulk", response_model=List[ObjectiveTarget], status_code=status.HTTP_201_CREATED)
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

@router.get("/dashboard/kpis", response_model=DashboardKPIs)
def get_dashboard_kpis(
    db: Session = Depends(get_db)
):
    """Get KPI summary for dashboard"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_dashboard_kpis()


@router.get("/dashboard/performance", response_model=PerformanceMetrics)
def get_performance_metrics(
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    db: Session = Depends(get_db)
):
    """Get performance metrics for objectives"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_performance_metrics(department_id)


@router.get("/dashboard/trends", response_model=List[TrendAnalysis])
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


@router.get("/dashboard/alerts", response_model=List[PerformanceAlert])
def get_dashboard_alerts(
    db: Session = Depends(get_db)
):
    """Get performance alerts for dashboard"""
    service = ObjectivesServiceEnhanced(db)
    return service.get_alerts()


@router.get("/dashboard/comparison", response_model=Dict[str, Any])
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


# ============================================================================
# DEPARTMENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/departments", response_model=Department, status_code=status.HTTP_201_CREATED)
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


@router.get("/departments", response_model=List[Department])
def list_departments(
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """List departments"""
    service = ObjectivesServiceEnhanced(db)
    return service.list_departments(status=status)


@router.get("/departments/{department_id}", response_model=Department)
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


@router.put("/departments/{department_id}", response_model=Department)
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


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
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


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

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


@router.get("/export", response_model=Dict[str, Any])
def export_objectives(
    format: str = Query("json", description="Export format (json, csv, excel)"),
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
    
    # This would implement actual export logic
    # For now, return a placeholder
    return {
        "export_date": datetime.utcnow(),
        "format": format,
        "objectives_count": len(objectives),
        "download_url": f"/api/v1/objectives/export/download/{format}"
    }
