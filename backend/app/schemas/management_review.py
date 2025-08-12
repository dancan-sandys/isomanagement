from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ManagementReviewStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReviewAgendaItemCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    discussion: Optional[str] = None
    decision: Optional[str] = None
    order_index: Optional[int] = None


class ReviewAgendaItemResponse(BaseModel):
    id: int
    topic: str
    discussion: Optional[str] = None
    decision: Optional[str] = None
    order_index: Optional[int] = None

    model_config = {"from_attributes": True}


class ReviewActionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class ReviewActionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ManagementReviewCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    review_date: Optional[datetime] = None
    attendees: Optional[str] = None
    inputs: Optional[str] = None
    status: Optional[ManagementReviewStatus] = ManagementReviewStatus.PLANNED
    next_review_date: Optional[datetime] = None
    agenda: Optional[List[ReviewAgendaItemCreate]] = None


class ManagementReviewUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    review_date: Optional[datetime] = None
    attendees: Optional[str] = None
    inputs: Optional[str] = None
    outputs: Optional[str] = None
    status: Optional[ManagementReviewStatus] = None
    next_review_date: Optional[datetime] = None


class ManagementReviewResponse(BaseModel):
    id: int
    title: str
    review_date: Optional[datetime]
    attendees: Optional[str]
    inputs: Optional[str]
    outputs: Optional[str]
    status: ManagementReviewStatus
    next_review_date: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    agenda: List[ReviewAgendaItemResponse] = []
    actions: List[ReviewActionResponse] = []

    model_config = {"from_attributes": True}


