from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NonConformanceSource(str, Enum):
    PRP = "prp"
    AUDIT = "audit"
    COMPLAINT = "complaint"
    PRODUCTION_DEVIATION = "production_deviation"
    SUPPLIER = "supplier"
    HACCP = "haccp"
    DOCUMENT = "document"
    OTHER = "other"


class NonConformanceStatus(str, Enum):
    OPEN = "open"
    UNDER_INVESTIGATION = "under_investigation"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    CAPA_ASSIGNED = "capa_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"


class CAPAStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"
    OVERDUE = "overdue"


class RootCauseMethod(str, Enum):
    FIVE_WHYS = "five_whys"
    ISHIKAWA = "ishikawa"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    OTHER = "other"


# Base schemas
class NonConformanceBase(BaseModel):
    title: str = Field(..., description="Title of the non-conformance")
    description: str = Field(..., description="Detailed description of the non-conformance")
    source: NonConformanceSource
    batch_reference: Optional[str] = None
    product_reference: Optional[str] = None
    process_reference: Optional[str] = None
    location: Optional[str] = None
    severity: str = Field(default="medium", description="low, medium, high, critical")
    impact_area: Optional[str] = None
    category: Optional[str] = None
    target_resolution_date: Optional[datetime] = None


class NonConformanceCreate(NonConformanceBase):
    pass


class NonConformanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[NonConformanceSource] = None
    batch_reference: Optional[str] = None
    product_reference: Optional[str] = None
    process_reference: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    impact_area: Optional[str] = None
    category: Optional[str] = None
    status: Optional[NonConformanceStatus] = None
    target_resolution_date: Optional[datetime] = None
    actual_resolution_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    assigned_date: Optional[datetime] = None
    evidence_files: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class NonConformanceResponse(NonConformanceBase):
    id: int
    nc_number: str
    status: NonConformanceStatus
    reported_date: datetime
    actual_resolution_date: Optional[datetime] = None
    reported_by: int
    assigned_to: Optional[int] = None
    assigned_date: Optional[datetime] = None
    evidence_files: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Root Cause Analysis schemas
class RootCauseAnalysisBase(BaseModel):
    method: RootCauseMethod
    analysis_date: datetime
    immediate_cause: Optional[str] = None
    underlying_cause: Optional[str] = None
    root_cause: Optional[str] = None
    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None
    fishbone_categories: Optional[Dict[str, Any]] = None
    fishbone_diagram_data: Optional[Dict[str, Any]] = None
    contributing_factors: Optional[List[str]] = None
    system_failures: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    preventive_measures: Optional[List[str]] = None


class RootCauseAnalysisCreate(RootCauseAnalysisBase):
    non_conformance_id: int


class RootCauseAnalysisUpdate(BaseModel):
    method: Optional[RootCauseMethod] = None
    analysis_date: Optional[datetime] = None
    immediate_cause: Optional[str] = None
    underlying_cause: Optional[str] = None
    root_cause: Optional[str] = None
    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None
    fishbone_categories: Optional[Dict[str, Any]] = None
    fishbone_diagram_data: Optional[Dict[str, Any]] = None
    contributing_factors: Optional[List[str]] = None
    system_failures: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    preventive_measures: Optional[List[str]] = None


class RootCauseAnalysisResponse(RootCauseAnalysisBase):
    id: int
    non_conformance_id: int
    conducted_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# CAPA Action schemas
class CAPAActionBase(BaseModel):
    title: str = Field(..., description="Title of the CAPA action")
    description: str = Field(..., description="Detailed description of the CAPA action")
    action_type: Optional[str] = None  # corrective, preventive, both
    responsible_person: int
    target_completion_date: datetime
    required_resources: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    implementation_plan: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    deliverables: Optional[List[str]] = None
    effectiveness_criteria: Optional[List[str]] = None


class CAPAActionCreate(CAPAActionBase):
    non_conformance_id: int


class CAPAActionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None
    responsible_person: Optional[int] = None
    target_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    status: Optional[CAPAStatus] = None
    progress_percentage: Optional[float] = None
    required_resources: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    implementation_plan: Optional[str] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    deliverables: Optional[List[str]] = None
    effectiveness_criteria: Optional[List[str]] = None
    effectiveness_measured: Optional[bool] = None
    effectiveness_score: Optional[float] = None


class CAPAActionResponse(CAPAActionBase):
    id: int
    capa_number: str
    non_conformance_id: int
    assigned_date: datetime
    actual_completion_date: Optional[datetime] = None
    status: CAPAStatus
    progress_percentage: float
    actual_cost: Optional[float] = None
    effectiveness_measured: bool
    effectiveness_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    created_by: int

    class Config:
        from_attributes = True


# CAPA Verification schemas
class CAPAVerificationBase(BaseModel):
    verification_date: datetime
    verification_criteria: Optional[List[str]] = None
    verification_method: Optional[str] = None
    verification_evidence: Optional[List[str]] = None
    verification_result: Optional[str] = None  # passed, failed, conditional
    effectiveness_score: Optional[float] = None
    comments: Optional[str] = None
    follow_up_required: bool = False
    follow_up_actions: Optional[List[str]] = None
    next_verification_date: Optional[datetime] = None


class CAPAVerificationCreate(CAPAVerificationBase):
    non_conformance_id: int
    capa_action_id: int


class CAPAVerificationUpdate(BaseModel):
    verification_date: Optional[datetime] = None
    verification_criteria: Optional[List[str]] = None
    verification_method: Optional[str] = None
    verification_evidence: Optional[List[str]] = None
    verification_result: Optional[str] = None
    effectiveness_score: Optional[float] = None
    comments: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_actions: Optional[List[str]] = None
    next_verification_date: Optional[datetime] = None


class CAPAVerificationResponse(CAPAVerificationBase):
    id: int
    non_conformance_id: int
    capa_action_id: int
    verified_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Attachment schemas
class NonConformanceAttachmentBase(BaseModel):
    file_name: str
    attachment_type: Optional[str] = None  # evidence, document, photo, video, etc.
    description: Optional[str] = None


class NonConformanceAttachmentCreate(NonConformanceAttachmentBase):
    non_conformance_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None


class NonConformanceAttachmentUpdate(BaseModel):
    file_name: Optional[str] = None
    attachment_type: Optional[str] = None
    description: Optional[str] = None


class NonConformanceAttachmentResponse(NonConformanceAttachmentBase):
    id: int
    non_conformance_id: int
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    original_filename: Optional[str] = None
    uploaded_by: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Filter schemas
class NonConformanceFilter(BaseModel):
    search: Optional[str] = None
    source: Optional[NonConformanceSource] = None
    status: Optional[NonConformanceStatus] = None
    severity: Optional[str] = None
    impact_area: Optional[str] = None
    reported_by: Optional[int] = None
    assigned_to: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


class CAPAFilter(BaseModel):
    non_conformance_id: Optional[int] = None
    status: Optional[CAPAStatus] = None
    responsible_person: Optional[int] = None
    action_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20


# Dashboard schemas
class NonConformanceDashboardStats(BaseModel):
    total_non_conformances: int
    open_non_conformances: int
    overdue_capas: int
    non_conformances_by_source: List[Dict[str, Any]]
    non_conformances_by_status: List[Dict[str, Any]]
    non_conformances_by_severity: List[Dict[str, Any]]
    recent_non_conformances: List[Dict[str, Any]]
    capa_completion_rate: float
    average_resolution_time: float


# Response schemas
class NonConformanceListResponse(BaseModel):
    items: List[NonConformanceResponse]
    total: int
    page: int
    size: int
    pages: int


class CAPAListResponse(BaseModel):
    items: List[CAPAActionResponse]
    total: int
    page: int
    size: int
    pages: int


class RootCauseAnalysisListResponse(BaseModel):
    items: List[RootCauseAnalysisResponse]
    total: int
    page: int
    size: int
    pages: int


class VerificationListResponse(BaseModel):
    items: List[CAPAVerificationResponse]
    total: int
    page: int
    size: int
    pages: int


class AttachmentListResponse(BaseModel):
    items: List[NonConformanceAttachmentResponse]
    total: int
    page: int
    size: int
    pages: int


# Bulk operations
class BulkNonConformanceAction(BaseModel):
    non_conformance_ids: List[int]
    action: str  # assign, update_status, close


class BulkCAPAAction(BaseModel):
    capa_ids: List[int]
    action: str  # update_status, assign, complete


# Root cause analysis tools
class FiveWhysAnalysis(BaseModel):
    problem: str
    why_1: str
    why_2: str
    why_3: str
    why_4: str
    why_5: str
    root_cause: str


class IshikawaAnalysis(BaseModel):
    problem: str
    categories: Dict[str, List[str]]  # e.g., {"People": ["training", "experience"], "Process": ["procedure", "equipment"]}
    diagram_data: Dict[str, Any]


class RootCauseAnalysisRequest(BaseModel):
    non_conformance_id: int
    method: RootCauseMethod
    analysis_data: Dict[str, Any]  # Flexible data structure for different methods 