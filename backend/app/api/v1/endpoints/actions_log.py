# -*- coding: utf-8 -*-
"""
Actions Log API Endpoints
Phase 3: FastAPI endpoints for action tracking and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.services.actions_log_service import ActionsLogService
from app.schemas.actions_log import (
    ActionLogCreate, ActionLogUpdate, ActionLogResponse,
    ActionsAnalytics, ActionStatus, ActionPriority, ActionSource
)

router = APIRouter()


@router.post("/actions", response_model=ActionLogResponse)
def create_action(payload: ActionLogCreate, db: Session = Depends(get_db)):
    """Create a new action log entry"""
    service = ActionsLogService(db)
    try:
        action = service.create_action(payload.model_dump())
        return action
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/actions", response_model=List[ActionLogResponse])
def list_actions(
    status: Optional[ActionStatus] = Query(None),
    priority: Optional[ActionPriority] = Query(None),
    source: Optional[ActionSource] = Query(None),
    assigned_to: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List actions with filtering"""
    service = ActionsLogService(db)
    actions = service.list_actions(
        status=status,
        priority=priority,
        source=source,
        assigned_to=assigned_to,
        department_id=department_id,
        limit=limit,
        offset=offset
    )
    return actions


@router.get("/actions/{action_id}", response_model=ActionLogResponse)
def get_action(action_id: int, db: Session = Depends(get_db)):
    """Get action by ID"""
    service = ActionsLogService(db)
    action = service.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.put("/actions/{action_id}", response_model=ActionLogResponse)
def update_action(action_id: int, payload: ActionLogUpdate, db: Session = Depends(get_db)):
    """Update an action log entry"""
    service = ActionsLogService(db)
    action = service.update_action(action_id, payload.model_dump(exclude_unset=True))
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.get("/analytics", response_model=ActionsAnalytics)
def get_analytics(db: Session = Depends(get_db)):
    """Get actions analytics"""
    service = ActionsLogService(db)
    return service.get_analytics()


@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard data for actions"""
    service = ActionsLogService(db)
    return service.get_dashboard_data()


@router.get("/actions/{action_id}/progress")
def get_action_progress(action_id: int, db: Session = Depends(get_db)):
    """Get progress updates for an action"""
    service = ActionsLogService(db)
    action = service.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # TODO: Implement progress tracking
    return {"message": "Progress tracking not yet implemented"}


@router.post("/actions/{action_id}/progress")
def add_progress_update(action_id: int, db: Session = Depends(get_db)):
    """Add a progress update to an action"""
    service = ActionsLogService(db)
    action = service.get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # TODO: Implement progress update
    return {"message": "Progress update not yet implemented"}


@router.get("/overdue")
def get_overdue_actions(db: Session = Depends(get_db)):
    """Get overdue actions"""
    service = ActionsLogService(db)
    # TODO: Implement overdue actions filtering
    return {"message": "Overdue actions not yet implemented"}


@router.get("/critical")
def get_critical_actions(db: Session = Depends(get_db)):
    """Get critical priority actions"""
    service = ActionsLogService(db)
    actions = service.list_actions(priority=ActionPriority.CRITICAL, limit=50)
    return actions


@router.get("/recent")
def get_recent_actions(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get recent actions"""
    service = ActionsLogService(db)
    actions = service.list_actions(limit=limit)
    return actions


@router.get("/by-source/{source}")
def get_actions_by_source(
    source: ActionSource,
    source_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get actions by source type and optionally by source ID"""
    service = ActionsLogService(db)
    actions = service.list_actions(source=source, limit=100)
    
    if source_id:
        actions = [action for action in actions if hasattr(action, 'source_id') and action.source_id == source_id]
    
    return actions


@router.get("/management-review/{review_id}")
def get_management_review_actions(review_id: int, db: Session = Depends(get_db)):
    """Get all actions linked to a specific management review"""
    service = ActionsLogService(db)
    actions = service.list_actions(source=ActionSource.MANAGEMENT_REVIEW, limit=100)
    
    # Filter by review ID using tags or source_id
    review_actions = []
    for action in actions:
        # Check if action is linked to this review through tags
        if hasattr(action, 'tags') and action.tags and action.tags.get('review_id') == review_id:
            review_actions.append(action)
        # Also check source_id if it matches a review action
        elif hasattr(action, 'source_id') and action.source_id:
            # We'd need to check if the source_id corresponds to a review action from this review
            # For now, we'll rely on tags
            pass
    
    return review_actions
