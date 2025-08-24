# -*- coding: utf-8 -*-
"""
Actions Log System Schemas
Phase 3: Pydantic schemas for action tracking and management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ActionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    OVERDUE = "overdue"


class ActionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class ActionSource(str, Enum):
    INTERESTED_PARTY = "interested_party"
    SWOT_ANALYSIS = "swot_analysis"
    PESTEL_ANALYSIS = "pestel_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    AUDIT_FINDING = "audit_finding"
    NON_CONFORMANCE = "non_conformance"
    MANAGEMENT_REVIEW = "management_review"
    COMPLAINT = "complaint"
    REGULATORY = "regulatory"
    STRATEGIC_PLANNING = "strategic_planning"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"


# Base schemas
class ActionLogBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    action_source: ActionSource
    source_id: Optional[int] = None
    priority: ActionPriority = ActionPriority.MEDIUM
    assigned_to: Optional[int] = None
    department_id: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    tags: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ActionLogCreate(ActionLogBase):
    assigned_by: int = Field(..., description="User ID who created the action")


class ActionLogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[ActionStatus] = None
    priority: Optional[ActionPriority] = None
    assigned_to: Optional[int] = None
    department_id: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    progress_percent: Optional[float] = Field(None, ge=0, le=100)
    actual_hours: Optional[float] = Field(None, ge=0)
    tags: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ActionLogResponse(ActionLogBase):
    id: int
    status: ActionStatus
    assigned_by: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: float = 0.0
    actual_hours: Optional[float] = None
    attachments: Optional[Dict[str, Any]] = None
    assigned_user_name: Optional[str] = None
    created_by_name: Optional[str] = None
    department_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ActionsAnalytics(BaseModel):
    total_actions: int
    pending_actions: int
    in_progress_actions: int
    completed_actions: int
    overdue_actions: int
    critical_actions: int
    high_priority_actions: int
    average_completion_time: Optional[float] = None
    completion_rate: float
    source_breakdown: Dict[str, int]
    priority_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
    department_breakdown: Dict[str, int]
    
    class Config:
        from_attributes = True


# Interested Parties Schemas
class InterestedPartyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    description: Optional[str] = None
    satisfaction_level: Optional[int] = Field(None, ge=1, le=10)
    is_active: bool = True


class InterestedPartyCreate(InterestedPartyBase):
    pass


class InterestedPartyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    description: Optional[str] = None
    satisfaction_level: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class InterestedPartyResponse(InterestedPartyBase):
    id: int
    last_assessment_date: Optional[datetime] = None
    next_assessment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
