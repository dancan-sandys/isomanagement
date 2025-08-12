from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.complaint import ComplaintStatus, ComplaintClassification, CommunicationChannel


class ComplaintBase(BaseModel):
    customer_name: str
    customer_contact: Optional[str] = None
    description: str
    classification: ComplaintClassification = ComplaintClassification.OTHER
    severity: Optional[str] = Field(default="medium")
    batch_id: Optional[int] = None
    product_id: Optional[int] = None
    attachments: Optional[list] = None


class ComplaintCreate(ComplaintBase):
    complaint_date: Optional[datetime] = None
    received_via: Optional[str] = None


class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    classification: Optional[ComplaintClassification] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    batch_id: Optional[int] = None
    product_id: Optional[int] = None
    attachments: Optional[list] = None


class ComplaintResponse(ComplaintBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    complaint_number: str
    complaint_date: datetime
    received_via: Optional[str] = None
    status: ComplaintStatus
    non_conformance_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class CommunicationCreate(BaseModel):
    channel: CommunicationChannel
    sender: Optional[str] = None
    recipient: Optional[str] = None
    message: str


class CommunicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    complaint_id: int
    communication_date: datetime
    channel: CommunicationChannel
    sender: Optional[str] = None
    recipient: Optional[str] = None
    message: str
    created_by: int


class InvestigationCreate(BaseModel):
    investigator_id: Optional[int] = None
    summary: Optional[str] = None


class InvestigationUpdate(BaseModel):
    investigator_id: Optional[int] = None
    root_cause_analysis_id: Optional[int] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    complaint_id: int
    start_date: datetime
    investigator_id: Optional[int] = None
    root_cause_analysis_id: Optional[int] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None


class ComplaintListResponse(BaseModel):
    items: List[ComplaintResponse]
    total: int
    page: int
    size: int
    pages: int


class ComplaintTrendResponse(BaseModel):
    by_classification: List[dict]
    by_severity: List[dict]
    monthly_counts: List[dict]


