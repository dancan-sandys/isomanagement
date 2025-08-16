from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class PRPCategory(str, Enum):
    # ISO 22002-1:2025 Required Categories
    FACILITY_EQUIPMENT_DESIGN = "facility_equipment_design"
    FACILITY_LAYOUT = "facility_layout"
    PRODUCTION_EQUIPMENT = "production_equipment"
    CLEANING_SANITATION = "cleaning_sanitation"
    PEST_CONTROL = "pest_control"
    PERSONNEL_HYGIENE = "personnel_hygiene"
    WASTE_MANAGEMENT = "waste_management"
    STORAGE_TRANSPORTATION = "storage_transportation"
    SUPPLIER_CONTROL = "supplier_control"
    PRODUCT_INFORMATION_CONSUMER_AWARENESS = "product_information_consumer_awareness"
    FOOD_DEFENSE_BIOVIGILANCE = "food_defense_biovigilance"
    WATER_QUALITY = "water_quality"
    AIR_QUALITY = "air_quality"
    EQUIPMENT_CALIBRATION = "equipment_calibration"
    MAINTENANCE = "maintenance"
    PERSONNEL_TRAINING = "personnel_training"
    RECALL_PROCEDURES = "recall_procedures"
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
    UNDER_REVIEW = "under_review"


class ChecklistStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    FAILED = "failed"


class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class CorrectiveActionStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    CLOSED = "closed"
    ESCALATED = "escalated"


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
    objective: str = Field(..., min_length=1)  # Required per ISO
    scope: str = Field(..., min_length=1)      # Required per ISO
    responsible_department: str = Field(..., min_length=1, max_length=100)
    responsible_person: int = Field(..., gt=0)
    frequency: PRPFrequency
    frequency_details: Optional[str] = None
    sop_reference: str = Field(..., min_length=1, max_length=100)  # Required per ISO
    forms_required: Optional[str] = None
    records_required: Optional[str] = None
    training_requirements: Optional[str] = None
    monitoring_frequency: Optional[str] = None
    verification_frequency: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    trend_analysis_required: bool = False
    corrective_action_procedure: Optional[str] = None
    escalation_procedure: Optional[str] = None
    preventive_action_procedure: Optional[str] = None

    @validator('program_code')
    def validate_program_code(cls, v):
        if not v.isalnum() and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Program code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()


class PRPProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[PRPCategory] = None
    objective: Optional[str] = Field(None, min_length=1)
    scope: Optional[str] = Field(None, min_length=1)
    responsible_department: Optional[str] = Field(None, min_length=1, max_length=100)
    responsible_person: Optional[int] = Field(None, gt=0)
    frequency: Optional[PRPFrequency] = None
    frequency_details: Optional[str] = None
    sop_reference: Optional[str] = Field(None, min_length=1, max_length=100)
    forms_required: Optional[str] = None
    records_required: Optional[str] = None
    training_requirements: Optional[str] = None
    monitoring_frequency: Optional[str] = None
    verification_frequency: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    trend_analysis_required: Optional[bool] = None
    corrective_action_procedure: Optional[str] = None
    escalation_procedure: Optional[str] = None
    preventive_action_procedure: Optional[str] = None


class PRPProgramResponse(BaseModel):
    id: int
    program_code: str
    name: str
    description: Optional[str] = None
    category: PRPCategory
    status: PRPStatus
    objective: str
    scope: str
    responsible_department: str
    responsible_person: int
    risk_assessment_required: bool
    risk_level: Optional[RiskLevel] = None
    frequency: PRPFrequency
    frequency_details: Optional[str] = None
    next_due_date: Optional[datetime] = None
    sop_reference: str
    forms_required: Optional[str] = None
    records_required: Optional[str] = None
    training_requirements: Optional[str] = None
    monitoring_frequency: Optional[str] = None
    verification_frequency: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    trend_analysis_required: bool
    checklist_count: int
    overdue_count: int
    risk_assessment_count: int
    corrective_action_count: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Risk Assessment Schemas
class RiskMatrixCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    likelihood_levels: List[str] = Field(..., min_items=3, max_items=5)
    severity_levels: List[str] = Field(..., min_items=3, max_items=5)
    risk_levels: Dict[str, str] = Field(..., description="Matrix mapping likelihood x severity to risk levels")


class RiskAssessmentCreate(BaseModel):
    assessment_code: str = Field(..., min_length=1, max_length=50)
    hazard_identified: str = Field(..., min_length=1)
    hazard_description: Optional[str] = None
    likelihood_level: str = Field(..., min_length=1, max_length=50)
    severity_level: str = Field(..., min_length=1, max_length=50)
    existing_controls: Optional[str] = None
    additional_controls_required: Optional[str] = None
    control_effectiveness: Optional[str] = None


class RiskControlCreate(BaseModel):
    control_code: str = Field(..., min_length=1, max_length=50)
    control_type: str = Field(..., min_length=1, max_length=50)
    control_description: str = Field(..., min_length=1)
    control_procedure: Optional[str] = None
    responsible_person: Optional[int] = Field(None, gt=0)
    implementation_date: Optional[datetime] = None
    frequency: Optional[PRPFrequency] = None
    effectiveness_measure: Optional[str] = None
    effectiveness_threshold: Optional[str] = None


# Corrective Action Schemas
class CorrectiveActionCreate(BaseModel):
    action_code: str = Field(..., min_length=1, max_length=50)
    source_type: str = Field(..., min_length=1, max_length=50)
    source_id: int = Field(..., gt=0)
    checklist_id: Optional[int] = Field(None, gt=0)
    non_conformance_description: str = Field(..., min_length=1)
    non_conformance_date: datetime
    severity: str = Field(..., min_length=1, max_length=50)
    immediate_cause: Optional[str] = None
    root_cause_analysis: Optional[str] = None
    root_cause_category: Optional[str] = None
    action_description: str = Field(..., min_length=1)
    action_type: str = Field(..., min_length=1, max_length=50)
    responsible_person: int = Field(..., gt=0)
    assigned_to: int = Field(..., gt=0)
    target_completion_date: datetime
    effectiveness_criteria: Optional[str] = None


class PreventiveActionCreate(BaseModel):
    action_code: str = Field(..., min_length=1, max_length=50)
    trigger_type: str = Field(..., min_length=1, max_length=50)
    trigger_description: str = Field(..., min_length=1)
    action_description: str = Field(..., min_length=1)
    objective: str = Field(..., min_length=1)
    responsible_person: int = Field(..., gt=0)
    assigned_to: int = Field(..., gt=0)
    implementation_plan: Optional[str] = None
    resources_required: Optional[str] = None
    budget_estimate: Optional[float] = Field(None, ge=0)
    planned_start_date: Optional[datetime] = None
    planned_completion_date: Optional[datetime] = None
    success_criteria: Optional[str] = None


# Checklist Schemas
class ChecklistCreate(BaseModel):
    checklist_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: datetime
    due_date: datetime
    assigned_to: int = Field(..., gt=0)

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'scheduled_date' in values and v <= values['scheduled_date']:
            raise ValueError('Due date must be after scheduled date')
        return v


class ChecklistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = Field(None, gt=0)
    general_comments: Optional[str] = None


class ChecklistItemCreate(BaseModel):
    item_number: int = Field(..., gt=0)
    question: str = Field(..., min_length=1)
    description: Optional[str] = None
    response_type: ResponseType
    response_options: Optional[str] = None
    expected_response: Optional[str] = None
    is_critical: bool = False
    points: int = Field(1, ge=1, le=10)


class ChecklistCompletion(BaseModel):
    items: List[Dict[str, Any]] = Field(..., min_items=1)
    general_comments: Optional[str] = None
    corrective_actions_required: bool = False
    corrective_actions: Optional[str] = None
    signature: Optional[str] = None  # Base64 encoded signature


class NonConformanceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    severity: str = Field(..., min_length=1, max_length=50)
    checklist_id: int = Field(..., gt=0)
    failed_items: List[int] = Field(..., min_items=1)


class ReminderCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    checklist_id: int = Field(..., gt=0)
    reminder_date: datetime
    message: str = Field(..., min_length=1)


class ScheduleCreate(BaseModel):
    program_id: int = Field(..., gt=0)
    schedule_type: str = Field(..., min_length=1, max_length=50)
    frequency: PRPFrequency
    start_date: datetime
    end_date: Optional[datetime] = None
    next_due_date: datetime
    preferred_time_start: Optional[str] = None
    preferred_time_end: Optional[str] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    default_assignee: Optional[int] = Field(None, gt=0)
    reminder_days_before: int = Field(1, ge=0, le=30)
    escalation_days_after: int = Field(1, ge=0, le=30)


class PRPReportRequest(BaseModel):
    program_id: Optional[int] = Field(None, gt=0)
    category: Optional[PRPCategory] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    format: str = Field("pdf", pattern="^(pdf|xlsx|json)$")
    include_risk_assessments: bool = True
    include_corrective_actions: bool = True
    include_trends: bool = True 