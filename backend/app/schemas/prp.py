from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class PRPCategory(str, Enum):
    CLEANING_SANITATION = "cleaning_sanitation"
    PEST_CONTROL = "pest_control"
    STAFF_HYGIENE = "staff_hygiene"
    WASTE_MANAGEMENT = "waste_management"
    EQUIPMENT_CALIBRATION = "equipment_calibration"
    MAINTENANCE = "maintenance"
    PERSONNEL_TRAINING = "personnel_training"
    SUPPLIER_CONTROL = "supplier_control"
    RECALL_PROCEDURES = "recall_procedures"
    WATER_QUALITY = "water_quality"
    AIR_QUALITY = "air_quality"
    TRANSPORTATION = "transportation"


class PRPFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    AS_NEEDED = "as_needed"


class PRPStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ChecklistStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    FAILED = "failed"


class ResponseType(str, Enum):
    YES_NO = "yes_no"
    NUMERIC = "numeric"
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"


# PRP Program Schemas
class PRPProgramCreate(BaseModel):
    program_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: PRPCategory
    objective: Optional[str] = None
    scope: Optional[str] = None
    responsible_department: Optional[str] = Field(None, max_length=100)
    responsible_person: Optional[int] = None
    frequency: PRPFrequency
    frequency_details: Optional[str] = None
    sop_reference: Optional[str] = Field(None, max_length=100)
    forms_required: Optional[str] = None


class PRPProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[PRPCategory] = None
    status: Optional[PRPStatus] = None
    objective: Optional[str] = None
    scope: Optional[str] = None
    responsible_department: Optional[str] = Field(None, max_length=100)
    responsible_person: Optional[int] = None
    frequency: Optional[PRPFrequency] = None
    frequency_details: Optional[str] = None
    sop_reference: Optional[str] = Field(None, max_length=100)
    forms_required: Optional[str] = None


class PRPProgramResponse(BaseModel):
    id: int
    program_code: str
    name: str
    description: Optional[str] = None
    category: PRPCategory
    status: PRPStatus
    objective: Optional[str] = None
    scope: Optional[str] = None
    responsible_department: Optional[str] = None
    responsible_person: Optional[int] = None
    frequency: PRPFrequency
    frequency_details: Optional[str] = None
    next_due_date: Optional[datetime] = None
    sop_reference: Optional[str] = None
    forms_required: Optional[str] = None
    checklist_count: int
    overdue_count: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Checklist Schemas
class ChecklistCreate(BaseModel):
    checklist_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: datetime
    due_date: datetime
    assigned_to: int


class ChecklistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ChecklistStatus] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    general_comments: Optional[str] = None
    corrective_actions_required: Optional[bool] = None
    corrective_actions: Optional[str] = None


class ChecklistResponse(BaseModel):
    id: int
    checklist_code: str
    name: str
    description: Optional[str] = None
    status: ChecklistStatus
    scheduled_date: datetime
    due_date: datetime
    completed_date: Optional[datetime] = None
    assigned_to: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    total_items: int
    passed_items: int
    failed_items: int
    not_applicable_items: int
    compliance_percentage: float
    corrective_actions_required: bool
    corrective_actions: Optional[str] = None
    general_comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Checklist Item Schemas
class ChecklistItemCreate(BaseModel):
    item_number: int = Field(..., ge=1)
    question: str = Field(..., min_length=1)
    description: Optional[str] = None
    response_type: ResponseType
    response_options: Optional[str] = None  # JSON string for multiple choice
    expected_response: Optional[str] = None
    is_critical: bool = False
    points: int = Field(1, ge=1)


class ChecklistItemUpdate(BaseModel):
    question: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    response_type: Optional[ResponseType] = None
    response_options: Optional[str] = None
    expected_response: Optional[str] = None
    is_critical: Optional[bool] = None
    points: Optional[int] = Field(None, ge=1)


class ChecklistItemResponse(BaseModel):
    id: int
    item_number: int
    question: str
    description: Optional[str] = None
    response_type: ResponseType
    response_options: Optional[str] = None
    expected_response: Optional[str] = None
    is_critical: bool
    points: int
    response: Optional[str] = None
    response_value: Optional[float] = None
    is_compliant: Optional[bool] = None
    comments: Optional[str] = None
    evidence_files: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Checklist Completion Schemas
class ChecklistItemCompletion(BaseModel):
    item_id: int
    response: str
    response_value: Optional[float] = None
    is_compliant: bool
    comments: Optional[str] = None
    evidence_files: Optional[str] = None


class ChecklistCompletion(BaseModel):
    checklist_id: int
    items: List[ChecklistItemCompletion]
    general_comments: Optional[str] = None
    corrective_actions_required: bool = False
    corrective_actions: Optional[str] = None
    signature: Optional[str] = None  # Base64 encoded signature
    completion_notes: Optional[str] = None


# Schedule Schemas
class ScheduleCreate(BaseModel):
    schedule_type: str = Field(..., pattern="^(recurring|one_time)$")
    frequency: PRPFrequency
    start_date: datetime
    end_date: Optional[datetime] = None
    preferred_time_start: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    preferred_time_end: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    default_assignee: Optional[int] = None
    reminder_days_before: int = Field(1, ge=0)
    escalation_days_after: int = Field(1, ge=0)


class ScheduleResponse(BaseModel):
    id: int
    schedule_type: str
    frequency: PRPFrequency
    start_date: datetime
    end_date: Optional[datetime] = None
    next_due_date: datetime
    preferred_time_start: Optional[str] = None
    preferred_time_end: Optional[str] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    default_assignee: Optional[int] = None
    reminder_days_before: int
    escalation_days_after: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Reminder and Escalation Schemas
class ReminderCreate(BaseModel):
    checklist_id: int
    reminder_type: str = Field(..., pattern="^(due_soon|overdue|escalation)$")
    message: str = Field(..., min_length=1)
    send_to: List[int] = Field(..., min_items=1)
    send_at: datetime


class ReminderResponse(BaseModel):
    id: int
    checklist_id: int
    reminder_type: str
    message: str
    send_to: List[int]
    send_at: datetime
    sent_at: Optional[datetime] = None
    is_sent: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# Non-conformance Schemas
class NonConformanceCreate(BaseModel):
    checklist_id: int
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    description: str = Field(..., min_length=1)
    root_cause: Optional[str] = None
    corrective_action: str = Field(..., min_length=1)
    assigned_to: int
    due_date: datetime
    evidence_files: Optional[str] = None


class NonConformanceResponse(BaseModel):
    id: int
    checklist_id: int
    severity: str
    description: str
    root_cause: Optional[str] = None
    corrective_action: str
    assigned_to: int
    due_date: datetime
    status: str
    evidence_files: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Dashboard Schemas
class PRPDashboardStats(BaseModel):
    total_programs: int
    active_programs: int
    total_checklists: int
    pending_checklists: int
    overdue_checklists: int
    completed_this_month: int
    compliance_rate: float
    recent_checklists: List[Dict[str, Any]]
    upcoming_checklists: List[Dict[str, Any]]
    non_conformances: List[Dict[str, Any]]


# Report Schemas
class PRPReportRequest(BaseModel):
    program_id: Optional[int] = None
    category: Optional[PRPCategory] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_non_conformances: bool = True
    include_evidence: bool = True
    format: str = Field("pdf", pattern="^(pdf|excel|html)$")


class PRPReportResponse(BaseModel):
    report_id: str
    report_url: str
    generated_at: datetime
    file_size: Optional[int] = None


# File Upload Schemas
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    uploaded_at: datetime


# Signature Schemas
class SignatureData(BaseModel):
    signature_data: str  # Base64 encoded signature
    signed_by: int
    signed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SignatureResponse(BaseModel):
    id: int
    checklist_id: int
    signature_data: str
    signed_by: str
    signed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    model_config = {"from_attributes": True} 